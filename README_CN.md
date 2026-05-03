---

# HR Agent - 智能工资管理系统

一个演示 **传统 SaaS 架构** 与 **AI Agent 动态编排架构** 对比的实验性项目。

## 项目架构

```
download_llm/
├── app.py                      # Gradio Web UI 入口
├── config.py                   # 全局配置 (路径、日志、薪资级别)
├── client.py                   # Ollama LLM 客户端
├── tools/
│   ├── __init__.py
│   ├── employee_tools.py       # 员工 CRUD 工具
│   ├── payroll_tools.py        # 工资计算与导出工具
│   └── schema.py               # MCP 工具 Schema 定义
├── services/
│   ├── __init__.py
│   └── agent.py                # Agent 调度器
├── data/                       # 数据存储目录
│   ├── employees.json          # 员工数据持久化
│   └── payroll_report_*.csv    # 导出的工资报表
├── test_app.py                 # 单元测试
├── requirements.txt            # Python 依赖
├── .github/
│   └── workflows/
│       └── test.yml            # GitHub Actions CI/CD
├── .gitignore
└── README.md
```

## 功能特性

### 控制组：传统 SaaS
- 硬编码业务流程：查员工 -> 算工资 -> 导 CSV
- 一键执行，高效但缺乏灵活性

### 实验组：AI Agent
- 自然语言交互，支持意图驱动
- 动态规划工具调用链
- 支持完整 CRUD 操作：
  - `get_employee_directory` - 查询所有员工
  - `get_employee_by_id` - 按 ID 查询
  - `add_employee` - 新增员工
  - `update_employee` - 更新员工
  - `delete_employee` - 删除员工
  - `calculate_payroll_and_tax` - 计算工资
  - `export_payroll_csv` - 导出 CSV

## 薪资级别

| 职级 | 基本工资 |
|------|----------|
| L1   | 10,000   |
| L2   | 20,000   |
| L3   | 35,000   |

工资计算规则：
- 五险一金扣除 = 基本工资 × 20%
- 个税扣除 = (基本工资 - 五险一金) × 5%
- 实发工资 = 基本工资 - 五险一金 - 个税

## 环境要求

- Python 3.10+
- Ollama (可选，本地运行 qwen3.5:9b)
- API 密钥 (.env 文件):
  - `DASHSCOPE_API_KEY` - 阿里云百炼 (qwen3.5-plus, qwen3.6-plus)
  - `DEEPSEEK_API_KEY` - DeepSeek API (deepseek-chat, deepseek-reasoner)
- 依赖包：gradio, openai, python-dotenv

## 安装运行

```bash
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

访问 http://127.0.0.1:7860

## 测试

```bash
python test_app.py -v
```

## 数据存储

- 员工数据：`data/employees.json`
- 工资报表：`data/payroll_report_YYYYMMDD_HHMMSS.csv`

所有数据存储在项目根目录的 `data/` 文件夹下，不占用系统盘空间。

## 可用模型

| 模型 | 提供商 | 描述 |
|------|--------|------|
| `qwen3.5:9b` | Ollama (本地) | 默认，轻量 |
| `qwen3.5-plus` | 阿里云百炼 | 云端，更强 |
| `qwen3.6-plus` | 阿里云百炼 | 云端，最强 |
| `deepseek-chat` | DeepSeek | 云端 |
| `deepseek-reasoner` | DeepSeek | 云端，推理专长 |

## 更新日志

### 2026-04-28
- 完成项目基本搭建
- 实现传统 SaaS 架构：查询员工 → 计算工资 → 导出 CSV
- 实现 AI Agent 架构：自然语言交互，意图驱动
- 支持完整 CRUD 操作和动态工具链规划
- 集成 Ollama 和 Dashscope/DeepSeek API 多模型支持

### 2026-05-03
- 添加 Redis 存储对话历史信息
- 前端支持选中历史对话并自动加载
- 优化 Gradio Chatbot 组件的消息格式显示
