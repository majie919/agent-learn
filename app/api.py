# ==========================================
# 文件名：api.py
# 作用：把 Agent 封装成 FastAPI 服务
# ==========================================

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Agent API", description="企业知识库客服 Agent")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 引入工具和 RAG
from app.tools import TOOLS
from app.rag import load_and_chunk, retrieve, build_prompt

# 定义请求体
class ChatRequest(BaseModel):
    message: str

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的真实天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，例如：北京"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，支持加减乘除和幂运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，例如 2**10"}
                },
                "required": ["expression"]
            }
        }
    }
]

async def agent_stream(user_input: str, max_steps: int = 5):
    """流式版本 Agent：把每一步的思考通过 SSE 推给前端"""
    
    # RAG 检索
    chunks = load_and_chunk()
    retrieved = retrieve(user_input, chunks)
    if retrieved:
        enhanced_input = build_prompt(user_input, retrieved)
        yield f"data: {json.dumps({'type': 'rag', 'content': f'检索到 {len(retrieved)} 条资料'}, ensure_ascii=False)}\n\n"
    else:
        enhanced_input = user_input
    
    messages = [
        {"role": "system", "content": "你是一个智能助手，需要时请调用工具。最终请用中文回答。"},
        {"role": "user", "content": enhanced_input}
    ]
    
    for step in range(max_steps):
        # 推送思考状态
        yield f"data: {json.dumps({'type': 'thought', 'content': f'第 {step+1} 轮思考...'}, ensure_ascii=False)}\n\n"
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        messages.append(msg)
        
        # 没有工具调用，直接返回最终答案
        if not msg.tool_calls:
            yield f"data: {json.dumps({'type': 'answer', 'content': msg.content}, ensure_ascii=False)}\n\n"
            break
        
        # 工具调用
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            # 推送工具调用信息
            yield f"data: {json.dumps({'type': 'tool_call', 'content': f'调用工具: {func_name}, 参数: {func_args}'}, ensure_ascii=False)}\n\n"
            
            result = TOOLS[func_name](**func_args) if func_name in TOOLS else f"未知工具: {func_name}"
            
            # 推送工具结果
            yield f"data: {json.dumps({'type': 'observation', 'content': str(result)}, ensure_ascii=False)}\n\n"
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

@app.post("/chat")
async def chat(req: ChatRequest):
    """流式接口：前端通过 SSE 实时接收 Agent 的思考过程"""
    return StreamingResponse(
        agent_stream(req.message),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health():
    return {"status": "ok"}