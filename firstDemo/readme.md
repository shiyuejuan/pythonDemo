# firstDemo

调用 DeepSeek 大模型 API 的最小可运行示例（Python），是项目 [pythonDemo](https://github.com/shiyuejuan/pythonDemo) 的第一个示例。

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [接口说明](#接口说明)
- [运行报错对照](#运行报错对照)

## 环境要求

| 项目 | 要求 |
| --- | --- |
| Python | 3.8 及以上 |
| 依赖 | `openai`（DeepSeek 兼容 OpenAI 接口，故复用该 SDK）、`python-dotenv` |

```bash
pip install openai python-dotenv
```

## 快速开始

### 1. 配置密钥

不要直接修改或提交 `.env.development`。正确做法是复制模板，再填入自己的密钥：

```bash
cp .env.example .env.development
```

编辑 `.env.development`：

```env
APP_ENV=development
DEEPSEEK_API_KEY=sk-你的密钥
MODEL=deepseek-flash
```

密钥申请地址：<https://platform.deepseek.com/api_keys>

### 2. 运行

在**项目根目录**执行：

```bash
python firstDemo/first.py
```

脚本会按 `APP_ENV` 加载对应环境文件（如 `.env.development`），读取 `DEEPSEEK_API_KEY`，向 DeepSeek 发起一次对话请求并打印结果。

> ⚠️ 环境文件是相对**当前工作目录**查找的。若在 `firstDemo/` 目录内直接运行 `python first.py`，需要把 `.env.development` 也复制到这个目录。

## 接口说明

| 参数 | 值 |
| --- | --- |
| `base_url` | `https://api.deepseek.com`（兼容写法：`https://api.deepseek.com/v1`） |
| `model` | `deepseek-flash` 或 `deepseek-v4-pro` |
| 接口路径 | `/chat/completions` |

## 运行报错对照

| 报错 | 原因 | 处理 |
| --- | --- | --- |
| `IndentationError` | 代码粘贴时顶层语句带了缩进 | 检查 `import` 等语句是否顶格 |
| `ModuleNotFoundError: No module named 'openai'` | 依赖未安装 | `pip install openai python-dotenv` |
| `AuthenticationError: 401` | 密钥无效或仍是占位符 | 确认 `.env.development` 已填真实密钥 |
| 余额不足类报错 | 账户余额为 0 | 到 DeepSeek 控制台充值 |
| 网络超时 / 连接失败 | 网络或代理问题 | 检查网络，必要时配置代理 |

## 安全提示

`.env` 系列文件已通过 `.gitignore` 排除。如果密钥曾经被提交或外泄，请立刻到平台后台删除该密钥并重新生成。
