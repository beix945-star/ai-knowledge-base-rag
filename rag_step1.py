from pypdf import PdfReader

# 读取PDF
pdf_path = "外卖骑手职业生存状况调查策划书(6).pdf"  # 你可以换成自己的文件

reader = PdfReader(pdf_path)

text = ""

# 提取所有页面文本
for page in reader.pages:
    text += page.extract_text()

print("📄 PDF总长度：", len(text))
print("📌 前500字：\n", text[:500])