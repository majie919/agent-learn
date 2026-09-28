# 🤖 企业知识库客服 Agent

一个基于 ReAct 循环 + Function Calling + RAG 的智能客服 Agent，能自主调用工具、检索企业知识库，并通过 SSE 流式输出实时展示思考过程。

## ✨ 功能特性

- **ReAct 循环**：Agent 能自主思考、调用工具、观察结果，直到完成任务
- **Function Calling**：支持真实天气查询、数学计算等工具
- **RAG 知识库**：能回答企业制度类问题（如年假、报销、工作时间）
- **向量检索**：基于余弦相似度的语义检索
- **SSE 流式输出**：前端实时看到 Agent 的思考、工具调用、观察结果
- **成本追踪**：统计 Token 消耗、延迟、循环步数
- **评估体系**：5/5 任务完成率，平均延迟 < 1 秒

## 🛠️ 技术栈

- Python 3.12 + FastAPI + Pydantic
- DeepSeek API（兼容 OpenAI SDK）
- SSE 流式输出
- RAG 检索 + 向量检索

## 📊 评估指标

- **任务完成率**：5/5 = 100%
- **平均延迟**：< 1 秒
- **单次 Token 消耗**：约 500 tokens

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/agent-learn.git
cd agent-learn

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 4. 配置 API Key
echo "DEEPSEEK_API_KEY=你的Key" > .env

# 5. 启动服务
uvicorn app.api:app --reload

# 6. 访问接口文档
# http://127.0.0.1:8000/docs