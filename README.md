# 💡 AI 맞춤 명언가 - 오늘의 한 마디

AI가 사용자의 고민과 감정 상태를 분석하여 따뜻한 위로와 통찰력 있는 명언을 건네주는 반응형 웹 서비스입니다.

---

## 🔗 배포 URL
- **Vercel 배포 주소**: `https://<YOUR-VERCEL-APP>.vercel.app` *(Vercel 배포 후 주소 입력)*

---

## 🌟 핵심 기능
1. **맞춤형 AI 명언 생성**: 사용자의 고민이나 기분을 입력받아 LLM 모델을 통해 맞춤형 명언과 조언을 제공합니다.
2. **지능형 다중 재시도 & 오류 로깅**: API 호출 오류 발생 시 상태 코드 및 상세 에러 본문을 콘솔에 명확하게 로깅하며, 최대 20회 자동 재시도합니다.
3. **무중단 Groq 롤백(Fallback)**: 1차 API(Gemini) 장애 또는 20회 재시도 실패 시 보조 API(Groq)로 즉시 자동 롤백하여 끊김 없는 서비스를 제공합니다.
4. **반응형 웹 UI**: 데스크톱, 태블릿, 모바일 등 모든 디바이스에 최적화된 유연한 화면 레이아웃을 제공합니다.
5. **안전한 API 키 관리**: API 키를 프론트엔드에 노출하지 않고 Vercel Serverless Function (Python 백엔드) 및 환경변수(`.env`)로 안전하게 관리합니다.
6. **강력한 예외 처리**: 빈값 입력 검증, 중복 클릭 방지 로딩 처리, 15초 요청 타임아웃, 서버 오류 안내 기능이 적용되어 있습니다.

---

## 🛠 기술 스택 (Tech Stack)

### Frontend
- **HTML5**: 시맨틱 태그 구조 설계
- **CSS3**: Vanilla CSS, Google Fonts, Flexbox/Grid, Responsive Media Queries
- **JavaScript (ES6+)**: Fetch API, AbortController, DOM Manipulation

### Backend
- **Python 3.x**: Vercel Serverless Functions (`api/index.py`)
- **python-dotenv**: 로컬 개발 환경변수 로딩

### AI & Deployment
- **Primary AI**: Google Gemini API (`gemini-3.6-flash`)
- **Fallback AI**: Groq API (`openai/gpt-oss-20b`)
- **Deployment**: Vercel Serverless Platform
- **Version Control**: Git / GitHub

---

## 📁 프로젝트 구조

```
A1-3/
├── api/
│   └── index.py          # Vercel Serverless Function 백엔드 (20회 재시도, 상세 로깅, Groq 롤백 내장)
├── index.html            # 메인 HTML (3개 주요 섹션 구성)
├── style.css             # 모던 반응형 스타일시트
├── script.js             # 프론트엔드 비동기 요청 및 UX 처리
├── requirements.txt      # 파이썬 서버리스 배포 의존성 (python-dotenv)
├── .gitignore            # 환경변수 및 임시파일 버전관리 제외
├── 서비스기획서.md        # 서비스 기획 및 명세 문서
└── README.md             # 프로젝트 종합 안내서
```

---

## 🔑 환경 변수(API 키) 설정 방법

기본 URL 및 모델은 코드 내에 디폴트가 내장되어 있어 **사용자는 `.env` 파일에 키만 입력**하면 바로 동작합니다.

### 1. 로컬 환경 (`.env`)
프로젝트 루트 디렉토리의 `.env` 파일에 발급받은 API 키를 입력합니다.
```env
# 1. Primary AI (기본: Google Gemini)
api_key=your_gemini_api_key_here

# 2. Fallback AI (롤백 보조: Groq)
GROQ_API_KEY=your_groq_api_key_here
```
> 💡 필요 시 `url`, `model`, `GROQ_URL`, `GROQ_MODEL`, `MAX_RETRIES` (기본값: 20)를 커스텀할 수 있습니다.  
> ⚠️ `.env` 파일은 `.gitignore`에 포함되어 GitHub에 커밋되지 않습니다.

### 2. Vercel 배포 환경
Vercel 대시보드에서 프로젝트 설정 메뉴로 이동하여 환경변수를 등록합니다.
1. `Settings` -> `Environment Variables` 선택
2. Key: `api_key` / Value: `your_gemini_api_key_here`
3. Key: `GROQ_API_KEY` / Value: `your_groq_api_key_here`

---

## 🚀 로컬 실행 방법

1. 저장소 클론 및 이동:
   ```bash
   git clone https://github.com/your-username/A1-3.git
   cd A1-3
   ```
2. `.env` 파일에 API 키 입력:
   ```env
   api_key=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```
3. 파이썬 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
4. 로컬 통합 서버 실행:
   ```bash
   python server.py
   ```
5. 브라우저에서 접속:
   👉 **`http://localhost:3000`** 접속하여 웹사이트 및 AI 명언 생성 테스트
