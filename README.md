# GitHub Copilot Task Agent

A powerful AI assistant that helps automate repetitive tasks using GitHub Copilot and OpenAI's API to generate, manage, and execute shell commands.

> **Note:** This project is still a work in progress and has only been used as a theoretical concept so far.

## 🚀 Features

- Generate shell commands from natural language descriptions
- Review and approve/reject suggested commands
- Execute commands with error handling
- Get AI-generated explanations of command behavior
- Generate fixes for failed commands
- Track command history for future reference
- Available in both CLI and GUI interfaces

## 📋 Files Overview

- `AI_agent.py` - The original CLI version of the agent
- `AI_agent_fixed.py` - Fixed version using OpenAI API directly
- `AI_agent_modified.py` - Modified version with enhanced features
- `AI_agent_gui.py` - Graphical user interface for the agent
- `AI_agent.ps1` - PowerShell script placeholder

## 🛠️ Setup and Installation

1. Clone this repository:
    ```
    git clone https://github.com/yourusername/github-copilot-task-agent.git
    cd github-copilot-task-agent
    ```

2. Install required dependencies:
    ```
    pip install openai tkinter
    ```

3. Set up your OpenAI API key:
    ```python
    import os
    os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    ```

## 💻 Usage

### CLI Version
```
python AI_agent.py
```

### GUI Version
```
python AI_agent_gui.py
```

## 📚 How It Works

1. **Task Generation**: Submit a natural language description of what you want to accomplish
2. **Review**: Examine the suggested shell command
3. **Approval**: Approve or reject the suggested command
4. **Execution**: Execute approved commands with full error handling
5. **Error Resolution**: For failed commands, get AI-suggested fixes

## 📂 Data Storage

The agent uses two JSON files for persistent storage:
- `tasks.json`: Stores all tasks with their status (pending, approved, completed, failed)
- `history.json`: Maintains a history of executed commands

## 🔄 Task Lifecycle

```
Natural Language Description
          ↓
Command Generation
          ↓
Review & Approval
          ↓
Execution
      /     \
Success     Failure
     |         |
 Complete   Generate Fix
                  |
              New Task
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.