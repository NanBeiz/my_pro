## DeepSeek + LangChain 简单聊天机器人

### 1. 准备环境
- 安装 Python 3.9+
- 在项目根目录安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key
- 在系统环境变量中设置：
  - `DEEPSEEK_API_KEY`: 从 DeepSeek 平台获取
  - 可选：`DEEPSEEK_MODEL`（默认 `deepseek-chat`）、`DEEPSEEK_TEMPERATURE`（默认 `0.7`）

Windows PowerShell 示例：
```powershell
$env:DEEPSEEK_API_KEY="你的key"
```

### 3. 运行
```bash
python chatbot_deepseek.py
```

### 4. 说明
- 使用 `langchain-openai` 的 `ChatOpenAI` 以 OpenAI 兼容协议连接 DeepSeek：`base_url=https://api.deepseek.com`
- 默认模型：`deepseek-chat`。你也可以将其改为 `deepseek-reasoner`。

hello git
