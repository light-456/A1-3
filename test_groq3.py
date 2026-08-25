import os
import json
import urllib.request
from urllib.error import HTTPError
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

payload = {
    "model": "mixtral-8x7b-32768",
    "messages": [
        {
            "role": "system",
            "content": "당신은 조언자입니다."
        },
        {
            "role": "user",
            "content": "안녕"
        }
    ]
}

url = "https://api.groq.com/openai/v1/chat/completions"
req_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers=req_headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        print(res_data["choices"][0]["message"]["content"])
except HTTPError as e:
    print("HTTP Error:", e.code)
    print("Response Body:", e.read().decode())
except Exception as e:
    print("API Error:", e)
