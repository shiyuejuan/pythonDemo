"""在别的文件里调用 run.py 导出的 runDemo()。

运行：
    python secondDemo/index.py

导入方式说明：
    本文件与 run.py 在同一目录，可以直接 `from run import runDemo`；
    若在项目根目录或其他包里调用，改用完整路径：
        from secondDemo.run import runDemo
"""

# 只导入需要的函数；verbose=False 表示不打印完整响应，只拿返回值
from run import runDemo

# ① 最简单的用法：拿到回答正文
answer = runDemo("用一句话说明什么是 REST API", verbose=False)
print("runDemo() 的返回值 →", answer)

# ② 换个模型、换系统提示词
answer2 = runDemo(
    "用一句话说明什么是环境变量",
    model="deepseek-flash",
    system="你是一名严谨的老师，只回答一句话。",
    verbose=False,
)
print("换系统提示词后 →", answer2)

# ③ 只要返回值，不打印响应 —— 适合把结果继续交给下游处理
for question in ("什么是 JSON？", "什么是 HTTP 状态码？"):
    result = runDemo(question, verbose=False)
    print(f"\n问：{question}\n答：{result}")
