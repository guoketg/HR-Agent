import json
import time
from client import get_client, get_provider_and_model
from tools.schema import tools_schema
from tools.employee_tools import (
    get_employee_directory, get_employee_by_id,
    add_employee, update_employee, delete_employee
)
from tools.payroll_tools import calculate_payroll_and_tax, export_payroll_csv
from config import logger

SYSTEM_PROMPT = """你是专业的 HR 助手。请自动规划工具调用链完成计算。
-查询员工：调用 get_employee_by_id 工具
计算工资：调用calculate_payroll_and_tax 工具
-当且仅当用户明确要求导出或者保存csv文件时，才调用export_payroll_csv 工具
"""

def validate_message(msg):
    if not isinstance(msg, dict):
        return False
    if "role" not in msg or "content" not in msg:
        return False
    if msg["content"] is None:
        return False
    if msg["role"] == "tool" and "tool_call_id" not in msg:
        return False
    return True

def validate_messages(msgs):
    for i, m in enumerate(msgs):
        if not validate_message(m):
            logger.error(f"不合规消息 #{i}: {m}")
            return False
    return True

def agent_orchestrator(user_message, history, messages_state, selected_model):
    try:
        logger.info(f"开始处理用户请求: {user_message}, 模型: {selected_model}")

        if not isinstance(messages_state, list):
            messages_state = []
        if not isinstance(history, list):
            history = []

        if not messages_state:
            messages_state = [{"role": "system", "content": SYSTEM_PROMPT}]
            logger.info("初始化系统提示词")

        messages_state.append({"role": "user", "content": user_message})
        messages_state = [m for m in messages_state if isinstance(m, dict) and "role" in m and "content" in m and m["content"] is not None]
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": f"[当前引擎: {selected_model}] 正在规划任务流..."})
        yield history, messages_state

        max_iterations = 10
        iteration = 0
        provider, model = get_provider_and_model(selected_model)
        client = get_client(provider)

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"开始迭代 {iteration}/{max_iterations}")

            try:
                logger.info(f"调用模型 {selected_model} 进行推理")
                if not validate_messages(messages_state):
                    logger.error("消息验证失败，终止请求")
                    raise ValueError("Invalid messages format")
                logger.info(f"发送的消息: {messages_state}")

                response = client.chat.completions.create(
                    model=model,
                    messages=messages_state,
                    tools=tools_schema,
                    tool_choice="auto"
                )
                response_msg = response.choices[0].message
                logger.info(f"收到响应: role={response_msg.role}, content={response_msg.content}, tool_calls={response_msg.tool_calls}")

                if response_msg.tool_calls:
                    assistant_msg = {"role": response_msg.role, "content": response_msg.content or "", "tool_calls": [
                        {"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}, "type": "function"}
                        for tc in response_msg.tool_calls
                    ]}
                    messages_state.append(assistant_msg)
                elif response_msg.content:
                    messages_state.append({"role": response_msg.role, "content": response_msg.content})

                messages_state = [m for m in messages_state if isinstance(m, dict) and "role" in m]

                if response_msg.tool_calls:
                    logger.info(f"模型请求调用 {len(response_msg.tool_calls)} 个工具")

                    for tool_call in response_msg.tool_calls:
                        func_name = tool_call.function.name
                        logger.info(f"准备调用工具: {func_name}")

                        try:
                            func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            logger.info(f"工具参数: {func_args}")
                        except json.JSONDecodeError as e:
                            logger.warning(f"工具参数解析失败: {e}")
                            func_args = {}

                        history[-1] = {"role": "assistant", "content": history[-1]["content"] + f"\n\n> **触发节点**: `{func_name}`"}
                        yield history, messages_state

                        start_time = time.time()
                        if func_name == "get_employee_directory":
                            tool_result = get_employee_directory()
                        elif func_name == "get_employee_by_id":
                            tool_result = get_employee_by_id(employee_id=func_args.get("employee_id", ""))
                        elif func_name == "add_employee":
                            tool_result = add_employee(employee_json=func_args.get("employee_json", "{}"))
                        elif func_name == "update_employee":
                            tool_result = update_employee(employee_json=func_args.get("employee_json", "{}"))
                        elif func_name == "delete_employee":
                            tool_result = delete_employee(employee_id=func_args.get("employee_id", ""))
                        elif func_name == "calculate_payroll_and_tax":
                            tool_result = calculate_payroll_and_tax(employees_json=func_args.get("employees_json", "[]"))
                        elif func_name == "export_payroll_csv":
                            tool_result = export_payroll_csv(payroll_json=func_args.get("payroll_json", "[]"))
                        else:
                            logger.error(f"未找到指定工具: {func_name}")
                            tool_result = json.dumps({"error": f"未找到指定工具: {func_name}"})

                        execution_time = time.time() - start_time
                        logger.info(f"工具 {func_name} 执行完成，耗时: {execution_time:.2f}秒")

                        tool_msg = {
                            "role": "tool",
                            "content": tool_result,
                            "tool_call_id": tool_call.id
                        }
                        logger.info(f"添加工具消息: {tool_msg}")
                        messages_state.append(tool_msg)
                        logger.info(f"工具结果已回注到上下文，当前消息数: {len(messages_state)}")

                    logger.info("继续下一轮迭代")
                    continue

                else:
                    final_text = response_msg.content if response_msg.content else "任务完成"
                    logger.info(f"模型输出最终结果: {final_text[:100]}...")

                    messages_state.append({"role": "assistant", "content": final_text})
                    messages_state = [m for m in messages_state if isinstance(m, dict) and "role" in m]
                    history[-1] = {"role": "assistant", "content": final_text}
                    yield history, messages_state
                    break

            except Exception as e:
                logger.error(f"迭代 {iteration} 执行失败: {str(e)}", exc_info=True)
                error_msg = f"[FAIL] 迭代 {iteration} 执行失败: {str(e)}"
                history[-1] = {"role": "assistant", "content": history[-1]["content"] + f"\n\n{error_msg}"}
                yield history, messages_state
                break

        if iteration >= max_iterations:
            logger.warning(f"已达到最大迭代次数 {max_iterations}，任务可能未完成")
            history[-1] = {"role": "assistant", "content": history[-1]["content"] + "\n\n已达到最大迭代次数，任务可能未完成"}
            messages_state = [m for m in messages_state if isinstance(m, dict) and "role" in m and "content" in m and m["content"] is not None]
            yield history, messages_state

        logger.info(f"用户请求处理完成，总迭代次数: {iteration}")

    except Exception as e:
        logger.error(f"Agent 调度器执行失败: {str(e)}", exc_info=True)
        error_msg = f"[FAIL] Agent 调度器执行失败: {str(e)}"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": error_msg})
        yield history, messages_state
