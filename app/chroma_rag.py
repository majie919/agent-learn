# ==========================================
# 文件名：chroma_rag.py
# 作用：用 ChromaDB 做真正的向量检索
# ==========================================

import os
import chromadb

# 1. 初始化 ChromaDB 客户端（数据存在本地文件夹 chroma_db）
client = chromadb.PersistentClient(path="chroma_db")

# 2. 创建集合（相当于一张表）
collection = client.get_or_create_collection(name="company_knowledge")

# 3. 加载文档并索引
def load_and_index(folder_path: str = "knowledge"):
    # 清空旧数据，避免重复索引
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
    
    idx = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                for p in paragraphs:
                    collection.add(
                        documents=[p],
                        metadatas=[{"source": filename}],
                        ids=[f"chunk_{idx}"]
                    )
                    idx += 1
    print(f"✅ 已索引 {idx} 个 Chunk")

# 4. 检索
def chroma_retrieve(query: str, top_k: int = 2) -> list:
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"][0] if results["documents"] else []

# 5. 测试
if __name__ == "__main__":
    load_and_index()
    query = "休假制度"  # 看看能不能匹配到“年假”
    results = chroma_retrieve(query)
    print(f"🔍 查询: {query}\n")
    for r in results:
        print(f"📚 匹配到: {r[:50]}...\n")