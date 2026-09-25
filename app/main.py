# ==========================================
# 文件名：main.py
# 作用：用 FastAPI 搭建一个流式聊天接口（Agent 对外提供服务的门面）
# ==========================================

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

# 创建 FastAPI 应用实例（相当于 Java 里的启动类）
app = FastAPI(title="Agent API", description="我的第一个 Agent 流式接口")

# 【定义请求体数据模型】
# 就像你刚才学的 Pydantic，FastAPI 会自动用这个模型校验前端传来的 JSON
class ChatRequest(BaseModel):
    message: str

# 【模拟大模型流式输出】
# 核心：这是一个异步生成器（async def + yield）
# Agent 开发里，真正的流式输出就是把 LLM 返回的每个 token（字）通过 yield 吐出来
async def fake_llm_stream(message: str):
    response = f"你说的是：{message}。我正在思考..."
    for char in response:
        yield char  # 关键字：每次只返回一个字
        await asyncio.sleep(0.05)  # 模拟打字机效果，等 0.05 秒再吐下一个字

# 【定义接口路由】
# POST 请求，路径是 /chat/stream
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    # StreamingResponse：FastAPI 专门用来处理流式返回的类
    # media_type="text/event-stream"：这就是 SSE (Server-Sent Events) 协议，前端专用的流式接收方式
    return StreamingResponse(
        fake_llm_stream(req.message),
        media_type="text/event-stream"
    )

# 【健康检查接口】
# 运维人员和 k8s 靠这个接口判断你的服务是不是还活着
@app.get("/health")
async def health():
    return {"status": "ok"}