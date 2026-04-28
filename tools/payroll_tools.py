import json
import csv
from datetime import datetime
from config import SALARY_LEVELS, DATA_DIR

def calculate_payroll_and_tax(employees_json: str):
    try:
        if not employees_json or not employees_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        try:
            employees = json.loads(employees_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        if not isinstance(employees, list):
            return json.dumps({"error": "输入数据格式错误，应为数组"}, ensure_ascii=False)
        if len(employees) == 0:
            return json.dumps({"error": "员工列表为空"}, ensure_ascii=False)
        results = []
        for emp in employees:
            if not isinstance(emp, dict):
                continue
            emp_result = emp.copy()
            if "base_salary" in emp and "social_insurance" in emp and "tax" in emp and "net_salary" in emp:
                emp_result["应发工资"] = emp["base_salary"]
                emp_result["五险一金扣除"] = emp["social_insurance"]
                emp_result["个税扣除"] = emp["tax"]
                emp_result["实发工资"] = emp["net_salary"]
            elif "level" not in emp:
                emp_result["error"] = "缺少 level 字段"
                results.append(emp_result)
                continue
            else:
                base_salary = SALARY_LEVELS.get(emp["level"], 0)
                if base_salary <= 0:
                    emp_result["error"] = f"无效的职级: {emp.get('level')}"
                    results.append(emp_result)
                    continue
                social_security = base_salary * 0.20
                tax = max(0, (base_salary - social_security) * 0.05)
                net_salary = base_salary - social_security - tax
                emp_result["应发工资"] = base_salary
                emp_result["五险一金扣除"] = social_security
                emp_result["个税扣除"] = tax
                emp_result["实发工资"] = net_salary
            results.append(emp_result)
        if not results:
            return json.dumps({"error": "没有有效的员工数据"}, ensure_ascii=False)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"计算失败: {str(e)}"}, ensure_ascii=False)

def export_payroll_csv(payroll_json: str):
    try:
        if not payroll_json or not payroll_json.strip():
            return json.dumps({"error": "输入数据为空"}, ensure_ascii=False)
        try:
            payroll_data = json.loads(payroll_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"JSON 解析失败: {str(e)}"}, ensure_ascii=False)
        if not isinstance(payroll_data, list) or len(payroll_data) == 0:
            return json.dumps({"error": "工资数据为空或格式错误"}, ensure_ascii=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"payroll_report_{timestamp}.csv"
        filepath = DATA_DIR / filename
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=payroll_data[0].keys())
                writer.writeheader()
                writer.writerows(payroll_data)
        except IOError as e:
            return json.dumps({"error": f"文件写入失败: {str(e)}"}, ensure_ascii=False)
        return json.dumps({"status": "success", "file_path": str(filepath), "record_count": len(payroll_data)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"导出失败: {str(e)}"}, ensure_ascii=False)
