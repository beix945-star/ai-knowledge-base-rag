from sentence_transformers import SentenceTransformer
import numpy as np

# 假设你已经有chunk（复制step2的逻辑）
chunks = [
    "外卖骑手收入情况调查...",
    "工作压力分析...",
    "职业满意度...",
    "交通安全问题...",
    "平台管理机制..."
]

# 加载模型（轻量级）
model = SentenceTransformer('all-MiniLM-L6-v2')

# 向量化
embeddings = model.encode(chunks)

print("📊 向量维度：", len(embeddings))
print("📌 第一个chunk向量前5个值：", embeddings[0][:5])