import requests

import os
API_KEY = os.getenv("DEEPSEEK_API_KEY")

url = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 💡 重点：这是“记忆核心”
messages = [
    {"role": "system", "content": "你是一个专业、简洁、友好的AI助手"}
]

print("🤖 AI聊天机器人已启动，输入 exit 退出")

while True:
    user_input = input("你：")

    if user_input.lower() == "exit":
        print("AI：再见！")
        break

    # 1. 加入用户消息
    messages.append({"role": "user", "content": user_input})

    # 2. 发请求
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    # 3. 提取AI回复
    ai_reply = result["choices"][0]["message"]["content"]

    print("AI：", ai_reply)

    # 4. 写入记忆（关键！）
    messages.append({"role": "assistant", "content": ai_reply})