"""多轮对话示例：在别的文件里调用 run.py 导出的 runDemo()。

运行（在本目录内）：
    python index.py

导入方式说明：
    本文件与 run.py 在同一目录，可以直接 `from run import runDemo`。
    注意：本目录名含连字符（multi-turnConversation），不是合法的 Python 包名，
    所以无法写 `from multi-turnConversation.run import runDemo` 从项目根导入；
    确实需要跨目录调用时，用 importlib 按文件路径加载，或把目录改成下划线风格。
"""

# 只导入需要的函数；verbose=False 表示不打印完整响应，只拿返回值
from run import runDemo

# 对话历史：第一条 system 消息设定人设，之后每轮追加 user / assistant
history = [
    {"role": "system", "content": "你是一个简洁的助手，回答不超过两句话。"},
]


def chat(user_input: str) -> str:
    history.append({"role": "user", "content": user_input})

    reply = runDemo(prompt=user_input, messages=history, verbose=False)

    # 关键：把模型的回复也塞回历史，否则模型下一轮就"失忆"
    history.append({"role": "assistant", "content": reply})

    return reply


# ① 最简单的用法：拿到回答正文
# reply = chat("什么是 JSON？")
# print("runDemo() 的返回值 →", reply)

# ② 多轮提问：同一个 history 一直追加，模型记得前面说过什么
for question in ("什么是 JSON？", "什么是 HTTP 状态码？"):
    result = chat(question)
    print(f"\n问：{question}\n答：{result}")
