import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ===== 示例chunks（来自step2）=====
chunks = [
    "外卖骑手收入较高，但工作压力大",
    "工作时间长，通常超过10小时",
    "职业满意度中等",
    "交通风险较高",
    "平台管理机制复杂"
]

# ===== embedding =====
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks)

# 转成numpy
embeddings = np.array(embeddings).astype('float32')

# ===== 建立索引 =====
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# ===== 用户问题 =====
query = "外卖骑手收入怎么样？"
query_vec = model.encode([query]).astype('float32')

# ===== 搜索 =====
D, I = index.search(query_vec, k=2)

print("🔍 最相关chunk：")
for i in I[0]:
    print("-", chunks[i])