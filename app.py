import gradio as gr
import json
from config import logger
from client import test_connection
from tools.employee_tools import get_employee_directory
from tools.payroll_tools import calculate_payroll_and_tax, export_payroll_csv
from services.agent import agent_orchestrator
from services.conversation_store import (
    create_conversation, get_conversation, update_conversation,
    delete_conversation, list_conversations, rename_conversation
)

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

def load_conversation_list():
    conversations = list_conversations()
    return [(f"{conv['title']} ({conv['id'][:8]})", conv["id"]) for conv in conversations]

def on_new_conversation():
    conv = create_conversation()
    return conv["id"], [{"role": "user", "content": ""}], load_conversation_list()

def on_load_conversation(conversation_id):
    if not conversation_id:
        return [], None, gr.update()

    if isinstance(conversation_id, (list, tuple)):
        conversation_id = conversation_id[1] if len(conversation_id) > 1 else (conversation_id[0] if conversation_id else None)

    if not conversation_id:
        return [], None, gr.update()

    conv = get_conversation(conversation_id)
    if conv:
        chat_messages = []
        last_user_msg = None
        final_assistant_msg = None

        for msg in conv.get("messages", []):
            if isinstance(msg, dict) and 'role' in msg:
                if msg['role'] == 'user':
                    last_user_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''
                elif msg['role'] == 'assistant' and not msg.get('tool_calls'):
                    final_assistant_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''

        if last_user_msg:
            chat_messages.append({"role": "user", "content": last_user_msg})
        if final_assistant_msg:
            chat_messages.append({"role": "assistant", "content": final_assistant_msg})

        return chat_messages, conversation_id, conv["title"]
    return [], None, gr.update()

def on_delete_conversation(conversation_id):
    if conversation_id:
        delete_conversation(conversation_id)
    return None, [], load_conversation_list()

def on_save_conversation(conversation_id, messages_state):
    if conversation_id and messages_state:
        update_conversation(conversation_id, messages_state)
    return conversation_id

def on_conversation_change(conversation_id):
    if isinstance(conversation_id,list):
        conversation_id=conversation_id[0] if conversation_id else None

    if conversation_id:
        conv = get_conversation(conversation_id)
        if conv:
            return conv["messages"], conv["title"]
    return [], "新对话"

def on_rename_conversation(conversation_id, new_title):
    if conversation_id and new_title:
        rename_conversation(conversation_id, new_title)
        return load_conversation_list()
    return load_conversation_list()

def chat_submit(user_message, history, messages_state, selected_model, conversation_id):
    if not conversation_id:
        conv = create_conversation(title=user_message[:30] if user_message else "新对话")
        conversation_id = conv["id"]
        # call agent to process
        result_list = list(agent_orchestrator(user_message, history, messages_state, selected_model))
        if result_list:
            final_history, final_messages = result_list[-1]
            # 转换为 Gradio Chatbot 的 messages 格式
            # 只保留 user 和最终 assistant 消息，过滤中间的工具调用消息
            chat_messages = []
            last_user_msg = None
            final_assistant_msg = None

            for msg in final_history:
                if isinstance(msg, dict) and 'role' in msg:
                    if msg['role'] == 'user':
                        last_user_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''
                    elif msg['role'] == 'assistant' and not msg.get('tool_calls'):
                        # 只保留没有 tool_calls 的 assistant 消息（最终回复）
                        final_assistant_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''

            # 构建最终的对话列表，content 可以是简单的字符串
            if last_user_msg:
                chat_messages.append({"role": "user", "content": last_user_msg})
            if final_assistant_msg:
                chat_messages.append({"role": "assistant", "content": final_assistant_msg})

            print(f"[DEBUG] chat_messages: {chat_messages}")

            if not chat_messages:
                chat_messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": "处理失败，请重试"}
                ]
            update_conversation(conversation_id, final_messages)
            return chat_messages, final_messages, conversation_id, load_conversation_list()
        return history if history else [], messages_state if messages_state else [],conversation_id, load_conversation_list()
    else:
        result_list = list(agent_orchestrator(user_message, history, messages_state, selected_model))
        if result_list:
            final_history, final_messages = result_list[-1]
            # 转换为 Gradio Chatbot 的 messages 格式
            chat_messages = []
            last_user_msg = None
            final_assistant_msg = None

            for msg in final_history:
                if isinstance(msg, dict) and 'role' in msg:
                    if msg['role'] == 'user':
                        last_user_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''
                    elif msg['role'] == 'assistant' and not msg.get('tool_calls'):
                        final_assistant_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''

            if last_user_msg:
                chat_messages.append({"role": "user", "content": last_user_msg})
            if final_assistant_msg:
                chat_messages.append({"role": "assistant", "content": final_assistant_msg})

            if not chat_messages:
                chat_messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": "处理失败，请重试"}
                ]
            update_conversation(conversation_id, final_messages)
            return chat_messages, final_messages, conversation_id, load_conversation_list()
        return history if history else [],messages_state if messages_state else [],conversation_id, load_conversation_list()

