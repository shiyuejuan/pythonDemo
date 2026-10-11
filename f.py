import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI as DeepSeekClient


env = os.getenv("APP_ENV", "development")
env_file = Path(f".env.{env}")

if env_file.exists():
    load_dotenv(env_file)

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit(
        f"未找到 API 密钥（环境：{env}）。请检查 {env_file} 是否存在。"
    )

# DeepSeekClient 会自动读取 DEEPSEEK_API_KEY
client = DeepSeekClient(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个简洁的助手，回答不超过两句话。"},
        {"role": "user", "content": "什么是 API？"},
    ],
)

print(response.choices[0].message.content)
print(response.model_dump_json(indent=2))