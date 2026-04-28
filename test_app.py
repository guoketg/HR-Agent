import unittest
import json
import os
from config import SALARY_LEVELS, DATA_DIR, EMPLOYEES_FILE
from tools.employee_tools import (
    get_employee_directory, get_employee_by_id,
    add_employee, update_employee, delete_employee,
    _save_employees, _load_employees
)
from tools.payroll_tools import calculate_payroll_and_tax, export_payroll_csv


class TestEmployeeTools(unittest.TestCase):
    def setUp(self):
        _save_employees([
            {"id": "E01", "name": "张三", "level": "L1"},
            {"id": "E02", "name": "李四", "level": "L2"},
            {"id": "E03", "name": "王五", "level": "L3"}
        ])

    def test_get_employee_directory(self):
        result = get_employee_directory()
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("level", data[0])

    def test_get_employee_by_id_found(self):
        result = get_employee_by_id("E01")
        data = json.loads(result)
        self.assertEqual(data["id"], "E01")
        self.assertEqual(data["name"], "张三")

    def test_get_employee_by_id_not_found(self):
        result = get_employee_by_id("E99")
        data = json.loads(result)
        self.assertIn("error", data)

    def test_add_employee_success(self):
        result = add_employee('{"id": "E04", "name": "赵六", "level": "L2"}')
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        employees = _load_employees()
        self.assertEqual(len(employees), 4)

    def test_add_employee_duplicate_id(self):
        result = add_employee('{"id": "E01", "name": "赵六", "level": "L2"}')
        data = json.loads(result)
        self.assertIn("error", data)

    def test_add_employee_invalid_level(self):
        result = add_employee('{"id": "E04", "name": "赵六", "level": "L9"}')
        data = json.loads(result)
        self.assertIn("error", data)

    def test_add_employee_missing_fields(self):
        result = add_employee('{"id": "E04"}')
        data = json.loads(result)
        self.assertIn("error", data)

    def test_update_employee_name(self):
        result = update_employee('{"id": "E01", "name": "张三大"}')
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        emp = json.loads(get_employee_by_id("E01"))
        self.assertEqual(emp["name"], "张三大")

    def test_update_employee_level(self):
        result = update_employee('{"id": "E01", "level": "L3"}')
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")

    def test_update_employee_not_found(self):
        result = update_employee('{"id": "E99", "name": "测试"}')
        data = json.loads(result)
        self.assertIn("error", data)

    def test_delete_employee_success(self):
        result = delete_employee("E01")
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        employees = _load_employees()
        self.assertEqual(len(employees), 2)

    def test_delete_employee_not_found(self):
        result = delete_employee("E99")
        data = json.loads(result)
        self.assertIn("error", data)


class TestPayrollTools(unittest.TestCase):
    def test_calculate_payroll_and_tax_valid(self):
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L1"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("应发工资", data[0])
        self.assertIn("五险一金扣除", data[0])
        self.assertIn("个税扣除", data[0])
        self.assertIn("实发工资", data[0])

    def test_calculate_payroll_and_tax_empty(self):
        result = calculate_payroll_and_tax("")
        data = json.loads(result)
        self.assertIn("error", data)

    def test_calculate_payroll_and_tax_invalid_json(self):
        result = calculate_payroll_and_tax("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)

    def test_export_payroll_csv_valid(self):
        payroll_data = json.dumps([
            {"id": "E01", "name": "张三", "level": "L1", "应发工资": 10000, "五险一金扣除": 2000, "个税扣除": 400, "实发工资": 7600}
        ])
        result = export_payroll_csv(payroll_data)
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        self.assertTrue(os.path.exists(data["file_path"]))

    def test_export_payroll_csv_empty(self):
        result = export_payroll_csv("")
        data = json.loads(result)
        self.assertIn("error", data)


class TestPayrollCalculation(unittest.TestCase):
    def test_l1_level_salary_calculation(self):
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L1"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)

        base_salary = SALARY_LEVELS["L1"]
        social_security = base_salary * 0.20
        tax = (base_salary - social_security) * 0.05
        expected_net = base_salary - social_security - tax

        self.assertAlmostEqual(data[0]["应发工资"], base_salary)
        self.assertAlmostEqual(data[0]["五险一金扣除"], social_security)
        self.assertAlmostEqual(data[0]["个税扣除"], tax, places=2)
        self.assertAlmostEqual(data[0]["实发工资"], expected_net, places=2)

    def test_l2_level_salary_calculation(self):
        employees = json.dumps([{"id": "E02", "name": "李四", "level": "L2"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)

        base_salary = SALARY_LEVELS["L2"]
        social_security = base_salary * 0.20
        tax = (base_salary - social_security) * 0.05
        expected_net = base_salary - social_security - tax

        self.assertAlmostEqual(data[0]["应发工资"], base_salary)
        self.assertAlmostEqual(data[0]["实发工资"], expected_net, places=2)

    def test_l3_level_salary_calculation(self):
        employees = json.dumps([{"id": "E03", "name": "王五", "level": "L3"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)

        base_salary = SALARY_LEVELS["L3"]
        social_security = base_salary * 0.20
        tax = (base_salary - social_security) * 0.05
        expected_net = base_salary - social_security - tax

        self.assertAlmostEqual(data[0]["应发工资"], base_salary)
        self.assertAlmostEqual(data[0]["实发工资"], expected_net, places=2)


class TestAgentOrchestrator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from unittest.mock import Mock
        cls.mock_client_patcher = None

    def test_agent_orchestrator_simple_query(self):
        from unittest.mock import Mock, patch
        from services.agent import agent_orchestrator

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].message.content = "这是测试回复"
        mock_response.choices[0].message.tool_calls = None

        with patch('client.client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            history = []
            messages_state = []
            results = list(agent_orchestrator("测试问题", history, messages_state, "qwen3.5:9b"))
            self.assertGreater(len(results), 0)


class TestDataPersistence(unittest.TestCase):
    def setUp(self):
        _save_employees([
            {"id": "E01", "name": "张三", "level": "L1"},
            {"id": "E02", "name": "李四", "level": "L2"},
            {"id": "E03", "name": "王五", "level": "L3"}
        ])

    def test_employees_persisted(self):
        employees = _load_employees()
        self.assertEqual(len(employees), 3)

    def test_data_directory_created(self):
        self.assertTrue(DATA_DIR.exists())


if __name__ == "__main__":
    unittest.main()
