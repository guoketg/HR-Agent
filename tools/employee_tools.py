import json
from config import EMPLOYEES_FILE, SALARY_LEVELS, logger

def _load_employees():
    if EMPLOYEES_FILE.exists():
        with open(EMPLOYEES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def _save_employees(employees):
    with open(EMPLOYEES_FILE, 'w', encoding='utf-8') as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)

def get_employee_directory():
    try:
        employees = _load_employees()
        if not employees:
            return json.dumps({"error": "员工数据为空"}, ensure_ascii=False)
        return json.dumps(employees, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)

def get_employee_by_id(employee_id: str):
    try:
        employees = _load_employees()
        for emp in employees:
            if emp.get("id") == employee_id:
                return json.dumps(emp, ensure_ascii=False)
        return json.dumps({"error": f"未找到员工: {employee_id}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)

def add_employee(employee_json: str):
    try:
        if not employee_json or not employee_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        try:
            new_emp = json.loads(employee_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        if not isinstance(new_emp, dict):
            return json.dumps({"error": "输入数据格式错误，应为对象"}, ensure_ascii=False)
        if "id" not in new_emp or "name" not in new_emp or "level" not in new_emp:
            return json.dumps({"error": "缺少必填字段 (id, name, level)"}, ensure_ascii=False)
        employees = _load_employees()
        if any(emp["id"] == new_emp["id"] for emp in employees):
            return json.dumps({"error": f"员工ID已存在: {new_emp['id']}"}, ensure_ascii=False)
        if new_emp["level"] not in SALARY_LEVELS:
            return json.dumps({"error": f"无效的职级: {new_emp['level']}"}, ensure_ascii=False)
        employees.append(new_emp)
        _save_employees(employees)
        return json.dumps({"status": "success", "message": f"员工 {new_emp['name']} 已添加", "employee": new_emp}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"添加失败: {str(e)}"}, ensure_ascii=False)

def update_employee(employee_json: str):
    try:
        if not employee_json or not employee_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        try:
            update_data = json.loads(employee_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        if not isinstance(update_data, dict):
            return json.dumps({"error": "输入数据格式错误，应为对象"}, ensure_ascii=False)
        if "id" not in update_data:
            return json.dumps({"error": "缺少必填字段 (id)"}, ensure_ascii=False)
        employees = _load_employees()
        found = False
        for i, emp in enumerate(employees):
            if emp["id"] == update_data["id"]:
                if "name" in update_data:
                    emp["name"] = update_data["name"]
                if "level" in update_data:
                    if update_data["level"] not in SALARY_LEVELS:
                        return json.dumps({"error": f"无效的职级: {update_data['level']}"}, ensure_ascii=False)
                    emp["level"] = update_data["level"]
                employees[i] = emp
                found = True
                break
        if not found:
            return json.dumps({"error": f"未找到员工: {update_data['id']}"}, ensure_ascii=False)
        _save_employees(employees)
        return json.dumps({"status": "success", "message": f"员工 {update_data['id']} 已更新", "employee": emp}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"更新失败: {str(e)}"}, ensure_ascii=False)

def delete_employee(employee_id: str):
    try:
        if not employee_id or not employee_id.strip():
            return json.dumps({"error": "员工ID不能为空"}, ensure_ascii=False)
        employees = _load_employees()
        original_len = len(employees)
        employees = [emp for emp in employees if emp["id"] != employee_id]
        if len(employees) == original_len:
            return json.dumps({"error": f"未找到员工: {employee_id}"}, ensure_ascii=False)
        _save_employees(employees)
        return json.dumps({"status": "success", "message": f"员工 {employee_id} 已删除"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"删除失败: {str(e)}"}, ensure_ascii=False)
