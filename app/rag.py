# ==========================================
# 文件名：rag.py
# 作用：最小可用的 RAG 系统（关键词检索版）
# ==========================================

import os

# 1. 加载知识库文档，切分成段落
def load_and_chunk(folder_path: str = "knowledge") -> list:
    """读取文件夹下所有 .txt 文件，按空行切分成小块"""
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # 按空行切分，每个段落作为一个 chunk
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                for p in paragraphs:
                    chunks.append({"source": filename, "content": p})
    return chunks

# 2. 简单检索：根据用户问题，找包含关键词的段落
def retrieve(query: str, chunks: list, top_k: int = 2) -> list:
    """最简版检索：按关键词匹配度打分"""
    # 把问题拆成关键词（这里简化处理，按字符出现次数算）
    keywords = list(set(query))  # 去重后的字符集合
    scored = []
    for chunk in chunks:
        # 计算这个段落里，包含了几个问题中的关键词
        score = sum(1 for kw in keywords if kw in chunk["content"])
        if score > 0:
            scored.append((score, chunk))
    # 按分数从高到低排序，取前 top_k 个
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]

# 3. 把检索到的资料拼成提示词
def build_prompt(query: str, retrieved_chunks: list) -> str:
    """把检索到的知识库内容拼成一段提示词，塞给 LLM"""
    context = "\n\n".join([c["content"] for c in retrieved_chunks])
    return f"""请基于以下资料回答用户问题。如果资料中没有相关信息，请如实说不知道。

【资料】
{context}

【用户问题】
{query}
"""