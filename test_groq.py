import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "user",
            "content": "안녕하세요"
        }
    ]
}

url = "https://api.groq.com/openai/v1/chat/completions"
req_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
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
except Exception as e:
    print("API Error:", e)
