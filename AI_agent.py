#!/usr/bin/env python3
import os
import json
import subprocess
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='copilot_agent.log'
)

class CopilotAgent:
    def __init__(self, tasks_file: str = "tasks.json", history_file: str = "history.json"):
        self.tasks_file = tasks_file
        self.history_file = history_file
        self.tasks = self._load_json(tasks_file, {"pending": [], "approved": [], "completed": [], "failed": []})
        self.history = self._load_json(history_file, {"commands": []})
        
    def _load_json(self, file_path: str, default_value: Dict) -> Dict:
        """Load JSON from file or return default if file doesn't exist"""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default_value
        
    def _save_json(self, data: Dict, file_path: str):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def save_state(self):
        """Save current state to files"""
        self._save_json(self.tasks, self.tasks_file)
        self._save_json(self.history, self.history_file)
            
    def generate_task(self, description: str) -> Dict:
        """Generate a task using GitHub Copilot CLI"""
        try:
            # Use gh copilot suggest to generate a shell command
            result = subprocess.run(
                ["gh", "copilot", "suggest", "-t", "shell", description],
                capture_output=True,
                text=True,
                check=False  # Allow non-zero exit codes
            )
            logging.debug(f"Subprocess stdout: {result.stdout}")
            logging.debug(f"Subprocess stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to generate task: {result.stderr}")
            
            # Extract the suggested command from the output
            lines = result.stdout.strip().split("\n")
            suggested_command = None
            for line in lines:
                if line.strip().startswith("mv") or line.strip().startswith("rm"):
                    suggested_command = line.strip()
                    break
            
            if not suggested_command:
                raise RuntimeError("No valid command was suggested by GitHub Copilot.")
            
            # Create new task
            task_id = len(self.tasks["pending"]) + len(self.tasks["approved"]) + \
                      len(self.tasks["completed"]) + len(self.tasks["failed"]) + 1
            task = {
                "id": task_id,
                "description": description,
                "command": suggested_command,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "error": None,
                "result": None
            }
            
            # Add to pending tasks
            self.tasks["pending"].append(task)
            self.save_state()
            
            return task
        
        except Exception as e:
            logging.error(f"Error generating task: {e}")
            raise
            
    def explain_task(self, task_id: int) -> str:
        """Get explanation for a task using GitHub Copilot explain"""
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
            
        try:
            # Use gh copilot explain to explain the command
            result = subprocess.run(
                ["gh", "copilot", "explain", task["command"]],
                capture_output=True, 
                text=True,
                check=True
            )
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error explaining task: {e.stderr}")
            return f"Failed to explain: {e.stderr}"
            
    def approve_task(self, task_id: int) -> Dict:
        """Move a task from pending to approved status"""
        for i, task in enumerate(self.tasks["pending"]):
            if task["id"] == task_id:
                approved_task = self.tasks["pending"].pop(i)
                approved_task["status"] = "approved"
                approved_task["approved_at"] = datetime.now().isoformat()
                self.tasks["approved"].append(approved_task)
                self.save_state()
                return approved_task
                
        raise ValueError(f"Task with ID {task_id} not found in pending tasks")
        
    def reject_task(self, task_id: int) -> Dict:
        """Remove a task from pending status"""
        for i, task in enumerate(self.tasks["pending"]):
            if task["id"] == task_id:
                rejected_task = self.tasks["pending"].pop(i)
                self.save_state()
                return rejected_task
                
        raise ValueError(f"Task with ID {task_id} not found in pending tasks")
        
    def execute_task(self, task_id: int) -> Dict:
        """Execute an approved task"""
        # Find the task
        task = None
        task_index = None
        
        for i, t in enumerate(self.tasks["approved"]):
            if t["id"] == task_id:
                task = t
                task_index = i
                break
                
        if not task:
            raise ValueError(f"Task with ID {task_id} not found in approved tasks")
            
        # Execute the command
        try:
            start_time = time.time()
            result = subprocess.run(
                task["command"], 
                shell=True,  # Use shell to execute the command
                capture_output=True, 
                text=True,
                timeout=300,  # 5 minute timeout
                check=True
            )
            execution_time = time.time() - start_time
            
            # Update task
            executed_task = self.tasks["approved"].pop(task_index)
            executed_task["status"] = "completed"
            executed_task["executed_at"] = datetime.now().isoformat()
            executed_task["execution_time"] = execution_time
            executed_task["result"] = result.stdout
            self.tasks["completed"].append(executed_task)
            
            # Add to history
            self.history["commands"].append({
                "task_id": task_id,
                "command": task["command"],
                "executed_at": executed_task["executed_at"],
                "success": True,
                "output": result.stdout
            })
            
            self.save_state()
            return executed_task
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            error_type = "Error" if isinstance(e, subprocess.CalledProcessError) else "Timeout"
            error_detail = e.stderr if isinstance(e, subprocess.CalledProcessError) else f"Command timed out after 300 seconds"
            
            # Move to failed tasks
            failed_task = self.tasks["approved"].pop(task_index)
            failed_task["status"] = "failed"
            failed_task["error_type"] = error_type
            failed_task["error"] = error_detail
            failed_task["failed_at"] = datetime.now().isoformat()
            self.tasks["failed"].append(failed_task)
            
            # Add to history
            self.history["commands"].append({
                "task_id": task_id,
                "command": task["command"],
                "executed_at": failed_task["failed_at"],
                "success": False,
                "error": error_detail
            })
            
            self.save_state()
            return failed_task
            
    def generate_error_fixes(self, task_id: int) -> List[str]:
        """Generate possible fixes for a failed task"""
        task = self._find_task_in_status(task_id, "failed")
        if not task:
            raise ValueError(f"Failed task with ID {task_id} not found")
            
        try:
            # Use Copilot to explain the error and suggest fixes
            prompt = f"Fix this command that failed with error: {task['command']} —— {task['error']}"
            
            result = subprocess.run(
                ["gh", "copilot", "suggest", "-t", "shell", prompt],
                capture_output=True, 
                text=True,
                check=True
            )
            
            # For simplicity, we'll just return the one suggested fix
            fixes = [result.stdout.strip()]
            return fixes
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error generating fixes: {e.stderr}")
            return []
            
    def retry_with_fix(self, task_id: int, fixed_command: str) -> Dict:
        """Retry a failed task with a fixed command"""
        task = self._find_task_in_status(task_id, "failed")
        if not task:
            raise ValueError(f"Failed task with ID {task_id} not found")
            
        # Create a new task based on the failed one
        new_task = {
            "id": len(self.tasks["pending"]) + len(self.tasks["approved"]) + \
                 len(self.tasks["completed"]) + len(self.tasks["failed"]) + 1,
            "description": f"Retry of task {task_id}: {task['description']}",
            "command": fixed_command,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "original_task_id": task_id,
            "error": None,
            "result": None
        }
        
        self.tasks["pending"].append(new_task)
        self.save_state()
        return new_task
        
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """Get all tasks with a specific status"""
        if status in self.tasks:
            return self.tasks[status]
        return []
        
    def _find_task(self, task_id: int) -> Optional[Dict]:
        """Find a task by ID across all statuses"""
        for status in ["pending", "approved", "completed", "failed"]:
            for task in self.tasks[status]:
                if task["id"] == task_id:
                    return task
        return None
        
    def _find_task_in_status(self, task_id: int, status: str) -> Optional[Dict]:
        """Find a task by ID in a specific status"""
        if status not in self.tasks:
            return None
            
        for task in self.tasks[status]:
            if task["id"] == task_id:
                return task
        return None

