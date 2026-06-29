from pypdf import PdfReader

pdf_path = "外卖骑手职业生存状况调查策划书(6).pdf"

reader = PdfReader(pdf_path)

text = ""
for page in reader.pages:
    text += page.extract_text()

# ===== Step 2：切分文本 =====
chunk_size = 200   # 每块200字
chunks = []

for i in range(0, len(text), chunk_size):
    chunk = text[i:i+chunk_size]
    chunks.append(chunk)

print("📦 chunk数量：", len(chunks))
print("\n📌 第一个chunk：\n", chunks[0])