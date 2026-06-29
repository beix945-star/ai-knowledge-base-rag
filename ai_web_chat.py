import streamlit as st
import requests

API_KEY = "你的API"  # 替换为你的DeepSeek API Key

url = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 页面标题
st.title("🤖 AI聊天机器人（DeepSeek版）")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一个专业、简洁的AI助手"}
    ]

# 展示历史对话
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# 用户输入
user_input = st.chat_input("请输入你的问题...")

if user_input:
    # 显示用户消息
    st.chat_message("user").write(user_input)

    # 加入历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 请求AI
    data = {
        "model": "deepseek-chat",
        "messages": st.session_state.messages,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    ai_reply = result["choices"][0]["message"]["content"]

    # 显示AI回复
    st.chat_message("assistant").write(ai_reply)

    # 加入历史
    st.session_state.messages.append(
        {"role": "assistant", "content": ai_reply}
    )