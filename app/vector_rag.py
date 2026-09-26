# ==========================================
# 文件名：vector_rag.py
# 作用：手写向量检索，理解余弦相似度
# ==========================================

import os
import numpy as np

# 1. 模拟 Embedding：把文本转成向量
# 真实场景会调用 Embedding 模型（如 text-embedding-3-small）
# 这里用哈希生成稳定的随机向量，保证同一文本每次结果相同
def get_embedding(text: str, dim: int = 128) -> np.ndarray:
    np.random.seed(hash(text) % (2**32))
    return np.random.randn(dim)

# 2. 计算余弦相似度：两个向量的夹角越小，越相似
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 3. 加载并切分知识库（和昨天一样）
def load_and_chunk(folder_path: str = "knowledge") -> list:
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                for p in paragraphs:
                    chunks.append({"source": filename, "content": p})
    return chunks

# 4. 向量检索
def vector_retrieve(query: str, chunks: list, top_k: int = 2) -> list:
    query_vec = get_embedding(query)
    scored = []
    for chunk in chunks:
        chunk_vec = get_embedding(chunk["content"])
        score = cosine_similarity(query_vec, chunk_vec)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]

# 5. 测试
if __name__ == "__main__":
    chunks = load_and_chunk()
    query = "我想问一下休假的事情"  # 故意用“休假”，测试语义匹配
    results = vector_retrieve(query, chunks)
    print(f"🔍 查询: {query}\n")
    for r in results:
        print(f"📚 匹配到: {r['content'][:50]}...\n")