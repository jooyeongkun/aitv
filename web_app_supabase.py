"""
여행 상담 AI 웹서비스 (Supabase 연동 버전)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional
from supabase_db import SupabaseDB
from travel_ai_consultant_supabase import TravelAIConsultantSupabase

app = FastAPI(title="여행 상담 AI 서비스 (Supabase)")

# HEAD 요청 자동 처리를 위한 미들웨어
@app.middleware("http")
async def add_head_support(request: Request, call_next):
    if request.method == "HEAD":
        # HEAD 요청을 GET으로 변환하여 처리
        request.scope["method"] = "GET"
        response = await call_next(request)
        # HEAD 응답에서는 body를 제거
        return Response(
            content="",
            status_code=response.status_code,
            headers=response.headers,
            media_type=response.media_type
        )
    return await call_next(request)

# Supabase DB 초기화
db = SupabaseDB()
consultant = None

@app.on_event("startup")
async def startup_event():
    global consultant
    if db.connect():
        consultant = TravelAIConsultantSupabase(db)
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

@app.get("/", response_class=HTMLResponse)
async def home():
    """메인 페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel AI Consultant (Supabase)</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .badge {
                background: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8em;
                margin-left: 10px;
            }
            #chatbox { 
                border: 2px solid #ddd; 
                height: 400px; 
                overflow-y: scroll; 
                padding: 15px;
                background: #f9f9f9;
                border-radius: 10px;
                margin-bottom: 15px;
            }
            .message { 
                margin: 10px 0; 
                padding: 10px;
                border-radius: 10px;
            }
            .user { 
                background: #e3f2fd; 
                text-align: right;
            }
            .ai { 
                background: #f3e5f5;
            }
            .input-group {
                display: flex;
                gap: 10px;
            }
            input { 
                flex: 1;
                padding: 12px; 
                border: 2px solid #ddd;
                border-radius: 25px;
                font-size: 16px;
            }
            button { 
                padding: 12px 25px; 
                background: #2196F3; 
                color: white; 
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            button:hover {
                background: #1976D2;
            }
            .status {
                text-align: center;
                color: #666;
                font-style: italic;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌟 Travel AI Consultant <span class="badge">Supabase</span></h1>
            <div id="chatbox"></div>
            <div class="input-group">
                <input type="text" id="messageInput" placeholder="여행 관련 질문을 입력하세요..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
            <div class="status" id="status">Connected to Supabase cloud database ☁️</div>
        </div>

        <script>
            let sessionId = null;
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                // Display user message
                addMessage('user', message);
                input.value = '';
                document.getElementById('status').textContent = 'AI is thinking...';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            session_id: sessionId
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        addMessage('ai', data.response);
                        sessionId = data.session_id;
                        document.getElementById('status').textContent = 'Ready for next question';
                    } else {
                        addMessage('ai', 'Sorry, there was an error processing your request.');
                        document.getElementById('status').textContent = 'Error occurred';
                    }
                } catch (error) {
                    addMessage('ai', 'Network error. Please try again.');
                    document.getElementById('status').textContent = 'Network error';
                }
            }
            
            function addMessage(type, text) {
                const chatbox = document.getElementById('chatbox');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + type;
                messageDiv.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'AI') + ':</strong> ' + text.replace(/\\n/g, '<br>');
                chatbox.appendChild(messageDiv);
                chatbox.scrollTop = chatbox.scrollHeight;
            }
            
            // Welcome message
            window.onload = function() {
                addMessage('ai', '안녕하세요! 저는 Supabase 클라우드 데이터베이스와 연동된 여행 상담 AI입니다. 🌟\\n\\n제주도, 부산, 강릉, 경주 등 다양한 국내 여행지에 대해 문의해보세요!');
            }
        </script>
    </body>
    </html>
    """

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
        
        print(f"AI response type: {type(response)}")
        print(f"AI response is None: {response is None}")
        
        if response is None:
            response = "Sorry, I cannot generate a response at this time."
        elif not response or response.strip() == "":
            response = "Sorry, I couldn't generate a proper response. Please try again."
            
        return ChatResponse(response=response, session_id=session_id)
    
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        print(f"Error type: {type(e)}")
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
async def get_hotels(city: str = None, max_price: int = None, min_rating: int = None):
    """호텔 조회 API"""
    try:
        hotels = db.get_hotels(city, max_price, min_rating)
        return {"hotels": hotels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy", 
        "database": "supabase",
        "connection": db.connected
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)