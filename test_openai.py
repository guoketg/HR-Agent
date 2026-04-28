from openai import OpenAI
# 初始化 Ollama 客⼾端（使⽤ OpenAI 兼容接⼝）
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='local',
    timeout=120
 )
# 测试连接
try:
    response = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "你是谁"}],
    max_tokens=1000
    )
    print("✅ Ollama API 连接成功")
    print(f"模型回复: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Ollama API 连接失败: {e}")