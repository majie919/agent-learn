# ==========================================
# 文件名：eval.py
# 作用：用一批测试问题跑 Agent，统计成功率、延迟、Token 成本
# ==========================================

import time
import json
from app.agent_loop import run_agent

# 测试用例集：输入 + 期望的答案关键词
TEST_CASES = [
    {"input": "北京天气怎么样", "expected_keywords": ["北京", "气温"]},
    {"input": "上海天气怎么样", "expected_keywords": ["上海", "气温"]},
    {"input": "帮我算一下 2 的 10 次方", "expected_keywords": ["1024"]},
    {"input": "公司的年假制度是什么", "expected_keywords": ["年假", "5天"]},
    {"input": "出差报销需要几天内提交", "expected_keywords": ["5个工作日"]},
]

def evaluate():
    """跑完所有测试用例，统计成功率"""
    success = 0
    total = len(TEST_CASES)
    
    for i, case in enumerate(TEST_CASES):
        print(f"\n🧪 测试 {i+1}/{total}: {case['input']}")
        start = time.time()
        
        # 注意：这里需要让 run_agent 返回最终答案（修改一下函数返回值）
        answer = run_agent(case["input"])
        elapsed = time.time() - start
        
        # 判断答案里是否包含了期望关键词
        if answer and any(kw in answer for kw in case["expected_keywords"]):
            print(f"✅ 通过（耗时 {elapsed:.2f}s）")
            success += 1
        else:
            print(f"❌ 失败（耗时 {elapsed:.2f}s）")
            return msg.content
    # 输出评估报告
    print(f"\n{'='*50}")
    print(f"📊 评估报告")
    print(f"   - 成功率: {success}/{total} = {success/total*100:.1f}%")
    print(f"{'='*50}")

if __name__ == "__main__":
    evaluate()