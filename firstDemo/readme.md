# firstDemo

调用 DeepSeek 大模型 API 的最小可运行示例（Python），是项目 [pythonDemo](https://github.com/shiyuejuan/pythonDemo) 的第一个示例。

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [在别的文件里调用](#在别的文件里调用)
- [响应对象怎么取值](#响应对象怎么取值)
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

> 配置文件会在「当前工作目录 → `first.py` 所在目录 → 项目根目录」中依次查找，命中即用。所以无论从哪个目录运行，只要项目里有 `.env.development` 就能读

### 3. 在别的文件里调用

`first.py` 把演示逻辑封装成了 `runDemo()`，可以直接导入使用：

```python
# 从项目根目录调用
from firstDemo.first import runDemo

answer = runDemo("什么是 API？", verbose=False)
print(answer)
```

```python
# 若调用方与 first.py 在同一目录，也可以直接
from first import runDemo
```

完整示例见 `call_demo.py`，运行：

```bash
python firstDemo/call_demo.py
```

**可用参数**

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `prompt` | `str` | `"什么是 API？"` | 用户提问 |
| `model` | `str \| None` | `None` | 模型名；不传则读环境变量 `MODEL`，再退回 `deepseek-flash` |
| `system` | `str \| None` | 简洁助手提示词 | 系统提示词；传 `None` 则只发用户消息 |
| `verbose` | `bool` | `True` | 是否打印回答与完整响应 |

**返回值**：模型回答的正文字符串（`str`），可直接交给下游处理。

模块导出的三个名字：`runDemo()`（发起对话）、`get_client()`（取客户端单例）、`load_env()`（加载配置文件）。

## 响应对象怎么取值

`runDemo(verbose=True)` 会打印完整响应。响应对象是 Pydantic 模型，有两种序列化写法：

| 写法 | 返回类型 | 说明 |
| --- | --- | --- |
| `response.model_dump_json(indent=2)` | `str` | 已是 JSON 文本，可直接 `print` 或写文件 |
| `response.model_dump()` | `dict` | 拿到的是字典，可以下标取值 |

两个容易踩的点：

- `model_dump()` 返回的是 Python 字典，`print` 出来带单引号，**不是合法 JSON**，不能直接喂给 `json.loads()`
- 想少打印一堆 `null`，加参数：`model_dump_json(indent=2, exclude_none=True)`
- `json.dumps()` 默认 `ensure_ascii=True`，中文会变成 `\uXXXX`，必须显式写 `ensure_ascii=False`

另外，DeepSeek 推理模型（如 `deepseek-flash`）会把思考过程放在独立字段里，**不在 `content` 中**：

```python
msg = response.choices[0].message
print(msg.content)             # 最终回答
print(msg.reasoning_content)   # 思考过程，按输出计费
```

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
| `SyntaxError: invalid character '，' (U+FF0C)` | 把中文标点或网页/Markdown 内容粘进了代码 | 删掉非代码内容；中文只放在 `#` 注释或引号内 |
| `ModuleNotFoundError: No module named 'openai'` | 依赖未安装 | `pip install openai python-dotenv` |
| `ModuleNotFoundError: No module named 'first'` / `'firstDemo'` | 导入路径不对 | 同目录用 `from first import runDemo`；跨目录用 `from firstDemo.first import runDemo`，并在项目根目录运行 |
| `AuthenticationError: 401` | 密钥无效或仍是占位符 | 确认 `.env.development` 已填真实密钥 |
| 余额不足类报错 | 账户余额为 0 | 到 DeepSeek 控制台充值 |
| 网络超时 / 连接失败 | 网络或代理问题 | 检查网络，必要时配置代理 |

## 安全提示

`.env` 系列文件已通过 `.gitignore` 排除。如果密钥曾经被提交或外泄，请立刻到平台后台删除该密钥并重新生成。
