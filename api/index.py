import os
import sys
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# 윈도우 콘솔 utf-8 인코딩 설정
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# .env 파일 환경변수 로드
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

def log_msg(msg):
    """콘솔 출력 버퍼링 방지 및 인코딩 안전 출력 함수"""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'), flush=True)

def call_ai_with_retry(api_key, url, model, user_input, system_prompt, max_retries=20, provider_name="Primary"):
    """
    AI API를 호출하며, 실패 시 상세 오류 원인을 로깅하고 최대 max_retries회까지 재시도합니다.
    """
    if not api_key:
        log_msg(f"[{provider_name}] API 키가 설정되어 있지 않아 호출을 건너뜁니다.")
        return None, "API 키 누락"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    encoded_data = json.dumps(payload).encode('utf-8')

    for attempt in range(1, max_retries + 1):
        log_msg(f"[{provider_name}] API 호출 시도 {attempt}/{max_retries} (URL: {url}, Model: {model})")
        try:
            req = urllib.request.Request(url, data=encoded_data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=4) as response:
                res_bytes = response.read()
                res_data = json.loads(res_bytes.decode('utf-8'))
                
                # OpenAI 호환 형식 결과 추출
                choices = res_data.get('choices', [])
                if choices and len(choices) > 0:
                    ai_text = choices[0].get('message', {}).get('content', '').strip()
                    log_msg(f"[{provider_name}] API 호출 성공! (시도 {attempt}회차에 완료)")
                    return ai_text, None
                else:
                    err_msg = f"응답 데이터 형식 오류 (choices 항목 없음): {res_data}"
                    log_msg(f"[{provider_name} 응답 파싱 오류] 시도 {attempt}/{max_retries} 실패: {err_msg}")

        except urllib.error.HTTPError as e:
            # HTTP 4xx, 5xx 에러 상세 로그 추출
            try:
                err_body = e.read().decode('utf-8', errors='replace')
            except Exception:
                err_body = "(에러 응답 본문 읽기 실패)"
            log_msg(f"[{provider_name} HTTP 오류] 시도 {attempt}/{max_retries} 실패 - 상태 코드: {e.code} ({e.reason})\n  └ 상세 내용: {err_body}")

        except urllib.error.URLError as e:
            # DNS, 네트워크 단절, 타임아웃 등
            log_msg(f"[{provider_name} 네트워크 오류] 시도 {attempt}/{max_retries} 실패 - 원인: {e.reason}")

        except Exception as e:
            # 기타 예외
            log_msg(f"[{provider_name} 예외 발생] 시도 {attempt}/{max_retries} 실패 - 예외 유형: {type(e).__name__}, 메시지: {str(e)}")

        # 다음 재시도 전 대기
        if attempt < max_retries:
            time.sleep(0.5)

    log_msg(f"[{provider_name}] 총 {max_retries}회 재시도를 모두 실패했습니다.")
    return None, f"{provider_name} 호출 실패"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. 프론트엔드에서 전송한 요청 데이터 읽기
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            data = {}
            
        user_input = data.get('text', '').strip()

        # 필수값 검증
        if not user_input:
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            resp = json.dumps({"error": "내용을 입력해주세요."}, ensure_ascii=False)
            self.wfile.write(resp.encode('utf-8'))
            return

        # 2. 환경변수 로드 및 기본값 설정
        # 1차 Primary 설정 (Gemini)
        primary_key = os.getenv('api_key') or os.getenv('API_KEY') or os.getenv('GEMINI_API_KEY', '')
        primary_url = os.getenv('url') or os.getenv('API_URL') or os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions')
        primary_model = os.getenv('model') or os.getenv('MODEL') or os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')

        # 2차 Fallback 설정 (Groq)
        fallback_key = os.getenv('GROQ_API_KEY') or os.getenv('FALLBACK_API_KEY') or os.getenv('groq_api_key', '')
        fallback_url = os.getenv('GROQ_URL') or os.getenv('FALLBACK_API_URL') or 'https://api.groq.com/openai/v1/chat/completions'
        fallback_model = os.getenv('GROQ_MODEL') or os.getenv('FALLBACK_MODEL') or 'openai/gpt-oss-20b'

        # 재시도 횟수 (기본 20회)
        try:
            max_retries = int(os.getenv('MAX_RETRIES', '20'))
        except ValueError:
            max_retries = 20

        system_prompt = "당신은 따뜻한 공감과 통찰력 있는 조언을 건네는 명언가입니다. 사용자의 고민에 맞는 짧고 힘이 되는 명언과 조언을 한국어로 3~4문장 내로 작성해주세요."

        # 3. 1차 API 호출 (최소 20회 재시도 및 오류 로깅)
        ai_result = None
        if primary_key:
            ai_result, _ = call_ai_with_retry(
                api_key=primary_key,
                url=primary_url,
                model=primary_model,
                user_input=user_input,
                system_prompt=system_prompt,
                max_retries=max_retries,
                provider_name="Primary(Gemini)"
            )

        # 4. 1차 API 실패 또는 키 미설정 시 2차(Groq) API로 자동 롤백
        if not ai_result:
            if fallback_key:
                log_msg(f"[Fallback 롤백] 1차 API({primary_model}) 실패로 인해 2차 보조 API(Groq: {fallback_model})로 롤백하여 호출을 시작합니다.")
                ai_result, _ = call_ai_with_retry(
                    api_key=fallback_key,
                    url=fallback_url,
                    model=fallback_model,
                    user_input=user_input,
                    system_prompt=system_prompt,
                    max_retries=max_retries,
                    provider_name="Fallback(Groq)"
                )
            else:
                log_msg("[Fallback 롤백 불가] 보조 API 키(GROQ_API_KEY)가 설정되어 있지 않습니다.")

        # 5. 최종 응답 반환
        if ai_result:
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            resp = json.dumps({"result": ai_result}, ensure_ascii=False)
            self.wfile.write(resp.encode('utf-8'))
        else:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            err_resp = json.dumps({"error": "AI 서비스 호출에 실패했습니다. 잠시 후 다시 시도해주세요."}, ensure_ascii=False)
            self.wfile.write(err_resp.encode('utf-8'))