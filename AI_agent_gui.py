import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Dict
from datetime import datetime
import threading

class CopilotAgentGUI:
    def __init__(self, agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("GitHub Copilot Task Agent")
        self.create_main_menu()

    def create_main_menu(self):
        """Create the main menu UI."""
        tk.Label(self.root, text="GitHub Copilot Task Agent", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="1. Create New Task", command=self.create_new_task).pack(fill="x", pady=5)
        tk.Button(self.root, text="2. View Pending Tasks", command=self.view_pending_tasks).pack(fill="x", pady=5)
        tk.Button(self.root, text="3. Approve/Reject Tasks", command=self.approve_reject_tasks).pack(fill="x", pady=5)
        tk.Button(self.root, text="4. Execute Approved Tasks", command=self.execute_approved_tasks).pack(fill="x", pady=5)
        tk.Button(self.root, text="5. View Failed Tasks", command=self.view_failed_tasks).pack(fill="x", pady=5)
        tk.Button(self.root, text="6. Generate Fix for Failed Task", command=self.generate_fix_for_failed_task).pack(fill="x", pady=5)
        tk.Button(self.root, text="7. View Task History", command=self.view_task_history).pack(fill="x", pady=5)
        tk.Button(self.root, text="8. Exit", command=self.root.quit).pack(fill="x", pady=5)

    def run_in_thread(self, target, *args):
        """Run a function in a separate thread."""
        thread = threading.Thread(target=target, args=args)
        thread.daemon = True  # Ensure the thread exits when the main program exits
        thread.start()

    def create_new_task(self):
        """Handle creating a new task."""
        description = simpledialog.askstring("Create New Task", "Enter task description in natural language:")
        if description:
            self.run_in_thread(self._create_new_task, description)

    def _create_new_task(self, description):
        try:
            task = self.agent.generate_task(description)
            messagebox.showinfo("Task Created", f"Task #{task['id']} created:\nCommand: {task['command']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create task: {e}")

    def view_pending_tasks(self):
        """Display pending tasks."""
        self.run_in_thread(self._view_pending_tasks)

    def _view_pending_tasks(self):
        pending_tasks = self.agent.get_tasks_by_status("pending")
        if not pending_tasks:
            messagebox.showinfo("Pending Tasks", "No pending tasks.")
        else:
            tasks_str = "\n".join([f"ID: {task['id']} - {task['description']}" for task in pending_tasks])
            messagebox.showinfo("Pending Tasks", tasks_str)

    def approve_reject_tasks(self):
        """Approve or reject pending tasks."""
        self.run_in_thread(self._approve_reject_tasks)

    def _approve_reject_tasks(self):
        pending_tasks = self.agent.get_tasks_by_status("pending")
        if not pending_tasks:
            messagebox.showinfo("Approve/Reject Tasks", "No pending tasks to approve or reject.")
            return

        for task in pending_tasks:
            response = messagebox.askquestion(
                "Approve/Reject Task",
                f"Task #{task['id']}:\nDescription: {task['description']}\nCommand: {task['command']}\n\nApprove this task?"
            )
            if response == "yes":
                self.agent.approve_task(task["id"])
                messagebox.showinfo("Task Approved", f"Task #{task['id']} approved.")
            else:
                self.agent.reject_task(task["id"])
                messagebox.showinfo("Task Rejected", f"Task #{task['id']} rejected.")

    def execute_approved_tasks(self):
        """Execute approved tasks."""
        self.run_in_thread(self._execute_approved_tasks)

    def _execute_approved_tasks(self):
        approved_tasks = self.agent.get_tasks_by_status("approved")
        if not approved_tasks:
            messagebox.showinfo("Execute Tasks", "No approved tasks to execute.")
            return

        for task in approved_tasks:
            response = messagebox.askquestion(
                "Execute Task",
                f"Task #{task['id']}:\nDescription: {task['description']}\nCommand: {task['command']}\n\nExecute this task?"
            )
            if response == "yes":
                try:
                    result = self.agent.execute_task(task["id"])
                    if result["status"] == "completed":
                        messagebox.showinfo("Task Completed", f"Task #{task['id']} completed successfully:\n{result['result']}")
                    else:
                        messagebox.showerror("Task Failed", f"Task #{task['id']} failed:\n{result['error']}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to execute task: {e}")

    def view_failed_tasks(self):
        """Display failed tasks."""
        self.run_in_thread(self._view_failed_tasks)

    def _view_failed_tasks(self):
        failed_tasks = self.agent.get_tasks_by_status("failed")
        if not failed_tasks:
            messagebox.showinfo("Failed Tasks", "No failed tasks.")
        else:
            tasks_str = "\n".join([f"ID: {task['id']} - {task['description']}\nError: {task['error']}" for task in failed_tasks])
            messagebox.showinfo("Failed Tasks", tasks_str)

    def generate_fix_for_failed_task(self):
        """Generate fixes for a failed task."""
        task_id = simpledialog.askinteger("Generate Fix", "Enter the ID of the failed task:")
        if task_id:
            self.run_in_thread(self._generate_fix_for_failed_task, task_id)

    def _generate_fix_for_failed_task(self, task_id):
        try:
            fixes = self.agent.generate_error_fixes(task_id)
            if not fixes:
                messagebox.showinfo("No Fixes", "No fixes generated.")
            else:
                fixes_str = "\n".join(fixes)
                messagebox.showinfo("Suggested Fixes", fixes_str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate fixes: {e}")

    def view_task_history(self):
        """Display task history."""
        self.run_in_thread(self._view_task_history)

    def _view_task_history(self):
        history = self.agent.history["commands"]
        if not history:
            messagebox.showinfo("Task History", "No task history available.")
        else:
            history_str = "\n".join([
                f"Task ID: {entry['task_id']}\nCommand: {entry['command']}\nExecuted At: {entry['executed_at']}\nSuccess: {entry['success']}\n"
                for entry in history
            ])
            messagebox.showinfo("Task History", history_str)

    def run(self):
        """Run the GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    from AI_agent import CopilotAgent  # Import your CopilotAgent class

    agent = CopilotAgent()
    gui = CopilotAgentGUI(agent)
    gui.run()