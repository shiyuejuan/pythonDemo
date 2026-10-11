"""策略二：摘要压缩（省 token，且不丢早期信息）。

模型有上下文窗口上限（如 128K token），历史越长消耗越多、超出会直接报错。
本示例把「最近 KEEP_RECENT 条对话」原文保留，更早的内容调用一次模型压成
一段要点摘要，替换掉原文后再发给主模型——既缩了长度，又保住了关键事实。

运行（在本目录内）：
    python index.py

导入方式说明：
    本文件与 run.py 在同一目录，可以直接 `from run import runDemo`。
    本目录名含连字符（contextLengthExceeded2），不是合法的 Python 包名，
    所以无法从项目根写 `from contextLengthExceeded2.run import runDemo`。

详细思路见同目录 readme.md。
"""

import os

# get_client：压缩历史那一次额外调用要用；runDemo：正常对话用
from run import get_client, runDemo

# 对话历史：第一条 system 消息设定人设，之后每轮追加 user / assistant
history = [
    {"role": "system", "content": "你是一个简洁的助手，回答不超过两句话。"},
]

# 原文保留的最近对话条数：1 轮 = user + assistant 两条，6 条 = 3 轮。
# 建议取偶数，才能和「轮」的边界对齐；奇数虽然也能跑，但窗口切点容易落在
# assistant 上（下面用 while 循环兜住）。
KEEP_RECENT = 6

# 摘要消息的标记，用来区分「这条 system 是人设」还是「这条 system 是旧摘要」
SUMMARY_PREFIX = "【此前对话摘要】"

# 调试用：记录最后一次真正发给模型的消息列表
last_messages = []


def summarize(text: str) -> str:
    """把一段对话文本压成要点摘要（一次独立的模型调用）。

    单独抽成函数有两个好处：职责单一；写测试时可以把它替换成假实现，
    免得每次验证逻辑都要花一次真实 API 调用。
    """
    model = os.getenv("MODEL") or "deepseek-flash"

    # 为什么这里只发一条 user 消息、没有 system：
    #   system 是可选的人设层（设定层），本次只是一次性文本转换任务，没有需要
    #   跨轮维持的人设，所以用不上。真正必须的是 messages 不能为空，
    #   另外不要把「指令」和「正文」拆到两条消息里——实测那样模型会把正文
    #   当成一个独立提问直接回答，反而不做摘要。
    resp = get_client().chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "把以下对话压缩成一段要点摘要，保留关键事实"
                "（人名、数字、已确认的结论）：\n\n" + text,
            }
        ],
    )

    # content 可能是 None（响应被过滤等情况），None 没有 strip 方法会直接报错，
    # 所以先用 or "" 兜底；strip() 负责去掉首尾空白（含换行、制表符），
    # 内部换行不受影响，模型的返回常带首尾多余换行，剪掉更干净。
    return (resp.choices[0].message.content or "").strip()


