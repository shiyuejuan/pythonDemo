"""调用 DeepSeek 大模型 API 的最小可运行示例（可被其他文件导入）。

直接运行：
    python firstDemo/first.py

在别的文件里调用：
    from firstDemo.first import runDemo
    answer = runDemo("什么是 API？")

    # 若调用方与 first.py 在同一目录，也可以直接：
    # from first import runDemo
"""

import os
#导入路径对象 Path，方便构造文件名并检查文件是否存在。
from pathlib import Path
#导入第三方 python-dotenv 包中的 load_dotenv；需先安装 python-dotenv。
from dotenv import load_dotenv
from openai import OpenAI as DeepSeekClient

# 显式声明本模块对外导出的名字（用 from xxx import * 时只会导入这些）
__all__ = ["runDemo", "get_client", "load_env"]

BASE_URL = "https://api.deepseek.com"
DEFAULT_SYSTEM_PROMPT = "你是一个简洁的助手，回答不超过两句话。"

# 客户端做进程内缓存，避免每次调用都重新创建
_client = None


def load_env():
    """按 APP_ENV 找到并加载对应的 .env 文件。

    依次在「当前工作目录 → first.py 所在目录 → 项目根目录」中查找，先命中先用。
    返回实际加载的文件路径；三个位置都没有则返回 None。
    """
    #读取 APP_ENV；如果未设置，默认使用 development。如果 APP_ENV 存在但值为空字符串，不会使用默认值。
    env = os.getenv("APP_ENV", "development")
    #拼出对应的 .env 文件名，如 .env.development 或 .env.test
    name = f".env.{env}"

    # 这里依次尝试三个位置，而不是只用相对路径，
    # 这样无论从哪个目录运行或导入，都能找到配置文件。
    here = Path(__file__).resolve().parent
    for candidate in (Path.cwd() / name, here / name, here.parent / name):
        if candidate.exists():
            # load_dotenv 默认 override=False，不会覆盖进程中已存在的同名变量
            load_dotenv(candidate)
            return candidate
    return None


def get_client():
    """返回 DeepSeek 客户端（进程内单例，自动读取 DEEPSEEK_API_KEY）。"""
    global _client
    if _client is None:
        env = os.getenv("APP_ENV", "development")
        env_file = load_env() or Path(f".env.{env}")
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise SystemExit(
                f"未找到 API 密钥（环境：{env}）。请检查 {env_file} 是否存在。"
            )
        # DeepSeekClient 会自动读取 DEEPSEEK_API_KEY，这里显式传入更直观
        _client = DeepSeekClient(api_key=api_key, base_url=BASE_URL)
    return _client


def runDemo(prompt="什么是 API？", model=None, system=DEFAULT_SYSTEM_PROMPT, verbose=True):
    """发起一次对话，并把回答正文返回给调用方。

    prompt  ：用户提问，默认「什么是 API？」
    model   ：模型名；不传则读环境变量 MODEL，再退回 deepseek-flash
    system  ：系统提示词；传 None 则只发用户消息
    verbose ：是否打印回答与完整响应
    返回    ：模型回答的正文（str）
    """
    # 模型名优先级：函数参数 > 环境变量 MODEL > 默认值 deepseek-flash
    model = model or os.getenv("MODEL") or "deepseek-flash"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = get_client().chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content or ""

    if verbose:
        print(answer)
        # 两种序列化写法的区别：
        #   model_dump()          -> dict，程序内取字段、改值
        #   model_dump_json(...)  -> str，直接打印或写文件
        # exclude_none=True 去掉值为 null 的字段，输出更短
        print(response.model_dump_json(indent=2, exclude_none=True))

    return answer


if __name__ == "__main__":
    # 直接运行本文件时，执行一次默认演示
    runDemo()
