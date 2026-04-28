import gradio as gr
import json
from config import logger
from client import test_connection
from tools.employee_tools import get_employee_directory
from tools.payroll_tools import calculate_payroll_and_tax, export_payroll_csv
from services.agent import agent_orchestrator

test_connection()

def saas_generate_payroll_api():
    try:
        emp_str = get_employee_directory()
        if "error" in emp_str:
            raise Exception(emp_str)

        payroll_str = calculate_payroll_and_tax(emp_str)
        if "error" in payroll_str:
            raise Exception(payroll_str)

        export_result = json.loads(export_payroll_csv(payroll_str))
        if "error" in export_result:
            raise Exception(export_result["error"])

        payroll_data = json.loads(payroll_str)
        table_data = [[d["name"], d["level"], d["应发工资"], d["五险一金扣除"], d["实发工资"]] for d in payroll_data]

        return table_data, export_result.get("file_path")
    except Exception as e:
        print(f"[FAIL] SaaS 执行失败: {e}")
        return [[str(e), "", "", "", ""]], None


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 现代软件架构实验：SaaS 巨石架构 vs Agent 动态编排")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 控制组：SaaS (硬编码)")
            gr.Markdown("> 极度高效，但极度死板。开发者提前锁死了业务流。")

            saas_btn = gr.Button("一键执行：生成工资单并下载", variant="primary")
            saas_table = gr.Dataframe(headers=["姓名", "职级", "应发", "五险一金", "实发"])
            saas_file = gr.File(label="导出的物理文件")

            saas_btn.click(fn=saas_generate_payroll_api, inputs=None, outputs=[saas_table, saas_file])

        with gr.Column(scale=1):
            gr.Markdown("### 实验组：Agent (意图驱动)")

            model_selector = gr.Dropdown(
                choices=[
                    "qwen3.5:9b",
                    "qwen3.5-plus",
                    "qwen3.6-plus",
                    "deepseek-chat",
                    "deepseek-reasoner"
                ],
                value="qwen3.5-plus",
                label="选择大模型 (本地9b/云端plus/deepseek)"
            )

            messages_state = gr.State([])
            chatbot = gr.Chatbot(label="Agent 神经推理中枢日志", height=450)
            chat_input = gr.Textbox(label="自然语言指令", placeholder="输入测试用例：帮我查一下全公司的工资，算好扣税，然后给我个 CSV 文件")

            chat_input.submit(
                fn=agent_orchestrator,
                inputs=[chat_input, chatbot, messages_state, model_selector],
                outputs=[chatbot, messages_state]
            ).then(lambda: "", None, chat_input)

if __name__ == "__main__":
    demo.launch()
