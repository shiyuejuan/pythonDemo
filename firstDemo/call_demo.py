"""在别的文件里调用 first.py 导出的 runDemo()。

运行：
    python firstDemo/call_demo.py

导入方式说明：
    本文件与 first.py 在同一目录，可以直接 `from first import runDemo`；
    若在项目根目录或其他包里调用，改用完整路径：
        from firstDemo.first import runDemo
"""

# 只导入需要的函数；verbose=False 表示不打印完整响应，只拿返回值
from first import runDemo

# ① 最简单的用法：拿到回答正文
answer = runDemo("用一句话说明什么是 REST API", verbose=False)
print("runDemo() 的返回值 →", answer)

# ② 换系统提示词
answer2 = runDemo(
    "用一句话说明什么是环境变量",
    system="你是一名严谨的老师，只回答一句话。",
    verbose=False,
)
print("换系统提示词后 →", answer2)

# ③ 批量提问 —— 返回值可以直接交给下游处理
for question in ("什么是 JSON？", "什么是 HTTP 状态码？"):
    print(f"问：{question}")
    print(f"答：{runDemo(question, verbose=False)}\n")
