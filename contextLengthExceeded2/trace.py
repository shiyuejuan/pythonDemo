"""逐行追踪：把 summarize_old_messages() 每一步的中间取值打印出来。

用途：配合 readme.md 看「第一次调用不压缩」和「第一次触发摘要压缩」这两轮
到底发生了什么。summarize() 被替换成假实现，输出确定、不消耗 API。

运行（在本目录内）：
    python trace.py
"""

import index
from index import KEEP_RECENT, SUMMARY_PREFIX

# ---- 把真实 API 调用换成假实现，便于看清输入输出 ----
SUMMARY_CALLS = []
VERIFYING = False          # 一致性校验期间的重复调用不计入统计


def fake_summarize(text: str) -> str:
    """确定性假摘要：按行数生成，便于对照；同时记录每次的输入，用于末尾统计。"""
    if not VERIFYING:
        SUMMARY_CALLS.append(text)
    n = len(text.split("\n"))
    with_old = "旧摘要+原文" if text.startswith(SUMMARY_PREFIX) else "纯原文"
    return f"<摘要：压缩了 {n} 行{with_old}>"


index.summarize = fake_summarize


def show(tag, value):
    print(f"  {tag:<24} {value!r}")


def trace_round(user_input: str, keep_recent: int = KEEP_RECENT):
    """追踪一轮，返回 (发给 runDemo 的条数, 送进摘要的 old 条数)。"""
    global VERIFYING
    history = index.history
    history.append({"role": "user", "content": user_input})

    print()
    print("=" * 76)
    print(f"chat({user_input!r})   ← 第 1 行已执行：history.append(本轮提问)")
    print("=" * 76)
    show("len(history)", len(history))
    show("history", [(m["role"], m["content"][:14]) for m in history])

    # ---------- 第一步 ----------
    persona = [
        m for m in history
        if m["role"] == "system" and not m["content"].startswith(SUMMARY_PREFIX)
    ]
    old_summaries = [
        m for m in history
        if m["role"] == "system" and m["content"].startswith(SUMMARY_PREFIX)
    ]
    dialog = [m for m in history if m["role"] != "system"]
    print("  ── 第一步：按 role 拆三段 ──")
    show("persona", [m["content"][:20] for m in persona])
    show("old_summaries", [m["content"][:20] for m in old_summaries])
    show("dialog", [f"{m['role'][0]}:{m['content'][:8]}" for m in dialog])

    # ---------- 第二步 ----------
    hit = len(dialog) <= keep_recent
    print("  ── 第二步：阈值判断 ──")
    show("len(dialog)", len(dialog))
    show("keep_recent", keep_recent)
    show("len(dialog) <= keep", f"{len(dialog)} <= {keep_recent} → {hit}")
    if hit:
        print("  >>> 命中提前 return history：不压缩、不调用模型")
        print(f"  发给 runDemo 的条数：{len(history)}")
        return len(history), 0

    print("  >>> 超过阈值，进入压缩分支")
    # ---------- 第三步 ----------
    start = max(0, len(dialog) - keep_recent)
    print("  ── 第三步：切窗口 + 对齐 user 边界 ──")
    show("start 初值", start)
    moved = False
    while start < len(dialog) and dialog[start]["role"] != "user":
        print(f"     dialog[{start}] 是 {dialog[start]['role']} → start 挪到 {start + 1}")
        start += 1
        moved = True
    if not moved:
        print(f"     dialog[{start}] 已经是 user → 不挪")
    old, recent = dialog[:start], dialog[start:]
    show("old（要进摘要）", [f"{m['role'][0]}:{m['content'][:8]}" for m in old])
    show("recent（原文保留）", [f"{m['role'][0]}:{m['content'][:8]}" for m in recent])

    # ---------- 第四步 ----------
    pieces = [m["content"] for m in old_summaries]
    pieces += [f"{m['role']}: {m['content']}" for m in old]
    print("  ── 第四步：拼出待压缩文本并调用 summarize() ──")
    show("pieces 行数", len(pieces))
    for i, p in enumerate(pieces):
        print(f"     pieces[{i}] = {p[:58]!r}")
    new_summary = index.summarize("\n".join(pieces))
    show("summarize() 返回", new_summary)

    result = (
        persona
        + [{"role": "system", "content": SUMMARY_PREFIX + new_summary}]
        + recent
    )
    print("  ── 返回值 ──")
    show("新摘要消息", SUMMARY_PREFIX + new_summary)
    show("返回条数", len(result))
    show("返回结构", [f"{m['role'][0]}:{m['content'][:10]}" for m in result])

    # 交叉校验：追踪复刻的表达式与真实函数结果必须一致
    VERIFYING = True
    assert index.summarize_old_messages(history, keep_recent) == result
    VERIFYING = False
    print("  [校验] 追踪结果 == 真实函数返回值 ✓")
    return len(result), len(old)


def main() -> None:
    print("KEEP_RECENT =", KEEP_RECENT, "| SUMMARY_PREFIX =", SUMMARY_PREFIX)
    print("阈值：dialog 条数 <= 6 时不压缩；第 4 轮 dialog=7 时首次触发")

    questions = [
        "什么是 JSON？",
        "什么是 HTTP 状态码？",
        "什么是 REST？",
        "什么是 WebSocket？",
        "什么是 RESTful API？",
    ]
    rows = []
    for q in questions:
        sent, old_len = trace_round(q)
        rows.append((old_len, sent))
        index.history.append({"role": "assistant", "content": f"（{q} 的回答）"})

    print()
    print("=" * 76)
    print("摘要调用统计（重点看 old 列：它逐轮 +2，也就是每次都在重压全部过期原文）")
    print("=" * 76)
    print("轮次 | 送进 summarize 的行数 | 发给 runDemo 的条数")
    for i, (old_len, sent) in enumerate(rows, 1):
        print(f"{i:>3}  | {old_len:>20}  | {sent:>18}")
    print(f"\nsummarize() 总计被调用 {len(SUMMARY_CALLS)} 次")
    print("old_summaries 全程为空：摘要消息不会写回 history（chat 只 append user/assistant）")


if __name__ == "__main__":
    main()
