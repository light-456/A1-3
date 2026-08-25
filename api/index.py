import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_json(
            200,
            {
                "message": "AI 명언 API가 정상적으로 작동하고 있습니다."
            }
        )

    def do_POST(self):
        try:
            # 1. Groq API 키 확인
            api_key = os.environ.get("GROQ_API_KEY")

            if not api_key:
                self.send_json(
                    500,
                    {
                        "error": "GROQ_API_KEY 환경변수가 설정되지 않았습니다."
                    }
                )
                return

            # 2. 프론트엔드에서 보낸 데이터 읽기
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(
                body.decode("utf-8")
            )

            user_input = data.get("text", "").strip()

            # 3. 빈 입력 확인
            if not user_input:
                self.send_json(
                    400,
                    {
                        "error": "내용을 입력해주세요."
                    }
                )
                return

            # 4. Groq API 요청 데이터
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "당신은 따뜻한 공감과 통찰력 있는 조언을 건네는 "
                            "명언가입니다. 사용자의 고민에 맞는 짧고 힘이 되는 "
                            "명언과 조언을 한국어로 3~4문장 내로 작성해주세요."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }

            # 5. Groq API 주소
            url = (
                "https://api.groq.com/"
                "openai/v1/chat/completions"
            )

            # 6. API 요청 헤더
            req_headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # 7. Groq API 호출
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=req_headers,
                method="POST"
            )

            with urllib.request.urlopen(
                req,
                timeout=15
            ) as response:

                res_data = json.loads(
                    response.read().decode("utf-8")
                )

            # 8. AI 결과
            ai_answer = (
                res_data["choices"][0]["message"]["content"]
            )

            # 9. 프론트엔드로 반환
            self.send_json(
                200,
                {
                    "result": ai_answer
                }
            )

        except Exception as e:
            print("API 오류:", str(e))

            self.send_json(
                500,
                {
                    "error": "잠시 후 다시 시도해주세요."
                }
            )

    def send_json(self, status_code, data):
        response = json.dumps(
            data,
            ensure_ascii=False
        )

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(response.encode("utf-8")))
        )

        self.end_headers()

        self.wfile.write(
            response.encode("utf-8")
        )