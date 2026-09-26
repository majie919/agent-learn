# ==========================================
# 文件名：agent_loop.py
# 作用：手写 Agent 的 ReAct 核心循环，串联工具和模拟 LLM
# ==========================================

import json
from app.tools import TOOLS

def mock_llm(messages: list) -> str:
    """
    模拟大模型（Mock LLM）。
    在真实场景里，这里会替换成调用 OpenAI/DeepSeek 的 API。
    我们通过读取传入的 messages，决定下一步返回什么。
    """
    # 获取最后一条用户或工具发来的消息
    last_content = messages[-1]["content"]
    
    # 模拟第1步：用户问完，LLM 决定查天气
    if "北京天气" in last_content:
        return json.dumps({
            "thought": "我需要先查一下北京的天气。",
            "action": "get_weather",
            "action_input": {"city": "北京"}
        })
    
    # 模拟第2步：拿到天气结果（32度），LLM 决定算算数
    elif "晴，32°C" in last_content:
        return json.dumps({
            "thought": "北京32度，符合要求，我需要算一下2的10次方。",
            "action": "calculator",
            "action_input": {"expression": "2**10"}
        })
    
    # 模拟第3步：算数结果出来了，LLM 给出最终答案
    elif "1024" in last_content:
        return json.dumps({
            "thought": "我已经拿到了天气和计算结果，可以回答用户了。",
            "final_answer": "北京今天晴，气温32度，建议穿短袖。2的10次方等于1024。"
        })
    
    # 兜底
    else:
        return json.dumps({
            "thought": "我暂时不知道该怎么办。",
            "final_answer": "抱歉，我无法回答这个问题。"
        })

def run_agent(user_input: str, max_steps: int = 5):
    """
    Agent 核心循环控制器
    """
    # 1. 初始化 Agent 的记忆（短期记忆：对话历史）
    messages = [
        {"role": "user", "content": user_input}
    ]
    
    print(f"👤 用户: {user_input}\n")
    
    # 2. 开始 ReAct 循环
    for step in range(max_steps):
        print(f"--- 第 {step + 1} 轮循环 ---")
        
        # 让 LLM 思考，拿到它的回复（这里先用模拟的）
        llm_response = mock_llm(messages)
        print(f"🤖 LLM 原始回复: {llm_response}")
        
        # 解析 LLM 返回的 JSON
        try:
            data = json.loads(llm_response)
        except Exception as e:
            print(f"解析 LLM 回复失败: {e}")
            break
            
        # 情况 A：如果 LLM 觉得任务完成了，返回最终答案，循环结束
        if "final_answer" in data:
            print(f"\n✅ Agent 最终回答: {data['final_answer']}")
            return data['final_answer']
            
        # 情况 B：LLM 决定调用工具
        action_name = data.get("action")
        action_input = data.get("action_input", {})
        
        if action_name in TOOLS:
            tool_info = TOOLS[action_name]
            
            # 用 Pydantic 校验参数（这就是我们昨天学的东西！）
            try:
                validated_args = tool_info["args_schema"](**action_input)
            except Exception as e:
                observation = f"参数校验失败: {e}"
            else:
                # 校验通过，执行真正的工具函数
                observation = tool_info["func"](**validated_args.model_dump())
                
            print(f"🛠️ 调用工具: {action_name} 参数: {validated_args.model_dump() if 'validated_args' in locals() else action_input}")
            print(f"👁️ 观察结果: {observation}\n")
            
            # 把工具执行结果塞回记忆里，供下一轮 LLM 参考
            messages.append({"role": "tool", "content": observation})
            
        else:
            print(f"⚠️ 未知工具: {action_name}")
            break
            
    print("⚠️ 达到最大步数，任务未完成。")
    return None

if __name__ == "__main__":
    run_agent("北京天气怎么样？如果超过30度，帮我算一下 2 的 10 次方。")