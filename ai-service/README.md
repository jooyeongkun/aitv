# AI Chat Service

## 설치 및 실행

### 1. 파이썬 환경 설정
```bash
cd ai-service
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일에서 다음 값들을 설정하세요:

```
OPENAI_API_KEY=your_openai_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chat_consulting
DB_USER=postgres
DB_PASS=your_password
```

### 3. AI 서비스 실행
```bash
python main.py
```

AI 서비스는 http://localhost:5000 에서 실행됩니다.

## API 엔드포인트

### POST /chat
고객 메시지에 대한 AI 응답을 생성합니다.

**요청:**
```json
{
  "message": "다낭 호텔 추천해주세요",
  "conversation_id": 1
}
```

**응답:**
```json
{
  "response": "다낭 지역의 호텔을 찾아드렸습니다...",
  "intent": "hotel",
  "keywords": ["다낭", "호텔"],
  "hotels_found": 3,
  "tours_found": 0
}
```

## AI 기능

1. **의도 파악**: 호텔, 투어, 가격, 일반 문의 분류
2. **키워드 추출**: 지역, 상품명, 관련 용어 추출
3. **DB 검색**: PostgreSQL에서 관련 호텔/투어 정보 검색
4. **응답 생성**: OpenAI GPT를 사용한 자연스러운 응답

## 특징

- ✅ DB에 있는 정보만 사용
- ✅ 무조건적인 추천 안함
- ✅ 고객 질문 의도에 맞는 답변
- ✅ 자연스러운 대화
- ✅ 실시간 자동 응답 (1초 딜레이)

## 연동 구조

```
고객 메시지 → Node.js (3004) → Python AI (5000) → Node.js → 소켓 전송
```