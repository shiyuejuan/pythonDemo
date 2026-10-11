"""DeepSeek API 调用示例：把逻辑封装成 runDemo()，供别的文件导入调用。

直接运行本文件：
    python run.py

在别的文件里调用：
    from run import runDemo              # 调用方与本文件在同一目录

注意：本目录名含连字符（multi-turnConversation），不是合法的 Python 包名，
无法用 `from multi-turnConversation.run import runDemo` 从项目根导入；
需要跨目录调用时，用 importlib 按文件路径加载，或把目录改成下划线风格。
"""

import os
#导入路径对象 Path，方便构造文件名并检查文件是否存在。
from pathlib import Path
#导入第三方 python-dotenv 包中的 load_dotenv；需先安装 python-dotenv。
from dotenv import load_dotenv
from openai import OpenAI as DeepSeekClient

# 显式声明对外导出的名字
__all__ = ["runDemo", "get_client", "load_env"]

BASE_URL = "https://api.deepseek.com"


# 客户端缓存，避免每次调用都重新创建
_client = None


def load_env():
    """按 APP_ENV 找到并加载对应的 .env 文件，返回文件路径或 None。"""
    #读取 APP_ENV；如果未设置，默认使用 development。如果 APP_ENV 存在但值为空字符串，不会使用默认值。
    env = os.getenv("APP_ENV", "development")
    #拼出对应的 .env 文件名，如 .env.development 或 .env.test
    name = f".env.{env}"

    # 依次尝试：当前工作目录 → 本文件所在目录 → 项目根目录
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
        # 注意：Path(f".env.{env}") 这类相对路径的解析基准是"当前工作目录（CWD）"，
        # 不是本文件所在的位置；所以优先用 load_env() 按 CWD → 脚本目录 → 项目根查找。
        env_file = load_env() or Path(f".env.{env}")
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise SystemExit(
                f"未找到 API 密钥（环境：{env}）。请检查 {env_file} 是否存在。"
            )
        _client = DeepSeekClient(api_key=api_key, base_url=BASE_URL)
    return _client


def runDemo(prompt="什么是 API？", model=None, messages=None, system=None, verbose=True):
    """发起一次对话，返回回答正文；verbose=False 时只返回不打印。

    两种用法：
        单轮：只传 prompt（可加 system 设定人设）；
        多轮：传完整 messages 列表（含对话历史），此时 prompt 被忽略。
    """
    model = model or os.getenv("MODEL") or "deepseek-flash"

    if messages is None:
        msgs = [{"role": "user", "content": prompt}]
        if system:
            msgs.insert(0, {"role": "system", "content": system})
    else:
        msgs = messages

    

    response = get_client().chat.completions.create(model=model, messages=msgs)
    answer = response.choices[0].message.content or ""

    if verbose:
        print(answer)
        print(response.model_dump_json(indent=2, exclude_none=True))

    return answer


if __name__ == "__main__":
    # 只有 python run.py 时才会走到这里
    # 被 import 时整块跳过
    runDemo()
