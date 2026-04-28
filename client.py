import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from config import logger

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

OLLAMA_BASE_URL = 'http://localhost:11434/v1'
OLLAMA_API_KEY = 'local'

DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DASHSCOPE_BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

def get_client(provider='ollama'):
    if provider == 'ollama':
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY, timeout=120)
    elif provider == 'deepseek':
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        return OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=api_key, timeout=120)
    elif provider == 'dashscope':
        api_key = os.getenv('DASHSCOPE_API_KEY', '')
        return OpenAI(base_url=DASHSCOPE_BASE_URL, api_key=api_key, timeout=120)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def get_provider_and_model(selected_model):
    if selected_model == 'qwen3.5:9b':
        return 'ollama', 'qwen3.5:9b'
    elif selected_model in ['deepseek-chat', 'deepseek-reasoner']:
        return 'deepseek', selected_model
    elif selected_model in ['qwen3.5-plus', 'qwen3.6-plus']:
        return 'dashscope', selected_model
    else:
        return 'ollama', selected_model

def test_connection():
    try:
        client = get_client('ollama')
        print("[OK] Ollama 客户端初始化成功")
        return True
    except Exception as e:
        print(f"[FAIL] Ollama 客户端初始化失败: {e}")
        return False
