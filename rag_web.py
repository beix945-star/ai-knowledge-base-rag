import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests


# ======================
# 页面配置
# ======================
st.set_page_config(
    page_title="AI知识库问答系统",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI知识库问答系统（DeepSeek + FAISS + RAG）")


# ======================
# 侧边栏配置
# ======================
st.sidebar.title("⚙️ 配置")

api_key = st.sidebar.text_input(
    "请输入 DeepSeek API Key",
    type="password",
    placeholder="sk-xxxx"
)

uploaded_files = st.sidebar.file_uploader(
    "上传文档",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True
)

top_k = st.sidebar.slider(
    "检索参考片段数量",
    min_value=1,
    max_value=5,
    value=3
)


# ======================
# 加载 embedding 模型
# ======================
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("BAAI/bge-small-zh-v1.5")


# ======================
# PDF读取
# ======================
from docx import Document

def read_document(file):
    filename = file.name.lower()

    # 读取 PDF
    if filename.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    # 读取 Word docx
    elif filename.endswith(".docx"):
        doc = Document(file)
        text = ""

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"

        return text

    # 读取 txt / md
    elif filename.endswith(".txt") or filename.endswith(".md"):
        return file.getvalue().decode("utf-8", errors="ignore")

    else:
        return ""


# ======================
# 文本切分优化版
# ======================
def split_text(text, source_name, chunk_size=250, overlap=50):
    paragraphs = text.split("\n")

    clean_paragraphs = []

    for p in paragraphs:
        p = p.strip()

        if len(p) < 10:
            continue
        if "目录" in p:
            continue

        clean_paragraphs.append(p)

    chunks = []
    current = ""

    for p in clean_paragraphs:
        if len(current) + len(p) <= chunk_size:
            current += p + "\n"
        else:
            if len(current.strip()) > 30:
                 chunks.append({
                    "text": current.strip(),
                    "source": source_name
                })
            overlap_text = current[-overlap:] if len(current) > overlap else ""
            current = overlap_text + "\n" + p + "\n"

    if len(current.strip()) > 30:
        chunks.append({
            "text": current.strip(),
            "source": source_name
        })

    return chunks


# ======================
# 构建FAISS索引
# ======================
def build_faiss_index(chunks, model):
    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(chunk_texts, normalize_embeddings=True)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return index


# ======================
# 查询改写：提升抽象问题检索效果
# ======================
def rewrite_query(query):
    if "幸福" in query or "满意" in query:
        return query + " 职业满意度 工作压力 收入稳定 社会保障 工作时长 交通安全 平台管理"
    if "收入" in query or "工资" in query or "钱" in query:
        return query + " 收入 工资 不稳定 平台 就业"
    if "压力" in query:
        return query + " 工作压力 工作时长 收入不稳定 交通安全"
    if "制度" in query or "分配" in query or "平台" in query:
        return query + " 平台管理 社会保障 制度 工作压力 收入不稳定"
    return query
def is_global_question(question):
        keywords = [
        "谁", "最大", "最多", "占比", "多少", "分别",
        "每个人", "四个人", "比较", "总结", "分工",
        "贡献", "功劳", "比例", "排名"
    ]
        return any(word in question for word in keywords)

# ======================
# 调用DeepSeek
# ======================
def ask_deepseek(api_key, context, query):
    api_key = api_key.strip()

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    prompt = f"""
你是一个严谨的文档分析助手。

请根据“参考内容”回答用户问题。

规则：
1. 优先使用参考内容中的信息
2. 如果问题涉及多人对比、分工、贡献、占比，请先提取每个人的相关工作记录
3. 如果文档没有明确量化数据，不能编造具体百分比
4. 可以基于工作记录数量、任务重要性、职责范围做“合理推测”，但必须说明这是推测
5. 回答要有结构，尽量分点说明
6. 如果信息不足，请说明缺少哪些信息

参考内容：
{context}

用户问题：
{query}

请用中文回答：
"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=60
    )

    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]

    return f"API调用失败：{result}"


# ======================
# 初始化聊天记录
# ======================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "index" not in st.session_state:
    st.session_state.index = None


# ======================
# 上传文档并构建知识库
# ======================
if uploaded_files:
    with st.spinner("正在读取多个文档并构建知识库..."):
        all_chunks = []

        for file in uploaded_files:
            text = read_document(file)

            if len(text.strip()) > 0:
                file_chunks = split_text(text, file.name)
                all_chunks.extend(file_chunks)

        if len(all_chunks) == 0:
            st.error("没有从文档中提取到有效文本。")
        else:
            chunks = all_chunks

            model = load_embedding_model()
            index = build_faiss_index(chunks, model)

            st.session_state.chunks = chunks
            st.session_state.index = index
            st.session_state.model = model

            st.success(f"知识库构建完成，共生成 {len(chunks)} 个文本片段。")

            with st.expander("查看文本片段"):
                for idx, chunk in enumerate(chunks):
                    st.markdown(f"### Chunk {idx}")
                    st.markdown(f"**来源：{chunk['source']}**")
                    st.write(chunk["text"])


# ======================
# 显示聊天历史
# ======================
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# ======================
# 用户提问
# ======================
# ======================
# 用户提问
# ======================
user_question = st.chat_input("请输入你想问文档的问题...")

if user_question:
    if not api_key:
        st.error("请先在左侧输入 DeepSeek API Key。")
        st.stop()

    if st.session_state.chunks is None or st.session_state.index is None:
        st.error("请先上传文档并等待知识库构建完成。")
        st.stop()

    # 显示用户消息
    st.session_state.chat_history.append(
        {"role": "user", "content": user_question}
    )

    with st.chat_message("user"):
        st.write(user_question)

    # 取出知识库数据
    model = st.session_state.model
    chunks = st.session_state.chunks
    index = st.session_state.index

    # 判断是否为全局分析问题
    if is_global_question(user_question):
        # 全局分析问题：使用全部 chunk
        valid_indices = list(range(len(chunks)))
    else:
        # 普通问题：走向量检索
        search_query = rewrite_query(user_question)

        query_vec = model.encode(
            [search_query],
            normalize_embeddings=True
        )

        query_vec = np.array(query_vec).astype("float32")

        k = min(top_k, len(chunks))
        D, I = index.search(query_vec, k=k)

        valid_indices = [i for i in I[0] if i != -1]

    # 构建 context
    if len(valid_indices) == 0:
        answer = "未检索到相关内容。"
        context = ""
    else:
        context_parts = []

        max_context_length = 8000
        current_length = 0

        for i in valid_indices:
            part = f"来源：{chunks[i]['source']}\n内容：{chunks[i]['text']}\n"

            if current_length + len(part) > max_context_length:
                break

            context_parts.append(part)
            current_length += len(part)

        context = "\n\n".join(context_parts)

        with st.spinner("AI正在基于文档生成回答..."):
            answer = ask_deepseek(api_key, context, user_question)

    # 保存AI回答
    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer}
    )

    # 显示AI回答
    with st.chat_message("assistant"):
        st.write(answer)

        with st.expander("查看命中的参考内容"):
            for i in valid_indices:
                st.markdown(f"### Chunk {i}")
                st.markdown(f"**来源：{chunks[i]['source']}**")
                st.write(chunks[i]["text"])