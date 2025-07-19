import os
import requests
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
print("API KEY:", api_key)
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "你好，介绍一下你自己"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
}
r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=30)
print(r.status_code, r.text)