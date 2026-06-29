from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests

# ======================
# 1. DeepSeek API
# ======================
API_KEY = "你的API"
url = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# ======================
# 2. 读取PDF
# ======================
pdf_path = "外卖骑手职业生存状况调查策划书(6).pdf"

reader = PdfReader(pdf_path)

text = ""
for page in reader.pages:
    if page.extract_text():
        text += page.extract_text()

# ======================
# 3. chunk优化（核心升级）
# ======================
def split_text(text):
    paragraphs = text.split("\n")

    chunks = []
    buffer = ""

    for p in paragraphs:
        p = p.strip()
        if len(p) < 10:
            continue

        buffer += p + "\n"

        if len(buffer) > 200:
            chunks.append(buffer)
            buffer = ""

    if buffer:
        chunks.append(buffer)

    return chunks

chunks = split_text(text)

print(f"📦 chunk数量: {len(chunks)}")

# ======================
# 4. embedding模型
# ======================
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

embeddings = model.encode(chunks, normalize_embeddings=True)
embeddings = np.array(embeddings).astype('float32')

# ======================
# 5. FAISS索引（cosine）
# ======================
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

# ======================
# 6. 用户问题
# ======================
query = input("请输入问题：")

def rewrite_query(query):
    if "幸福" in query or "满意" in query:
        return query + " 职业满意度 工作压力 收入稳定 社会保障 工作时长 交通安全"
    if "收入" in query or "工资" in query:
        return query + " 收入 不稳定 工资 平台 就业"
    if "压力" in query:
        return query + " 工作压力 工作时长 交通安全 收入不稳定"
    return query

search_query = rewrite_query(query)

query_vec = model.encode([search_query], normalize_embeddings=True)
query_vec = np.array(query_vec).astype('float32')
# ======================
# 7. 检索（topK）
# ======================
D, I = index.search(query_vec, k=2)

# 防止空结果
if len(I[0]) == 0:
    print("❌ 未检索到相关内容")
    exit()

# ======================
# 8. 构建上下文
# ======================
# ===== 8. 构建上下文 =====
valid_indices = [i for i in I[0] if i != -1]

# 最多取前3个有效chunk
top_indices = valid_indices[:3]

context = "\n\n".join([chunks[i] for i in top_indices])

# ======================
# 9. Prompt优化版
# ======================
prompt = f"""
你是一个严谨的基于文档的AI助手。

请根据“参考内容”回答用户问题。

规则：
1. 优先使用参考内容中的直接信息
2. 如果文档没有直接结论，但有相关因素，可以基于这些因素做有限推断
3. 推断时必须说明“根据文档中的相关信息推测”
4. 不允许编造文档中没有的数据
5. 用简洁、专业中文回答

参考内容：
{context}

用户问题：
{query}

请开始回答：
"""

# ======================
# 10. 调用DeepSeek
# ======================
data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

# ======================
# 11. 输出结果
# ======================
print("\n🤖 AI回答：\n")

if "choices" in result:
    print(result["choices"][0]["message"]["content"])
else:
    print("❌ API错误：")
    print(result)

# ======================
# 12. Debug（可删）
# ======================
print("\n--- DEBUG ---")
print("Top chunks index:", I)

print("\n📌 命中的内容：")
for i in I[0]:
    print("-----")
    print(chunks[i])