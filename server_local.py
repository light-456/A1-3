import os
import sys
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer
from api.index import handler as ApiHandler

# 윈도우 콘솔 utf-8 인코딩 설정
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class DevServerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        # /api 또는 /api/index 경로로 들어오는 POST 요청을 api/index.py 핸들러로 전달
        if self.path in ['/api', '/api/index', '/api/']:
            return ApiHandler.do_POST(self)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # 루트 디렉토리의 정적 파일(index.html, style.css, script.js 등) 서빙
        return super().do_GET()

def run(port=3000):
    root_dir = Path(__file__).resolve().parent
    os.chdir(root_dir)
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, DevServerHandler)
    print("==================================================", flush=True)
    print(f"[*] 로컬 통합 개발 서버가 시작되었습니다.", flush=True)
    print(f"[*] 브라우저 주소: http://localhost:{port}", flush=True)
    print("==================================================", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.", flush=True)

if __name__ == '__main__':
    run()
