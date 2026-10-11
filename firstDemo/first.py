import os
#导入路径对象 Path，方便构造文件名并检查文件是否存在。
from pathlib import Path
#导入第三方 python-dotenv 包中的 load_dotenv；需先安装 python-dotenv。
from dotenv import load_dotenv
from openai import OpenAI as DeepSeekClient

#读取 APP_ENV；如果未设置，默认使用 development。如果 APP_ENV 存在但值为空字符串，不会使用默认值。
env = os.getenv("APP_ENV", "development")
#拼出对应的 .env 文件名，如 .env.development 或 .env.test。这里用相对路径，解析位置是运行进程的当前工作目录，不一定是脚本目录。
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
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": "你是一个简洁的助手，回答不超过两句话。"},
        {"role": "user", "content": "什么是 API？"},
    ],
)

print(response.choices[0].message.content)
"""
写法	返回类型	说明
response.model_dump_json(indent=2)	str	已是 JSON 文本，直接 print 或写文件
response.model_dump()	dict	拿到的是字典，可以下标取值
"""
print(response.model_dump_json(indent=2))