
---

# HR Agent - Intelligent Payroll Management System (English)

An experimental project demonstrating the comparison between **traditional SaaS architecture** and **AI Agent dynamic orchestration architecture**.

## Project Structure

```
download_llm/
├── app.py                      # Gradio Web UI entry point
├── config.py                   # Global configuration (paths, logging, salary levels)
├── client.py                   # Ollama LLM client
├── tools/
│   ├── __init__.py
│   ├── employee_tools.py       # Employee CRUD tools
│   ├── payroll_tools.py        # Payroll calculation and export tools
│   └── schema.py              # MCP tool schema definition
├── services/
│   ├── __init__.py
│   └── agent.py               # Agent orchestrator
├── data/                      # Data storage directory
│   ├── employees.json         # Employee data persistence
│   └── payroll_report_*.csv   # Exported payroll reports
├── test_app.py                # Unit tests
├── requirements.txt           # Python dependencies
├── .github/
│   └── workflows/
│       └── test.yml           # GitHub Actions CI/CD
├── .gitignore
└── README.md
```

## Features

### Control Group: Traditional SaaS
- Hardcoded business flow: Query Employees -> Calculate Payroll -> Export CSV
- One-click execution, efficient but inflexible

### Experimental Group: AI Agent
- Natural language interaction, intent-driven
- Dynamic tool chain planning
- Full CRUD operations support:
  - `get_employee_directory` - Query all employees
  - `get_employee_by_id` - Query by ID
  - `add_employee` - Add new employee
  - `update_employee` - Update employee info
  - `delete_employee` - Delete employee
  - `calculate_payroll_and_tax` - Calculate payroll
  - `export_payroll_csv` - Export CSV

## Salary Levels

| Level | Base Salary |
|-------|-------------|
| L1    | 10,000      |
| L2    | 20,000      |
| L3    | 35,000      |

Calculation Rules:
- Social Insurance = Base Salary × 20%
- Individual Income Tax = (Base Salary - Social Insurance) × 5%
- Net Salary = Base Salary - Social Insurance - Tax

## Requirements

- Python 3.10+
- Ollama (optional, for local qwen3.5:9b)
- API Keys (.env file):
  - `DASHSCOPE_API_KEY` - Alibaba Cloud Dashscope (qwen3.5-plus, qwen3.6-plus)
  - `DEEPSEEK_API_KEY` - DeepSeek API (deepseek-chat, deepseek-reasoner)
- Dependencies: gradio, openai, python-dotenv

## Installation & Usage

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

Visit http://127.0.0.1:7861

## Testing

```bash
python test_app.py -v
```


## Data Storage

- Employee data: `data/employees.json`
- Payroll reports: `data/payroll_report_YYYYMMDD_HHMMSS.csv`

All data is stored in the `data/` directory under the project root, without occupying system disk space.

## CI/CD

GitHub Actions is configured to run tests automatically on push and pull request to the `develop` branch.

## Available Models

| Model | Provider | Description |
|-------|----------|-------------|
| `qwen3.5:9b` | Ollama (local) | Default, lightweight |
| `qwen3.5-plus` | Alibaba Dashscope | Cloud, more powerful |
| `qwen3.6-plus` | Alibaba Dashscope | Cloud, most powerful |
| `deepseek-chat` | DeepSeek | Cloud |
| `deepseek-reasoner` | DeepSeek | Cloud, reasoning specialized |


# HR Agent - 智能工资管理系统

# HR Agent - Intelligent Payroll Management System

An experimental project demonstrating the comparison between **traditional SaaS architecture** and **AI Agent dynamic orchestration architecture**.

## Project Structure

```
download_llm/
├── app.py                      # Gradio Web UI entry point
├── config.py                   # Global configuration (paths, logging, salary levels)
├── client.py                   # Ollama LLM client
├── tools/
│   ├── __init__.py
│   ├── employee_tools.py       # Employee CRUD tools
│   ├── payroll_tools.py        # Payroll calculation and export tools
│   └── schema.py              # MCP tool schema definition
├── services/
│   ├── __init__.py
│   └── agent.py                # Agent orchestrator
├── data/                       # Data storage directory
│   ├── employees.json          # Employee data persistence
│   └── payroll_report_*.csv   # Exported payroll reports
├── test_app.py                 # Unit tests
├── requirements.txt            # Python dependencies
├── .github/
│   └── workflows/
│       └── test.yml           # GitHub Actions CI/CD
├── .gitignore
└── README.md
```

## Features

### Control Group: Traditional SaaS
- Hardcoded business flow: Query Employees -> Calculate Payroll -> Export CSV
- One-click execution, efficient but inflexible

### Experimental Group: AI Agent
- Natural language interaction, intent-driven
- Dynamic tool chain planning
- Full CRUD operations support:
  - `get_employee_directory` - Query all employees
  - `get_employee_by_id` - Query by ID
  - `add_employee` - Add new employee
  - `update_employee` - Update employee info
  - `delete_employee` - Delete employee
  - `calculate_payroll_and_tax` - Calculate payroll
  - `export_payroll_csv` - Export CSV

## Salary Levels

| Level | Base Salary |
|-------|-------------|
| L1    | 10,000      |
| L2    | 20,000      |
| L3    | 35,000      |

Calculation Rules:
- Social Insurance = Base Salary × 20%
- Individual Income Tax = (Base Salary - Social Insurance) × 5%
- Net Salary = Base Salary - Social Insurance - Tax

## Requirements

- Python 3.10+
- Ollama (optional, for local qwen3.5:9b)
- API Keys (.env file):
  - `DASHSCOPE_API_KEY` - Alibaba Cloud Dashscope (qwen3.5-plus, qwen3.6-plus)
  - `DEEPSEEK_API_KEY` - DeepSeek API (deepseek-chat, deepseek-reasoner)
- Dependencies: gradio, openai, python-dotenv

## Installation & Usage

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

Visit http://127.0.0.1:7860

## Testing

```bash
python test_app.py -v
```

## Data Storage

- Employee data: `data/employees.json`
- Payroll reports: `data/payroll_report_YYYYMMDD_HHMMSS.csv`

## CI/CD

GitHub Actions is configured to run tests automatically on push and pull request to the `develop` branch.

## Available Models

| Model | Provider | Description |
|-------|----------|-------------|
| `qwen3.5:9b` | Ollama (local) | Default, lightweight |
| `qwen3.5-plus` | Alibaba Dashscope | Cloud, more powerful |
| `qwen3.6-plus` | Alibaba Dashscope | Cloud, most powerful |
| `deepseek-chat` | DeepSeek | Cloud |
| `deepseek-reasoner` | DeepSeek | Cloud, reasoning specialized |

## Changelog

### 2026-04-28
- Project basic setup completed
- Traditional SaaS architecture: Query Employees -> Calculate Payroll -> Export CSV
- AI Agent architecture: Natural language interaction, intent-driven
- Full CRUD operations and dynamic tool chain planning
- Multi-model support: Ollama, Dashscope, DeepSeek APIs

### 2026-05-03
- Added Redis storage for conversation history
- Frontend supports selecting and loading historical conversations
- Optimized Gradio Chatbot component message format display
