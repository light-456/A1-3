// 엔터키 키 입력 지원
document.addEventListener('DOMContentLoaded', () => {
    const inputElement = document.getElementById('userInput');
    if (inputElement) {
        inputElement.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                generateAdvice();
            }
        });
    }
});

async function generateAdvice() {
    const userInput = document.getElementById('userInput').value;
    const resultElement = document.getElementById('result');
    const resultBox = document.getElementById('resultBox');
    const btn = document.getElementById('generateBtn');

    // 1. 빈 입력 검증 (필수값 누락)
    if (!userInput.trim()) {
        resultBox.classList.remove('hidden');
        resultElement.innerText = "⚠️ 고민이나 기분을 입력해주세요.";
        resultElement.className = "error-text";
        return;
    }

    // UI 상태 업데이트 (로딩 시작 및 버튼 비활성화)
    btn.disabled = true;
    btn.innerText = "생성 중...";
    resultBox.classList.remove('hidden');
    resultElement.innerText = "⏳ AI가 당신을 위한 명언을 생각하고 있습니다...";
    resultElement.className = "loading-text";

    // 45초 타임아웃 컨트롤러 설정 (재시도 및 지연 대비)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 45000);

    try {
        const response = await fetch('/api/index', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: userInput }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        
        let data;
        try {
            data = await response.json();
        } catch (jsonErr) {
            console.error("JSON 파싱 에러:", jsonErr);
            throw new Error("서버 응답 형식이 올바르지 않습니다.");
        }

        if (response.ok) {
            // 성공 시 결과 표시
            resultElement.innerText = data.result;
            resultElement.className = "success-text";
        } else {
            // API 4xx/5xx 에러 처리
            console.error("서버 반환 에러:", data);
            resultElement.innerText = data.error || "⚠️ 잠시 후 다시 시도해주세요.";
            resultElement.className = "error-text";
        }
    } catch (error) {
        clearTimeout(timeoutId);
        console.error("통신 에러 상세:", error);
        if (error.name === 'AbortError') {
            // 타임아웃 발생 시 메시지
            resultElement.innerText = "⌛ 응답 시간이 지연되고 있습니다. 잠시 후 다시 시도해주세요.";
        } else {
            // 네트워크 등 일반 통신 오류
            resultElement.innerText = "⚠️ 서버 통신 중 오류가 발생했습니다. (백엔드 서버 실행 여부를 확인해주세요)";
        }
        resultElement.className = "error-text";
    } finally {
        // UI 상태 복구
        btn.disabled = false;
        btn.innerText = "생성하기";
    }
}