"""策略一：滑动窗口（最简单的上下文控制）。

模型有上下文窗口上限（如 128K token），历史越长消耗越多、超出会直接报错。
本示例只把「system 人设 + 最近 MAX_TURNS 轮对话」发给模型，
更早的消息在发送时被裁掉，但本地 history 仍然保留完整记录。

运行（在本目录内）：
    python index.py

导入方式说明：
    本文件与 run.py 在同一目录，可以直接 `from run import runDemo`。
    本目录名含连字符（contextLengthExceeded），不是合法的 Python 包名，
    所以无法从项目根写 `from contextLengthExceeded.run import runDemo`。
"""

# 只导入需要的函数；verbose=False 表示不打印完整响应，只拿返回值
from run import runDemo

# 对话历史：第一条 system 消息设定人设，之后每轮追加 user / assistant
history = [
    {"role": "system", "content": "你是一个简洁的助手，回答不超过两句话。"},
]

MAX_TURNS = 20


def trim_history(history, max_turns=MAX_TURNS):
    """保留 system 消息 + 最近 max_turns 轮对话，返回一份可直接发给模型的新列表。"""
    # 第一步：挑出所有人设消息（list comprehension）。
    # 等价于下面这段循环：
    #     system_msgs = []
    #     for m in history:
    #         if m["role"] == "system":
    #             system_msgs.append(m)
    # 本示例里 history[0] 就是那条 system 消息，所以结果是长度为 1 的列表：
    #     [{"role": "system", "content": "你是一个简洁的助手……"}]
    system_msgs = [m for m in history if m["role"] == "system"]

    # 第二步：剩下的都是 user / assistant 对话，去掉人设后单独成列
    dialog = [m for m in history if m["role"] != "system"]

    # 第三步：只取最近 max_turns 轮，一轮 = 一条 user + 一条 assistant，所以要乘 2。
    #
    #     window = dialog[-max_turns * 2:] if max_turns > 0 else []
    #
    # 等价于：
    #     if max_turns > 0:
    #         window = dialog[-max_turns * 2:]
    #     else:
    #         window = []
    #
    # 为什么必须判断 max_turns > 0：
    #     max_turns = 0 时 -0 就是 0，dialog[0:] 会从头取到尾、返回全部历史，
    #     与「什么都不带」的意图完全相反。
    #     三元表达式只对选中的那一侧求值，所以 > 0 为假时切片根本不会执行，
    #     这也是它能避开 -0 陷阱的根本原因。
    #
    # 运算顺序提示：一元负号优先级高于乘法，-max_turns * 2 == (-max_turns) * 2，
    #     两者数学结果相同；但 ** 优先级更高，-3 ** 2 是 -9 而不是 9。
    window = dialog[-max_turns * 2:] if max_turns > 0 else []

    # 第四步：兜底——万一窗口第一条不是 user，丢掉它，避免以 assistant 开场被 API 拒绝
    if window and window[0]["role"] != "user":
        window = window[1:]

    # 第五步：把 system 消息拼回最前面。
    #     列表相加是「浅拷贝 + 拼接」，返回新列表，system_msgs / dialog 本身都不变：
    #         a + b = [{'role': 'user'}, {'role': 'user2'}]
    #         (a + b) is a  → False（是新列表）
    #         改 (a + b)[0]['role'] 后 a 也变了（内层 dict 是同一份引用）
    return system_msgs + window


def chat(user_input: str) -> str:
    history.append({"role": "user", "content": user_input})

    # 只把裁剪后的窗口发给模型；history 本身保留完整记录，方便以后换策略
    history_new = trim_history(history, max_turns=MAX_TURNS)
    reply = runDemo(prompt=user_input, messages=history_new, verbose=False)

    # 关键：把模型的回复也塞回历史，否则模型下一轮就"失忆"
    history.append({"role": "assistant", "content": reply})

    return reply


if __name__ == "__main__":
    # ① 最简单的用法：拿到回答正文
    # reply = chat("什么是 JSON？")
    # print("runDemo() 的返回值 →", reply)

    # ② 多轮提问：同一个 history 一直追加，模型记得前面说过什么
    for question in ("什么是 JSON？", "什么是 HTTP 状态码？"):
        result = chat(question)
        print(f"\n问：{question}\n答：{result}")