def main():
    """CLI interface for the Copilot Agent"""
    agent = CopilotAgent()
    
    while True:
        print("\n=== GitHub Copilot Task Agent ===")
        print("1. Create new task")
        print("2. View pending tasks")
        print("3. Approve/reject tasks")
        print("4. Execute approved tasks")
        print("5. View failed tasks")
        print("6. Generate fix for failed task")
        print("7. View task history")
        print("8. Exit")
        
        choice = input("\nSelect an option: ")
        
        try:
            if choice == "1":
                description = input("Enter task description in natural language: ")
                task = agent.generate_task(description)
                print(f"\nGenerated Task #{task['id']}:")
                print(f"Command: {task['command']}")
                
                explain = input("Would you like an explanation of this command? (y/n): ")
                if explain.lower() == 'y':
                    explanation = agent.explain_task(task['id'])
                    print("\nExplanation:")
                    print(explanation)
                    
            elif choice == "2":
                pending_tasks = agent.get_tasks_by_status("pending")
                if not pending_tasks:
                    print("No pending tasks.")
                else:
                    print("\nPending Tasks:")
                    for task in pending_tasks:
                        print(f"ID: {task['id']} - {task['description']}")
                        print(f"Command: {task['command']}")
                        print("---")
                        
            elif choice == "3":
                pending_tasks = agent.get_tasks_by_status("pending")
                if not pending_tasks:
                    print("No pending tasks to approve.")
                else:
                    print("\nPending Tasks:")
                    for task in pending_tasks:
                        print(f"ID: {task['id']} - {task['description']}")
                        print(f"Command: {task['command']}")
                        
                        choice = input("Approve this task? (y/n/e for explain): ")
                        if choice.lower() == 'e':
                            explanation = agent.explain_task(task['id'])
                            print("\nExplanation:")
                            print(explanation)
                            choice = input("Approve this task? (y/n): ")
                            
                        if choice.lower() == 'y':
                            agent.approve_task(task['id'])
                            print(f"Task {task['id']} approved.")
                        else:
                            agent.reject_task(task['id'])
                            print(f"Task {task['id']} rejected.")
                            
            elif choice == "4":
                approved_tasks = agent.get_tasks_by_status("approved")
                if not approved_tasks:
                    print("No approved tasks to execute.")
                else:
                    print("\nApproved Tasks:")
                    for task in approved_tasks:
                        print(f"ID: {task['id']} - {task['description']}")
                        print(f"Command: {task['command']}")
                        
                        execute = input("Execute this task? (y/n): ")
                        if execute.lower() == 'y':
                            print(f"Executing task {task['id']}...")
                            result = agent.execute_task(task['id'])
                            
                            if result['status'] == 'completed':
                                print("Task completed successfully!")
                                print("\nOutput:")
                                print(result['result'])
                            else:
                                print(f"Task failed with error: {result['error']}")
                                
            elif choice == "5":
                failed_tasks = agent.get_tasks_by_status("failed")
                if not failed_tasks:
                    print("No failed tasks.")
                else:
                    print("\nFailed Tasks:")
                    for task in failed_tasks:
                        print(f"ID: {task['id']} - {task['description']}")
                        print(f"Command: {task['command']}")
                        print(f"Error: {task['error']}")
                        print("---")
                        
            elif choice == "6":
                task_id = int(input("Enter ID of failed task: "))
                fixes = agent.generate_error_fixes(task_id)
                if not fixes:
                    print("No fixes generated.")
                else:
                    print("\nSuggested Fixes:")
                    for fix in fixes:
                        print(fix)
                    
                    retry = input("Would you like to retry with one of these fixes? (y/n): ")
                    if retry.lower() == 'y':
                        fixed_command = input("Enter the fixed command: ")
                        new_task = agent.retry_with_fix(task_id, fixed_command)
                        print(f"New Task #{new_task['id']} created for retry.")
                        
            elif choice == "7":
                print("\nTask History:")
                for entry in agent.history["commands"]:
                    print(f"Task ID: {entry['task_id']}")
                    print(f"Command: {entry['command']}")
                    print(f"Executed At: {entry['executed_at']}")
                    print(f"Success: {entry['success']}")
                    if entry['success']:
                        print(f"Output: {entry['output']}")
                    else:
                        print(f"Error: {entry['error']}")
                    print("---")
                    
            elif choice == "8":
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please select a valid option.")
                
        except Exception as e:
            print(f"An error occurred: {e}")
            logging.error(f"An error occurred: {e}")
        finally:
            print("End of try block")

if __name__ == "__main__":
    main()