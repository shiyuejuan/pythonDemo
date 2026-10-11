# pythonDemo

调用 DeepSeek 大模型 API 的最小可运行示例（Python）。用最少的代码走通「读取密钥 → 发起对话 → 打印结果」的完整流程。

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
  - [1. 安装依赖](#1-安装依赖)
  - [2. 配置密钥](#2-配置密钥)
  - [3. 运行](#3-运行)
- [项目结构](#项目结构)
- [接口说明](#接口说明)
- [安全提示](#安全提示)

## 环境要求

| 项目 | 要求 |
| --- | --- |
| Python | 3.8 及以上 |
| 依赖 | `openai`（DeepSeek 兼容 OpenAI 接口，故复用该 SDK）、`python-dotenv` |

> DeepSeek 官方接口与 OpenAI SDK 兼容，因此代码中 `import openai` 即可直接调用，只需把 `base_url` 指向 DeepSeek。

## 快速开始

### 1. 安装依赖

```bash
pip install openai python-dotenv
```

### 2. 配置密钥

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

> 脚本会按 `APP_ENV` 的值加载对应的环境文件，例如 `APP_ENV=development` 读取 `.env.development`，`APP_ENV=test` 读取 `.env.test`。

### 3. 运行

在**项目根目录**执行：

```bash
python firstDemo/first.py
```

脚本会读取 `DEEPSEEK_API_KEY`，向 DeepSeek 发起一次对话请求，并打印回答内容与完整响应。

想在**别的文件里调用**，导入封装好的函数即可：

```python
from firstDemo.first import runDemo

answer = runDemo("什么是 API？", verbose=False)
```

运行现成的调用示例：`python firstDemo/call_demo.py`。详细参数见 `firstDemo/readme.md`。

> 配置文件会在「当前工作目录 → `first.py` 所在目录 → 项目根目录」中依次查找，所以从哪个目录运行都能读到 `.env.development`。

## 项目结构

```text
pythonDemo/
├── firstDemo/
│   ├── first.py          # 主程序：封装 runDemo()，可直接运行也可被导入
│   ├── call_demo.py      # 调用示例：演示如何导入并调用 runDemo()
│   └── readme.md         # 该目录的说明
├── .env.example          # 环境变量模板（可提交）
├── .env.development      # 真实密钥（已被忽略，禁止提交）
├── .gitignore            # 忽略规则
├── check-secrets.sh      # 密钥泄露自检脚本
└── README.md
```

## 接口说明

| 参数 | 值 |
| --- | --- |
| `base_url` | `https://api.deepseek.com`（兼容写法：`https://api.deepseek.com/v1`） |
| `model` | `deepseek-flash` 或 `deepseek-v4-pro` |
| 接口路径 | `/chat/completions` |
| 认证方式 | 请求头携带 `Authorization: Bearer <DEEPSEEK_API_KEY>` |

> `base_url` 里的 `/v1` 只是为兼容 OpenAI SDK 而保留的路径写法，与模型版本无关，加或不加都会请求到 `https://api.deepseek.com/chat/completions`。

## 安全提示

`.env` 系列文件已通过 `.gitignore` 排除。如果密钥曾经被提交或外泄，请立刻到平台后台删除该密钥并重新生成。

为防忽略规则被误改，本项目额外加了三层保护：

| 保护层 | 位置 | 作用 |
| --- | --- | --- |
| 仓库内忽略规则 | `.gitignore` | 常规忽略，会随仓库一起提交 |
| 本地备份忽略规则 | `.git/info/exclude` | 存在 `.git` 内，即使 `.gitignore` 被误改名也仍然生效 |
| 提交前钩子 | `.git/hooks/pre-commit` | 暂存区出现 `.env*` 文件或疑似真实密钥时直接阻止提交 |

提交前想自查，运行：

```bash
./check-secrets.sh
```

脚本会检查 `.gitignore` 文件名是否正常、密钥文件是否真被忽略、已跟踪文件中是否有漏网密钥、暂存区是否干净。

> **常见的坑**：`.gitignore` 一旦被改名（例如变成名字前带空格的 ` .gitignore`），Git 就不会读取它，**所有忽略规则会同时失效**。用 `ls -b | grep gitignore` 可以一眼看出文件名是否异常。
