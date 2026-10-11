##pythonDemo
调用 DeepSeek 大模型 API 的最小可运行示例（Python）。
环境要求
- Python 3.8+
- 依赖：openai（DeepSeek 兼容 OpenAI 接口，因此复用该 SDK）、python-dotenv
pip install openai python-dotenv
##配置密钥
不要修改或提交 .env.development，正确做法是复制模板后填入自己的密钥：
cp .env.example .env.development
编辑 .env.development：
APP_ENV=development
DEEPSEEK_API_KEY=sk-你的密钥
MODEL=deepseek-flash
密钥申请地址：https://platform.deepseek.com/api_keys
运行
python first.py
脚本会按 APP_ENV 加载对应环境文件（如 .env.development），读取 DEEPSEEK_API_KEY，向 DeepSeek 发起一次对话请求并打印结果。
接口说明
参数
值
base_url
https://api.deepseek.com（兼容写法 https://api.deepseek.com/v1）
model
deepseek-flash 或 deepseek-v4-pro
接口路径
/chat/completions
安全提示
.env 系列文件已通过 .gitignore 排除。如果密钥曾经被提交或外泄，请立刻到平台后台删除该密钥并重新生成。