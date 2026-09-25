# ==========================================
# 文件名：pydantic_demo.py
# 作用：演示用 Pydantic 校验数据（Agent 防止大模型乱传参数的核心工具）
# ==========================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional

# 【定义数据模型 1：工具调用】
# 继承 BaseModel 后，这个类就拥有了自动校验、类型转换、序列化等能力
class ToolCall(BaseModel):
    # Field 用来给字段加约束：description 是给 LLM 看的提示，default_factory 是默认值
    name: str = Field(description="工具名称，例如 get_weather")
    arguments: dict = Field(default_factory=dict, description="工具参数")
    
    # 【自定义校验器】
    # @field_validator 装饰器：在赋值后自动触发这个函数
    # 这里校验 name 不能为空，如果为空就抛出 ValueError
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("工具名不能为空")
        return v

# 【定义数据模型 2：用户请求】
# Agent 收到用户请求时，先经过这个模型校验，防止恶意或错误输入
class AgentRequest(BaseModel):
    user_input: str = Field(min_length=1, max_length=2000, description="用户输入内容")
    session_id: Optional[str] = Field(default=None, description="会话ID，可选")
    max_steps: int = Field(default=5, ge=1, le=20, description="最大循环步数，默认5，范围1-20")

# ============ 测试环节 ============

# 1. 正常情况：传入合法数据
req = AgentRequest(user_input="北京天气如何？")
# model_dump()：把对象转成 Python 字典，方便后续处理
print("正常请求:", req.model_dump())

# 2. 异常情况：传入空字符串，触发校验失败
try:
    bad = AgentRequest(user_input="")
except Exception as e:
    # 这里会捕获 Pydantic 的 ValidationError
    print(f"校验失败: {e}")

# 3. 工具调用测试
tc = ToolCall(name="get_weather", arguments={"city": "北京"})
# model_dump_json()：把对象转成 JSON 字符串，方便存日志或发给前端
print("工具调用:", tc.model_dump_json())