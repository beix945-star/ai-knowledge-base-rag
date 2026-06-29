import requests

import os
API_KEY = os.getenv("DEEPSEEK_API_KEY")

url = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "简单介绍你自己 " }
    ],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)

result = response.json()

print(result["choices"][0]["message"]["content"])