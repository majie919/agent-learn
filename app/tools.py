# ==========================================
# 文件名：tools.py
# 作用：定义 Agent 可调用的工具（真实天气 API）
# ==========================================

import requests

def get_weather(city: str) -> str:
    """查询真实城市天气（使用 Open-Meteo 免费 API）"""
    # 1. 把城市名转成经纬度
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh"
    geo_resp = requests.get(geo_url).json()
    if not geo_resp.get("results"):
        return f"未找到城市: {city}"
    
    lat = geo_resp["results"][0]["latitude"]
    lon = geo_resp["results"][0]["longitude"]
    
    # 2. 用经纬度查真实天气
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather_resp = requests.get(weather_url).json()
    temp = weather_resp["current_weather"]["temperature"]
    return f"{city} 当前气温: {temp}°C"

def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

# 工具字典（供 Agent 调用）
TOOLS = {
    "get_weather": get_weather,
    "calculator": calculator
}