def summarize_old_messages(history, keep_recent=KEEP_RECENT):
    """保留人设 + 最近 keep_recent 条原文，更早的对话折叠成一条摘要 system 消息。

    返回一份可以直接发给模型的新列表；history 本身不动（仍保留完整记录）。
    """
    # 第一步：拆成「人设」「旧摘要」「对话」三部分。
    # 用 role 过滤，而不是写死 history[0] / history[1:] 这种下标——
    # 摘要消息一旦生成，它也是 system 角色，按下标取就会把它当成对话内容。
    #
    # 列表推导式等价于「先建空列表 → 逐个遍历 → 条件成立就追加」：
    #     persona = []
    #     for m in history:
    #         if m["role"] == "system" and not m["content"].startswith(SUMMARY_PREFIX):
    #             persona.append(m)
    #
    # 两个条件用 and 连接，左边的 role 判断先执行：左边为假时右边不再求值
    # （短路），所以 content 为 None 的对话消息不会引发 AttributeError。
    # 第二道筛子 not m["content"].startswith(SUMMARY_PREFIX)：startswith 返回
    # True/False，加 not 取反，意思是「这条内容不以『【此前对话摘要】』开头」，
    # 摘要消息由此被排除。残留风险：system 消息的 content 若为 None 仍会抛
    # AttributeError，要彻底防住可写成 not (m.get("content") or "").startswith(...)。
    persona = [
        m
        for m in history
        if m["role"] == "system" and not m["content"].startswith(SUMMARY_PREFIX)
    ]
    old_summaries = [
        m
        for m in history
        if m["role"] == "system" and m["content"].startswith(SUMMARY_PREFIX)
    ]
    dialog = [m for m in history if m["role"] != "system"]

    # 第二步：判断该不该压。这里比的是「对话条数」，不是 len(history)。
    # len(history) 里还躺着人设和旧摘要，如果写成 keep_recent + 1 这种魔数，
    # 摘要消息一出现（它也是 system），这个 1 就再也对不上了。
    if len(dialog) <= keep_recent:
        return history

    # 第三步：切窗口，并且保证窗口从 user 开始。
    # 直接切可能落在 assistant 上（比如 keep_recent 是奇数、或中途某轮报错
    # 导致消息没严格交替），有些模型遇到「首条是 assistant」会直接报 400。
    # 往后挪一条而不是丢掉首条，可以保住「问 + 答」成对。
    #
    # 这里用的是切片 s[start:stop:step]，规则是「含头不含尾」：
    #     省略即默认 —— s[:n] 前 n 个字符；s[n:] 从第 n 个到末尾；s[:] 完整复制
    #     dialog[:start] 取到 start 之前，dialog[start:] 从 start 取到末尾
    #     s[::-1] 是反转字符串的标准写法；step 为负时 start/stop 默认值自动对调
    #     空切片不报错：s[2:2]、s[4:2] 都返回 ''，不会抛异常
    start = max(0, len(dialog) - keep_recent)
    while start < len(dialog) and dialog[start]["role"] != "user":
        start += 1
    old, recent = dialog[:start], dialog[start:]

    # 第四步：滚动摘要——把「上一次的摘要」和「这次过期的原文」一起重新压一遍。
    # 必须带上旧摘要：如果只压 old、把上一条摘要丢掉，早期信息会从第二次压缩起
    # 永久消失。合并重压之后，摘要永远只有一条，不会越滚越多。
    pieces = [m["content"] for m in old_summaries]
    pieces += [f"{m['role']}: {m['content']}" for m in old]
    new_summary = summarize("\n".join(pieces))

    return (
        persona
        + [{"role": "system", "content": SUMMARY_PREFIX + new_summary}]
        + recent
    )


def chat(user_input: str, keep_recent: int = KEEP_RECENT) -> str:
    """追加一轮提问，返回回答正文。"""
    global last_messages

    history.append({"role": "user", "content": user_input})

    # 只把「压缩后的窗口」发给模型；history 本身保留完整记录，方便以后换策略
    history_new = summarize_old_messages(history, keep_recent=keep_recent)
    last_messages = history_new

    # 注意：messages 非 None 时 runDemo 内部会忽略 prompt，
    # 这里继续传 prompt 只是为了让单独调用 runDemo 的人知道本轮问题是什么
    reply = runDemo(prompt=user_input, messages=history_new, verbose=False)

    # 关键：把模型的回复也塞回历史，否则模型下一轮就"失忆"
    history.append({"role": "assistant", "content": reply})

    return reply


if __name__ == "__main__":
    # ① 最简单的用法：拿到回答正文
    # reply = chat("什么是 JSON？")
    # print("runDemo() 的返回值 →", reply)

    # ② 多轮提问：同一个 history 一直追加，模型记得前面说过什么
    for question in (
        "什么是 JSON？",
        "什么是 HTTP 状态码？",
        "什么是 REST？",
        "什么是 WebSocket？",
    ):
        result = chat(question)
        print(f"\n问：{question}\n答：{result}")

    # ③ 看压缩效果：最后一次真正发给模型的消息结构
    print(f"\n=== 最后一次发给模型的消息（共 {len(last_messages)} 条）===")
    for m in last_messages:
        content = m["content"].replace("\n", " ")
        print(f"[{m['role']:>9}] {content[:46]}{'…' if len(content) > 46 else ''}")