with gr.Blocks() as demo:
    gr.Markdown("## HR Agent - 智能工资管理系统")

    with gr.Row():
        with gr.Column(scale=1, min_width=200):
            gr.Markdown("### 对话历史")

            conversation_dropdown = gr.Dropdown(
                choices=load_conversation_list(),
                label="选择对话",
                allow_custom_value=True
            )

            with gr.Row():
                new_conv_btn = gr.Button("新建对话", variant="primary", size="sm")
                load_conv_btn = gr.Button("加载", size="sm")
                delete_conv_btn = gr.Button("删除", size="sm", variant="stop")

            conversation_title = gr.Textbox(label="对话标题", lines=1)

            rename_btn = gr.Button("重命名", size="sm")

            gr.Markdown("---")
            gr.Markdown("### 控制组：SaaS")

            saas_btn = gr.Button("一键执行：生成工资单", variant="primary")
            saas_table = gr.Dataframe(headers=["姓名", "职级", "应发", "五险一金", "实发"])
            saas_file = gr.File(label="导出的物理文件")

        with gr.Column(scale=2):
            gr.Markdown("### 实验组：Agent (意图驱动)")

            model_selector = gr.Dropdown(
                choices=[
                    "qwen3.5:9b",
                    "qwen3.5-plus",
                    "qwen3.6-plus",
                    "deepseek-chat",
                    "deepseek-reasoner"
                ],
                value="qwen3.5:9b",
                label="选择大模型"
            )

            messages_state = gr.State([])
            conversation_id_state = gr.State(None)
            chatbot = gr.Chatbot(label="Agent 对话", height=400)
            chat_input = gr.Textbox(label="自然语言指令", placeholder="输入指令，如：查看所有员工工资")

            chat_input.submit(
                fn=chat_submit,
                inputs=[chat_input, chatbot, messages_state, model_selector, conversation_id_state],
                outputs=[chatbot, messages_state, conversation_id_state, conversation_dropdown]
            )

    saas_btn.click(fn=saas_generate_payroll_api, inputs=None, outputs=[saas_table, saas_file])

    new_conv_btn.click(
        fn=on_new_conversation,
        inputs=None,
        outputs=[conversation_id_state, chatbot, conversation_dropdown]
    ).then(
        fn=lambda: ("新对话", []),
        inputs=None,
        outputs=[conversation_title, messages_state]
    )

    load_conv_btn.click(
        fn=on_load_conversation,
        inputs=[conversation_dropdown],
        outputs=[chatbot, messages_state, conversation_title]
    ).then(
        fn=lambda conv_id: conv_id,
        inputs=[conversation_dropdown],
        outputs=[conversation_id_state]
    )

    delete_conv_btn.click(
        fn=on_delete_conversation,
        inputs=[conversation_dropdown],
        outputs=[conversation_id_state, chatbot, conversation_dropdown]
    )

    rename_btn.click(
        fn=on_rename_conversation,
        inputs=[conversation_dropdown, conversation_title],
        outputs=[conversation_dropdown]
    )

    def on_conversation_change(conv_id):
        print(f"[DEBUG] on_conversation_change called with: {conv_id}, type: {type(conv_id)}")
        # 如果是列表（多个选项），忽略，只处理单个字符串 id
        if isinstance(conv_id, (list, tuple)):
            print("[DEBUG] received list/tuple, ignoring change event")
            return gr.no_update(), gr.no_update(), gr.no_update()
        if not conv_id:
            print("[DEBUG] conv_id is empty, ignoring")
            return gr.no_update(), gr.no_update(), gr.no_update()
        conv = get_conversation(conv_id)
        print(f"[DEBUG] get_conversation result: {conv}")
        if conv:
            # 转换存储的消息格式为 Chatbot 期望的格式
            chat_messages = []
            last_user_msg = None
            final_assistant_msg = None

            for msg in conv.get("messages", []):
                if isinstance(msg, dict) and 'role' in msg:
                    if msg['role'] == 'user':
                        last_user_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''
                    elif msg['role'] == 'assistant' and not msg.get('tool_calls'):
                        final_assistant_msg = str(msg.get('content', '')) if msg.get('content') is not None else ''

            if last_user_msg:
                chat_messages.append({"role": "user", "content": last_user_msg})
            if final_assistant_msg:
                chat_messages.append({"role": "assistant", "content": final_assistant_msg})

            print(f"[DEBUG] returning chat_messages: {chat_messages}")
            return chat_messages, conv['title'], conv_id
        print("[DEBUG] conversation not found, returning defaults")
        return [],'新对话',None

    conversation_dropdown.change(
        fn=on_load_conversation,
        inputs=[conversation_dropdown],
        outputs=[chatbot, messages_state, conversation_title]
    ).then(
        fn=lambda conv_id: conv_id,
        inputs=[conversation_dropdown],
        outputs=[conversation_id_state]
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())