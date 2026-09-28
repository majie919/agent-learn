# ==========================================
# 文件名：agent_loop.py
# 作用：完整版 Agent（ReAct 循环 + DeepSeek API + RAG + 评估统计）
# ==========================================

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.tools import TOOLS
from app.rag import load_and_chunk, retrieve, build_prompt

# 加载 .env 里的 API Key
load_dotenv()

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 定义工具的 JSON Schema
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

def run_agent(user_input: str, max_steps: int = 5):
    """Agent 核心循环"""
    # RAG 检索
    chunks = load_and_chunk()
    retrieved = retrieve(user_input, chunks)
    if retrieved:
        print(f"📚 检索到 {len(retrieved)} 条相关资料")
        enhanced_input = build_prompt(user_input, retrieved)
    else:
        enhanced_input = user_input

    # 初始化 messages
    messages = [
        {"role": "system", "content": "你是一个智能助手，需要时请调用工具。最终请用中文回答。"},
        {"role": "user", "content": enhanced_input}
    ]

    # 统计变量
    total_tokens = 0
    start_time = time.time()
    steps_used = 0

    print(f"👤 用户: {user_input}\n")

    for step in range(max_steps):
        steps_used = step + 1
        print(f"--- 第 {step + 1} 轮循环 ---")

        # 调用 LLM
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )

        # 累加 Token 消耗
        if response.usage:
            total_tokens += response.usage.total_tokens

        msg = response.choices[0].message
        messages.append(msg)

        # 情况 A：模型没有调用工具，直接返回最终答案
        if not msg.tool_calls:
            print(f"\n✅ Agent 最终回答: {msg.content}")
            elapsed = time.time() - start_time
            print(f"\n📊 本次执行统计：")
            print(f"   - 循环步数: {steps_used}")
            print(f"   - 总耗时: {elapsed:.2f} 秒")
            print(f"   - Token 消耗: {total_tokens}")
            return msg.content

        # 情况 B：模型决定调用工具
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"🛠️ 模型决定调用工具: {func_name}，参数: {func_args}")

            if func_name in TOOLS:
                result = TOOLS[func_name](**func_args)
            else:
                result = f"未知工具: {func_name}"

            print(f"👁️ 观察结果: {result}\n")

            # 把工具结果回填给模型
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    print("⚠️ 达到最大步数，任务未完成。")
    return None


if __name__ == "__main__":
    print("🤖 Agent 已启动，输入 'quit' 或 'exit' 退出。\n")
    while True:
        user_input = input("👤 你: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 再见！")
            break
        run_agent(user_input)
        print("\n" + "=" * 50 + "\n")