import json
import uuid
from datetime import datetime
import redis
from config import logger

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

CONVERSATION_INDEX_KEY = 'hr_agent:conversations:index'
CONVERSATION_PREFIX = 'hr_agent:conversation:'

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis 连接成功")
except Exception as e:
    logger.warning(f"Redis 连接失败: {e}，将使用内存存储")
    redis_client = None

_memory_store = {}
_memory_index = {}

def _get_redis_client():
    return redis_client

def _ensure_redis():
    if redis_client is None:
        raise Exception("Redis 不可用，请检查 Redis 服务")
    return redis_client

def create_conversation(title: str = None) -> dict:
    conversation_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    title = title or f"新对话 {timestamp[:10]}"

    conversation = {
        "id": conversation_id,
        "title": title,
        "created_at": timestamp,
        "updated_at": timestamp,
        "messages": []
    }

    client = _get_redis_client()
    if client:
        client.hset(CONVERSATION_PREFIX + conversation_id, mapping={
            "title": title,
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": "[]"
        })
        client.zadd(CONVERSATION_INDEX_KEY, {conversation_id: float(datetime.now().timestamp())})
        client.hset(CONVERSATION_INDEX_KEY + ":titles", conversation_id, title)
    else:
        _memory_index[conversation_id] = {
            "title": title,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        _memory_store[conversation_id] = conversation

    logger.info(f"创建对话: {conversation_id} - {title}")
    return conversation

def get_conversation(conversation_id: str) -> dict:
    if isinstance(conversation_id,(list,tuple)):
        conversation_id=conversation_id[1] if len(conversation_id) > 1 else (conversation_id[0] if conversation_id else None)
    if not conversation_id:
        return None

    client = _get_redis_client()
    if client:
        data = client.hgetall(CONVERSATION_PREFIX + conversation_id)
        if data:
            return {
                "id": conversation_id,
                "title": data.get("title", ""),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "messages": json.loads(data.get("messages", "[]"))
            }
        return None
    else:
        return _memory_store.get(conversation_id)

def update_conversation(conversation_id: str, messages: list) -> bool:
    client = _get_redis_client()
    timestamp = datetime.now().isoformat()

    if client:
        conv_key = CONVERSATION_PREFIX + conversation_id
        if not client.exists(conv_key):
            return False
        client.hset(conv_key, mapping={
            "updated_at": timestamp,
            "messages": json.dumps(messages, ensure_ascii=False)
        })
        client.zadd(CONVERSATION_INDEX_KEY, {conversation_id: float(datetime.now().timestamp())})
        return True
    else:
        if conversation_id not in _memory_store:
            return False
        _memory_store[conversation_id]["messages"] = messages
        _memory_store[conversation_id]["updated_at"] = timestamp
        _memory_index[conversation_id]["updated_at"] = timestamp
        return True

def delete_conversation(conversation_id: str) -> bool:
    client = _get_redis_client()

    if client:
        conv_key = CONVERSATION_PREFIX + conversation_id
        if not client.exists(conv_key):
            return False
        client.delete(conv_key)
        client.zrem(CONVERSATION_INDEX_KEY, conversation_id)
        client.hdel(CONVERSATION_INDEX_KEY + ":titles", conversation_id)
        logger.info(f"删除对话: {conversation_id}")
        return True
    else:
        if conversation_id in _memory_store:
            del _memory_store[conversation_id]
            if conversation_id in _memory_index:
                del _memory_index[conversation_id]
            return True
        return False

def list_conversations() -> list:
    client = _get_redis_client()
    conversations = []

    if client:
        conv_ids = client.zrevrange(CONVERSATION_INDEX_KEY, 0, -1)
        titles = client.hgetall(CONVERSATION_INDEX_KEY + ":titles")
        created_times = {}

        for conv_id in conv_ids:
            data = client.hgetall(CONVERSATION_PREFIX + conv_id)
            if data:
                created_times[conv_id] = data.get("created_at", "")

        for conv_id in conv_ids:
            conversations.append({
                "id": conv_id,
                "title": titles.get(conv_id, "未命名"),
                "created_at": created_times.get(conv_id, ""),
                "updated_at": client.hget(CONVERSATION_PREFIX + conv_id, "updated_at") or ""
            })
    else:
        for conv_id, info in _memory_index.items():
            conversations.append({
                "id": conv_id,
                "title": info["title"],
                "created_at": info["created_at"],
                "updated_at": info["updated_at"]
            })
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)

    return conversations

def rename_conversation(conversation_id: str, new_title: str) -> bool:
    client = _get_redis_client()
    timestamp = datetime.now().isoformat()

    if client:
        conv_key = CONVERSATION_PREFIX + conversation_id
        if not client.exists(conv_key):
            return False
        client.hset(conv_key, "title", new_title)
        client.hset(conv_key, "updated_at", timestamp)
        client.zadd(CONVERSATION_INDEX_KEY, {conversation_id: float(datetime.now().timestamp())})
        client.hset(CONVERSATION_INDEX_KEY + ":titles", conversation_id, new_title)
        return True
    else:
        if conversation_id not in _memory_store:
            return False
        _memory_store[conversation_id]["title"] = new_title
        _memory_store[conversation_id]["updated_at"] = timestamp
        _memory_index[conversation_id]["title"] = new_title
        _memory_index[conversation_id]["updated_at"] = timestamp
        return True
