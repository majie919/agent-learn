import asyncio
import time

# 异步版本
async def async_task(name: str, seconds: int):
    print(f"{name} 开始")
    await asyncio.sleep(seconds)  # 注意：是 asyncio.sleep，不是 time.sleep
    print(f"{name} 结束")
    return f"{name} 结果"

async def main():
    start = time.time()
    
    # 并发执行三个任务
    results = await asyncio.gather(
        async_task("任务A", 2),
        async_task("任务B", 2),
        async_task("任务C", 2),
    )
    
    print(f"结果: {results}")
    print(f"总耗时: {time.time() - start:.2f}秒")  # 约2秒，不是6秒

if __name__ == "__main__":
    asyncio.run(main())