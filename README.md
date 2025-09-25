# 세친구 투어 채팅 상담 시스템

베트남 다낭 투어 상품을 AI 챗봇으로 상담받을 수 있는 시스템입니다.

## 🏗️ 시스템 구조

- **Frontend**: React.js (Vercel)
- **Database**: PostgreSQL (Supabase)
- **AI Service**: Python FastAPI (Railway)
- **LLM**: OpenAI GPT-4o-mini

## 📦 프로젝트 구조

```
chat-consulting/
├── client/          # React 프론트엔드
├── server/          # Node.js 백엔드 (로컬 개발용)
├── ai-service/      # Python AI 서비스
└── database/        # 데이터베이스 스키마
```

## 🚀 로컬 개발

### 필수 요구사항
- Node.js 18+
- Python 3.9+
- PostgreSQL
- OpenAI API 키

### 설치 및 실행

1. **프론트엔드 실행**
```bash
cd client
npm install
npm start
```

2. **AI 서비스 실행**
```bash
cd ai-service
pip install -r requirements.txt
python main.py
```

3. **데이터베이스 설정**
- PostgreSQL에서 `chat_consulting` 데이터베이스 생성
- 환경변수 설정 (.env 파일)

## 🌐 온라인 배포

### 배포된 서비스
- **Frontend**: [Vercel URL]
- **Database**: Supabase
- **AI Service**: Railway

## 🎯 주요 기능

- 실시간 채팅 인터페이스
- AI 투어 상품 상담
- 7개 투어 상품 데이터베이스
- 가격 문의 및 정보 제공
- WebSocket 실시간 통신

## 📋 투어 상품

1. 래프팅 투어
2. 라이트팩 투어
3. 베스트팩 투어
4. 베이직 골프투어 54홀
5. 베이직 골프투어 72홀
6. 호이안 투어
7. 패밀리팩 투어

## 🔧 기술 스택

- **Frontend**: React, Socket.IO Client
- **Backend**: Node.js, Express, Socket.IO
- **AI**: Python, FastAPI, OpenAI API
- **Database**: PostgreSQL
- **Deployment**: Vercel, Supabase, Railway