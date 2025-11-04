# AI 音乐推荐 Agent（KB + LLM）

一个基于知识库 + 大模型（LangChain Agent）的音乐推荐原型：
- 前端：简单网页输入自然语言
- 后端：Flask + LangChain Agent（优先查 JSON 知识库的 Tool，不足时由模型生成补全）

## 目录结构

```
backend/
  main.py              # Flask 入口（/api/health, /api/recommend）
  agent_core.py        # LangChain Agent（create_openai_functions_agent + Tool）
  kb.py                # JSON 知识库检索/打分与 Tool 适配
  llm.py               # （保留）直连 SDK 版本，当前路由已改用 Agent
  knowledge_base.json  # JSON 知识库示例
frontend/
  index.html           # 简单前端页面
requirements.txt       # 依赖
.env.example           # 环境变量示例（可选）
```

## 快速开始

1) 安装依赖（建议 Python 3.10+）

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2) （可选）配置 OpenAI Key，用于 LLM 回退

复制 `.env.example` 为 `.env` 并设置：

```
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

未配置 Key 时，系统会使用可复现的本地 Mock 返回。

3) 启动后端（Flask）

```bash
python -m backend.main
```

访问健康检查：`http://localhost:8000/api/health`

4) 打开前端

直接用浏览器打开 `frontend/index.html`，或用任意静态服务器托管。

## API

- POST `/api/recommend`
  - 请求体：`{ query: string, top_k?: number }`
  - 返回：`{ query, recommendations: Array<...>, meta: { strategy } }`
  - 策略：`langchain_agent`

## 自定义知识库

编辑 `backend/knowledge_base.json` 的 `tracks` 列表，新增/修改歌曲条目：
- `title`, `artist`, `album`, `genre`, `tags`: ["string"]

建议按常见场景/心情/风格补充 `tags`，提高检索效果。

## 生产化建议

- 引入更好的分词/嵌入检索（如 sentence-transformers + Faiss）
- 提升打分策略，加入意图/情绪识别
- 加入去重和多样性约束
- 前端美化与播放链接整合（Spotify/Apple Music/网易云）
- 缓存与观测（日志、指标）

## LangChain + DeepSeek 简单对话机器人

一个使用 LangChain 通过 OpenAI 兼容接口连接 DeepSeek 的命令行聊天机器人，支持会话记忆。

### 1. 准备环境（Windows PowerShell）

```powershell
cd E:\my_pro

# 可选：创建并激活虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

方法一：创建 `.env` 文件（推荐，与 `python-dotenv` 配合）

```ini
# 在项目根目录新建 .env，内容示例：
DEEPSEEK_API_KEY=替换为你的DeepSeek密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

也可以参考 `env.example` 快速复制：

```powershell
Copy-Item env.example .env
# 然后编辑 .env 写入真实密钥
```

方法二：临时在 PowerShell 中设置（仅本次会话有效）

```powershell
$env:DEEPSEEK_API_KEY = "你的密钥"
$env:DEEPSEEK_BASE_URL = "https://api.deepseek.com"
$env:DEEPSEEK_MODEL = "deepseek-chat"
```

### 3. 运行机器人

```powershell
python .\app\main.py
```

启动后直接输入内容对话，输入 `/exit` 退出。

### 4. 说明

- 使用 `langchain-openai.ChatOpenAI` 通过 `base_url` 指向 DeepSeek 的 OpenAI 兼容接口。
- 默认模型为 `deepseek-chat`，可通过 `DEEPSEEK_MODEL` 覆盖（如 `deepseek-reasoner`）。
- 会话记忆基于 `RunnableWithMessageHistory`，示例中用默认 `session_id`；若要多会话，可按需区分。


当前后端默认使用 LangChain Agent。若要切换为直连 SDK 的 `backend/llm.py` 路径，可在 `backend/main.py` 中替换为原有逻辑。
