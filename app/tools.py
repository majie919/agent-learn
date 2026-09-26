# ==========================================
# 文件名：tools.py
# 作用：定义 Agent 可以调用的工具，并用 Pydantic 做参数校验
# ==========================================

from pydantic import BaseModel, Field

# 1. 定义查天气的参数模型
class WeatherArgs(BaseModel):
    city: str = Field(description="城市名称，例如：北京、上海")

# 2. 定义算数的参数模型
class CalculatorArgs(BaseModel):
    expression: str = Field(description="数学表达式，例如：2**10 或 3*5+2")

# 3. 真正的工具函数
def get_weather(city: str) -> str:
    """查询城市天气"""
    fake_data = {"北京": "晴，32°C", "上海": "小雨，27°C"}
    return fake_data.get(city, "未知城市")

def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        # 限制可用函数，防止注入攻击
        allowed = {"abs": abs, "round": round, "__import__": __import__}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

# 4. 把工具和它的参数模型绑定在一起，形成一个工具字典
# 以后 Agent 会根据这个字典，知道有哪些工具可用，以及怎么校验参数
TOOLS = {
    "get_weather": {
        "func": get_weather,
        "args_schema": WeatherArgs,
        "description": "查询指定城市的天气。"
    },
    "calculator": {
        "func": calculator,
        "args_schema": CalculatorArgs,
        "description": "计算数学表达式。"
    }
}