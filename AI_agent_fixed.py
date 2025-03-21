#!C:\Users\Tyler\AppData\Local\Microsoft\WindowsApps\python.exe

import os
import openai
import json
import subprocess
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CopilotAgent:
    def __init__(self, tasks_file: str = "tasks.json", history_file: str = "history.json"):
        self.tasks_file = tasks_file
        self.history_file = history_file
        self.tasks = self._load_json(tasks_file, {"pending": [], "approved": [], "completed": [], "failed": []})
        self.history = self._load_json(history_file, {"commands": []})
        
    def _load_json(self, file_path: str, default_value: Dict) -> Dict:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default_value
        
    def _save_json(self, data: Dict, file_path: str):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def save_state(self):
        self._save_json(self.tasks, self.tasks_file)
        self._save_json(self.history, self.history_file)
    
    def generate_task(self, description: str) -> Dict:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Generate a shell command for the following task."},
                    {"role": "user", "content": description}
                ]
            )
            suggested_command = response['choices'][0]['message']['content'].strip()
            
            task_id = len(self.tasks["pending"]) + len(self.tasks["approved"]) +                      len(self.tasks["completed"]) + len(self.tasks["failed"]) + 1
                     
            task = {
                "id": task_id,
                "description": description,
                "command": suggested_command,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "error": None,
                "result": None
            }
            
            self.tasks["pending"].append(task)
            self.save_state()
            return task
            
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate task due to OpenAI API error: {e}")
    
    def generate_error_fixes(self, task_id: int) -> List[str]:
        task = self._find_task_in_status(task_id, "failed")
        if not task:
            raise ValueError(f"Failed task with ID {task_id} not found")
            
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Suggest a fix for the following failed shell command."},
                    {"role": "user", "content": f"Command: {task['command']}
Error: {task['error']}"}
                ]
            )
            return [response['choices'][0]['message']['content'].strip()]
            
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            return []
    
    def _find_task_in_status(self, task_id: int, status: str) -> Optional[Dict]:
        if status not in self.tasks:
            return None
        for task in self.tasks[status]:
            if task["id"] == task_id:
                return task
        return None

def main():
    agent = CopilotAgent()
    
    while True:
        print("\n=== OpenAI Task Agent ===")
        print("1. Create new task")
        print("2. View pending tasks")
        print("3. Approve tasks")
        print("4. Execute approved tasks")
        print("5. View failed tasks")
        print("6. Generate fix for failed task")
        print("7. Exit")
        
        choice = input("\nSelect an option: ")
        
        try:
            if choice == "1":
                description = input("Enter task description: ")
                task = agent.generate_task(description)
                print(f"\nTask Created: {task['command']}")
                
            elif choice == "2":
                print(agent.tasks["pending"])
                
            elif choice == "3":
                task_id = int(input("Enter task ID to approve: "))
                agent.approve_task(task_id)
                
            elif choice == "4":
                task_id = int(input("Enter task ID to execute: "))
                print(agent.execute_task(task_id))
                
            elif choice == "5":
                print(agent.tasks["failed"])
                
            elif choice == "6":
                task_id = int(input("Enter failed task ID: "))
                print(agent.generate_error_fixes(task_id))
                
            elif choice == "7":
                break
                
        except Exception as e:
            print(f"Error: {e}")
            logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
