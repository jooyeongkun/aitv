"""
여행 상담 AI 웹서비스 (FastAPI)
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from travel_ai_consultant import TravelConsultantDB, TravelAIConsultant
import os

app = FastAPI(title="여행 상담 AI 서비스")

# DB 설정
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'travel_consultation'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 5432))
}

# 전역 변수로 DB와 상담사 초기화
db = TravelConsultantDB(db_config)
consultant = None

@app.on_event("startup")
async def startup_event():
    global consultant
    if db.connect():
        consultant = TravelAIConsultant(db)
        print("Travel consultation AI service started!")
    else:
        raise Exception("Database connection failed")

# 요청/응답 모델
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# API 엔드포인트
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """여행 상담 채팅 API"""
    # Debug info removed due to encoding issues
    try:
        # 세션 ID가 없으면 새로 생성
        if not request.session_id:
            session_id = db.create_consultation_session()
        else:
            session_id = request.session_id
        
        # AI 응답 생성
        response = consultant.generate_travel_recommendation(
            request.message, session_id
        )
        
        # Response debug info removed due to encoding issues
        
        if response is None:
            response = "Sorry, I cannot generate a response at this time."
            
        return ChatResponse(response=response, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/packages")
async def get_packages(destination: str = None, category: str = None, max_price: int = None):
    """패키지 상품 조회 API"""
    try:
        packages = db.get_packages(destination, category, max_price)
        return {"packages": packages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hotels")
async def get_hotels(city: str = None, star_rating: int = None, max_price: int = None):
    """호텔 정보 조회 API"""
    try:
        hotels = db.get_hotels(city, star_rating, max_price)
        return {"hotels": hotels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def home():
    """메인 페이지 (간단한 채팅 UI)"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>여행 상담 AI</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .chat-container { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; background: #fafafa; }
            .message { margin-bottom: 15px; padding: 10px; border-radius: 8px; }
            .user-message { background: #007bff; color: white; margin-left: 20%; text-align: right; }
            .ai-message { background: #e9ecef; color: #333; margin-right: 20%; }
            .input-container { display: flex; gap: 10px; }
            #messageInput { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            #sendButton { padding: 12px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            #sendButton:hover { background: #0056b3; }
            .loading { color: #666; font-style: italic; }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            
            @media (max-width: 600px) {
                .container { margin: 10px; padding: 15px; }
                .user-message, .ai-message { margin-left: 0; margin-right: 0; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 여행 상담 AI</h1>
            <div id="chatContainer" class="chat-container">
                <div class="message ai-message">
                    안녕하세요! 여행 계획을 도와드릴 AI 상담사입니다. 어떤 여행을 계획하고 계신가요? 😊
                </div>
            </div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="여행 관련 질문을 입력하세요... (예: 제주도 3박4일 힐링여행 추천해주세요)" />
                <button id="sendButton">전송</button>
            </div>
        </div>

        <script>
            let sessionId = null;

            function sendMessage() {
                console.log('sendMessage 함수 호출됨');
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                console.log('메시지:', message);
                if (!message) {
                    console.log('빈 메시지이므로 리턴');
                    return;
                }

                addMessage(message, 'user');
                input.value = '';
                
                // 로딩 메시지 표시
                const loadingDiv = addMessage('답변을 생성중입니다...', 'ai', 'loading');
                console.log('API 호출 시작');

                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                })
                .then(response => {
                    console.log('응답 받음:', response);
                    return response.json();
                })
                .then(data => {
                    console.log('JSON 데이터:', data);
                    loadingDiv.remove();
                    if (data.response) {
                        addMessage(data.response, 'ai');
                        sessionId = data.session_id;
                    } else if (data.detail) {
                        addMessage('요청 처리 중 오류가 발생했습니다: ' + JSON.stringify(data.detail), 'ai');
                    } else {
                        addMessage('알 수 없는 오류가 발생했습니다.', 'ai');
                    }
                })
                .catch(error => {
                    console.error('에러 발생:', error);
                    loadingDiv.remove();
                    addMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.', 'ai');
                });
            }

            function addMessage(text, sender, className = '') {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + sender + '-message ' + className;
                if (text && typeof text === 'string') {
                    messageDiv.innerHTML = text.replace(/\\n/g, '<br>');
                } else {
                    messageDiv.innerHTML = text || '메시지를 표시할 수 없습니다.';
                }
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return messageDiv;
            }

            // Enter 키로 전송
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                console.log('키 입력됨:', e.key);
                if (e.key === 'Enter') {
                    console.log('엔터 키 감지, sendMessage 호출');
                    sendMessage();
                }
            });
            
            // 전송 버튼 클릭 이벤트
            document.getElementById('sendButton').addEventListener('click', function() {
                console.log('전송 버튼 클릭됨');
                sendMessage();
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)