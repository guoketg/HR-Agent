tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_directory",
            "description": "第一步：获取全公司所有员工的基础数据（包含姓名和职级）。不需要参数。"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_employee_by_id",
            "description": "根据员工ID查询单个员工的详细信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "员工ID，如 E01"}
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_employee",
            "description": "新增员工到花名册。接收 JSON 字符串，包含 id, name, level 字段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_json": {"type": "string", "description": "员工信息 JSON，格式: {\"id\": \"E04\", \"name\": \"赵六\", \"level\": \"L2\"}"}
                },
                "required": ["employee_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_employee",
            "description": "更新员工信息。可更新 name 或 level 字段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_json": {"type": "string", "description": "员工更新信息 JSON，格式: {\"id\": \"E01\", \"name\": \"新名字\"} 或 {\"id\": \"E01\", \"level\": \"L3\"}"}
                },
                "required": ["employee_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_employee",
            "description": "从花名册删除员工。",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "要删除的员工ID，如 E01"}
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_payroll_and_tax",
            "description": "第二步：接收员工基础数据 JSON，计算实发工资。必须在获取员工名单后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "employees_json": {"type": "string", "description": "由 get_employee_directory 返回的 JSON 数据"}
                },
                "required": ["employees_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_payroll_csv",
            "description": "第三步：将工资详细信息的 JSON 数据导出为 CSV 文件。必须在计算完工资后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "payroll_json": {"type": "string", "description": "由 calculate_payroll_and_tax 返回的工资 JSON"}
                },
                "required": ["payroll_json"]
            }
        }
    }
]
