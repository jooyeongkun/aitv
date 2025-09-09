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

@app.get("/admin")
async def admin_page():
    """데이터 관리 페이지"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>데이터 관리 - Travel AI Admin</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px;
            }
            .tabs {
                display: flex;
                margin-bottom: 30px;
                border-bottom: 2px solid #eee;
            }
            .tab {
                padding: 15px 30px;
                cursor: pointer;
                background: #f9f9f9;
                border: none;
                margin-right: 5px;
                border-radius: 8px 8px 0 0;
            }
            .tab.active {
                background: #2196F3;
                color: white;
            }
            .content {
                display: none;
            }
            .content.active {
                display: block;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            button {
                padding: 12px 25px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover {
                background: #45a049;
            }
            .delete-btn {
                background: #f44336;
            }
            .delete-btn:hover {
                background: #da190b;
            }
            .data-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .data-table th, .data-table td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            .data-table th {
                background: #f4f4f4;
                font-weight: bold;
            }
            .data-table tr:nth-child(even) {
                background: #f9f9f9;
            }
            .success {
                color: #4CAF50;
                background: #d4edda;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .error {
                color: #721c24;
                background: #f8d7da;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .form-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            @media (max-width: 768px) {
                .form-container {
                    grid-template-columns: 1fr;
                }
            }
            .excel-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 14px;
            }
            .excel-table th, .excel-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                position: relative;
            }
            .excel-table th {
                background: #f4f4f4;
                font-weight: bold;
                position: sticky;
                top: 0;
            }
            .excel-table tr:nth-child(even) {
                background: #f9f9f9;
            }
            .excel-table tr:hover {
                background: #e3f2fd;
            }
            .editable-cell {
                cursor: pointer;
                min-height: 20px;
                transition: background-color 0.2s;
            }
            .editable-cell:hover {
                background: #e8f5e8;
            }
            .editing {
                background: #fff3cd !important;
            }
            .excel-input {
                width: 100%;
                border: 2px solid #007bff;
                padding: 4px;
                font-size: 14px;
                box-sizing: border-box;
            }
            .action-buttons {
                white-space: nowrap;
            }
            .action-buttons button {
                padding: 4px 8px;
                margin: 1px;
                font-size: 12px;
            }
            .new-row {
                background: #d4edda !important;
                animation: highlight 2s ease-out;
            }
            @keyframes highlight {
                0% { background: #c3e6cb !important; }
                100% { background: #d4edda !important; }
            }
            .consultation-container {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: 20px;
                height: 600px;
                margin-top: 20px;
            }
            .session-list-panel {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                background: #f9f9f9;
            }
            .sessions-list {
                height: 400px;
                overflow-y: auto;
            }
            .session-item {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 8px;
                background: white;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 12px;
            }
            .session-item:hover {
                background: #e3f2fd;
                border-color: #2196F3;
            }
            .session-item.active {
                background: #2196F3;
                color: white;
                border-color: #1976D2;
            }
            .session-item.human-mode {
                border-left: 4px solid #4CAF50;
            }
            .session-time {
                font-weight: bold;
                font-size: 11px;
                color: #666;
                margin-bottom: 5px;
            }
            .session-item.active .session-time {
                color: #e3f2fd;
            }
            .chat-panel {
                border: 2px solid #ddd;
                border-radius: 8px;
                background: white;
                display: flex;
                flex-direction: column;
            }
            .consultation-chat-window {
                height: 100%;
                display: flex;
                flex-direction: column;
            }
            .chat-header-consultation {
                background: #2196F3;
                color: white;
                padding: 15px;
                border-radius: 6px 6px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #ddd;
            }
            .chat-controls button {
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                color: white;
                cursor: pointer;
                font-size: 12px;
                margin-left: 10px;
            }
            .consultation-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: #f8f9fa;
                max-height: 400px;
            }
            .consultation-message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 8px;
                max-width: 80%;
                word-wrap: break-word;
            }
            .consultation-message.user {
                background: #e3f2fd;
                margin-left: auto;
                text-align: right;
            }
            .consultation-message.ai {
                background: #f3e5f5;
                border-left: 3px solid #9c27b0;
            }
            .consultation-message.human {
                background: #e8f5e9;
                border-left: 3px solid #4CAF50;
            }
            .consultation-input {
                padding: 15px;
                border-top: 1px solid #ddd;
                display: flex;
                gap: 10px;
                background: white;
                border-radius: 0 0 6px 6px;
            }
            .consultation-input input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 20px;
                font-size: 14px;
            }
            .consultation-input button {
                padding: 10px 20px;
                border: none;
                border-radius: 20px;
                color: white;
                cursor: pointer;
                font-size: 14px;
            }
            .consultation-placeholder {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #f8f9fa;
                border-radius: 6px;
            }
            @media (max-width: 768px) {
                .consultation-container {
                    grid-template-columns: 1fr;
                    grid-template-rows: 200px 1fr;
                    height: 800px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏨 Travel AI 데이터 관리</h1>
            
            <div class="tabs">
                <button class="tab active" data-tab="packages" onclick="showTab('packages', event)">패키지 관리</button>
                <button class="tab" data-tab="hotels" onclick="showTab('hotels', event)">호텔 관리</button>
                <button class="tab" data-tab="view-data" onclick="showTab('view-data', event)">데이터 조회</button>
                <button class="tab" data-tab="excel-mode" onclick="showTab('excel-mode', event)">엑셀 모드</button>
                <button class="tab" data-tab="consultation" onclick="showTab('consultation', event)">상담 관리</button>
            </div>

            <!-- 패키지 관리 탭 -->
            <div id="packages" class="content active">
                <h2>패키지 관리</h2>
                <div class="form-container">
                    <div>
                        <h3>새 패키지 추가</h3>
                        <form id="packageForm">
                            <div class="form-group">
                                <label for="pkg-name">패키지명</label>
                                <input type="text" id="pkg-name" required>
                            </div>
                            <div class="form-group">
                                <label for="pkg-destination">목적지</label>
                                <input type="text" id="pkg-destination" required>
                            </div>
                            <div class="form-group">
                                <label for="pkg-duration">기간 (일)</label>
                                <input type="number" id="pkg-duration" required>
                            </div>
                            <div class="form-group">
                                <label for="pkg-price">가격 (원)</label>
                                <input type="number" id="pkg-price" required>
                            </div>
                            <div class="form-group">
                                <label for="pkg-category">카테고리</label>
                                <select id="pkg-category" required>
                                    <option value="">선택하세요</option>
                                    <option value="cultural">문화관광</option>
                                    <option value="nature">자연관광</option>
                                    <option value="food">미식여행</option>
                                    <option value="adventure">모험여행</option>
                                    <option value="healing">힐링여행</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="pkg-description">설명</label>
                                <textarea id="pkg-description" rows="3"></textarea>
                            </div>
                            <button type="submit">패키지 추가</button>
                        </form>
                    </div>
                    <div id="packageResult"></div>
                </div>
            </div>

            <!-- 호텔 관리 탭 -->
            <div id="hotels" class="content">
                <h2>호텔 관리</h2>
                <div class="form-container">
                    <div>
                        <h3>새 호텔 추가</h3>
                        <form id="hotelForm">
                            <div class="form-group">
                                <label for="hotel-name">호텔명</label>
                                <input type="text" id="hotel-name" required>
                            </div>
                            <div class="form-group">
                                <label for="hotel-city">도시</label>
                                <input type="text" id="hotel-city" required>
                            </div>
                            <div class="form-group">
                                <label for="hotel-rating">별점</label>
                                <select id="hotel-rating" required>
                                    <option value="">선택하세요</option>
                                    <option value="1">⭐ 1성급</option>
                                    <option value="2">⭐⭐ 2성급</option>
                                    <option value="3">⭐⭐⭐ 3성급</option>
                                    <option value="4">⭐⭐⭐⭐ 4성급</option>
                                    <option value="5">⭐⭐⭐⭐⭐ 5성급</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="hotel-price">1박 가격 (원)</label>
                                <input type="number" id="hotel-price" required>
                            </div>
                            <div class="form-group">
                                <label for="hotel-address">주소</label>
                                <input type="text" id="hotel-address">
                            </div>
                            <div class="form-group">
                                <label for="hotel-amenities">편의시설</label>
                                <textarea id="hotel-amenities" rows="3" placeholder="예: 무료Wi-Fi, 수영장, 피트니스센터"></textarea>
                            </div>
                            <button type="submit">호텔 추가</button>
                        </form>
                    </div>
                    <div id="hotelResult"></div>
                </div>
            </div>

            <!-- 데이터 조회 탭 -->
            <div id="view-data" class="content">
                <h2>데이터 조회</h2>
                <div style="margin-bottom: 20px;">
                    <button onclick="loadAllData()">전체 데이터 새로고침</button>
                </div>
                
                <h3>패키지 목록</h3>
                <div id="packagesList"></div>
                
                <h3>호텔 목록</h3>
                <div id="hotelsList"></div>
            </div>

            <!-- 엑셀 모드 탭 -->
            <div id="excel-mode" class="content">
                <h2>📊 엑셀 모드 (인라인 편집)</h2>
                <p style="color: #666; margin-bottom: 20px;">테이블 셀을 더블클릭하여 직접 편집하세요. Enter키로 저장, Escape키로 취소</p>
                
                <div style="margin-bottom: 30px;">
                    <button onclick="loadExcelData()" style="background: #4CAF50;">🔄 데이터 새로고침</button>
                    <button onclick="addNewRow('packages')" style="background: #2196F3;">➕ 새 패키지 추가</button>
                    <button onclick="addNewRow('hotels')" style="background: #FF9800;">🏨 새 호텔 추가</button>
                </div>
                
                <h3>📦 패키지 목록 (클릭하여 편집)</h3>
                <div id="excelPackagesList" style="margin-bottom: 40px;"></div>
                
                <h3>🏨 호텔 목록 (클릭하여 편집)</h3>
                <div id="excelHotelsList"></div>
            </div>

            <!-- 상담 관리 탭 -->
            <div id="consultation" class="content">
                <h2>💬 상담 관리</h2>
                <div class="consultation-container">
                    <div class="session-list-panel">
                        <h3>상담 세션 목록</h3>
                        <div style="margin-bottom: 15px;">
                            <button onclick="loadConsultationSessions()" style="background: #4CAF50;">🔄 새로고침</button>
                            <button onclick="deleteAllConsultationData()" style="background: #f44336; margin-left: 10px;">🗑️ 전체 삭제</button>
                        </div>
                        <div id="consultationSessionsList" class="sessions-list"></div>
                    </div>
                    <div class="chat-panel">
                        <div id="consultationChatWindow" class="consultation-chat-window" style="display: none;">
                            <div class="chat-header-consultation">
                                <span id="consultationChatTitle">상담 세션을 선택하세요</span>
                                <div class="chat-controls">
                                    <button id="takeOverConsultationBtn" onclick="takeOverConsultation()" style="background: #FF9800;">상담 인계받기</button>
                                </div>
                            </div>
                            <div id="consultationChatMessages" class="consultation-messages"></div>
                            <div class="consultation-input">
                                <input type="text" id="consultationMessageInput" placeholder="고객에게 메시지를 입력하세요..." onkeypress="if(event.key==='Enter') sendConsultationMessage()">
                                <button onclick="sendConsultationMessage()" style="background: #4CAF50;">전송</button>
                            </div>
                        </div>
                        <div id="consultationPlaceholder" class="consultation-placeholder">
                            <div style="text-align: center; color: #666; margin-top: 100px;">
                                <h3>상담 세션을 선택하면 채팅이 표시됩니다</h3>
                                <p>좌측 목록에서 세션을 클릭하세요</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // 탭 전환 함수
            function showTab(tabName, event) {
                console.log('showTab called with:', tabName); // 디버깅용
                
                const tabs = document.querySelectorAll('.tab');
                const contents = document.querySelectorAll('.content');
                
                // 모든 탭에서 active 제거
                tabs.forEach(tab => tab.classList.remove('active'));
                contents.forEach(content => content.classList.remove('active'));
                
                // 클릭된 탭에 active 추가
                if (event && event.target) {
                    event.target.classList.add('active');
                } else {
                    // event가 없는 경우 탭 이름으로 찾아서 active 추가
                    const activeTab = document.querySelector(`button[onclick*="${tabName}"]`);
                    if (activeTab) {
                        activeTab.classList.add('active');
                    }
                }
                
                // 해당 컨텐츠 표시
                const targetContent = document.getElementById(tabName);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                // 기존 자동 새로고침 인터벌 정리
                if (consultationRefreshInterval) {
                    clearInterval(consultationRefreshInterval);
                    consultationRefreshInterval = null;
                }
                
                if (tabName === 'view-data') {
                    loadAllData();
                } else if (tabName === 'excel-mode') {
                    loadExcelData();
                } else if (tabName === 'consultation') {
                    loadConsultationSessions();
                    // 상담 관리 탭에서 3초마다 자동 새로고침
                    consultationRefreshInterval = setInterval(() => {
                        loadConsultationSessions();
                        if (currentConsultationSessionId) {
                            loadConsultationMessages(currentConsultationSessionId);
                        }
                    }, 3000);
                }
            }

            // 패키지 추가
            document.getElementById('packageForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const packageData = {
                    name: document.getElementById('pkg-name').value,
                    destination: document.getElementById('pkg-destination').value,
                    duration: parseInt(document.getElementById('pkg-duration').value),
                    price: parseInt(document.getElementById('pkg-price').value),
                    category: document.getElementById('pkg-category').value,
                    description: document.getElementById('pkg-description').value
                };

                try {
                    const response = await fetch('/admin/packages', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(packageData)
                    });

                    const result = await response.json();
                    const resultDiv = document.getElementById('packageResult');

                    if (response.ok) {
                        resultDiv.innerHTML = '<div class="success">패키지가 성공적으로 추가되었습니다!</div>';
                        document.getElementById('packageForm').reset();
                    } else {
                        resultDiv.innerHTML = `<div class="error">오류: ${result.detail || result.message}</div>`;
                    }
                } catch (error) {
                    document.getElementById('packageResult').innerHTML = `<div class="error">네트워크 오류: ${error.message}</div>`;
                }
            });

            // 호텔 추가
            document.getElementById('hotelForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const hotelData = {
                    name: document.getElementById('hotel-name').value,
                    city: document.getElementById('hotel-city').value,
                    star_rating: parseInt(document.getElementById('hotel-rating').value),
                    price_per_night: parseInt(document.getElementById('hotel-price').value),
                    address: document.getElementById('hotel-address').value,
                    amenities: document.getElementById('hotel-amenities').value
                };

                try {
                    const response = await fetch('/admin/hotels', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(hotelData)
                    });

                    const result = await response.json();
                    const resultDiv = document.getElementById('hotelResult');

                    if (response.ok) {
                        resultDiv.innerHTML = '<div class="success">호텔이 성공적으로 추가되었습니다!</div>';
                        document.getElementById('hotelForm').reset();
                    } else {
                        resultDiv.innerHTML = `<div class="error">오류: ${result.detail || result.message}</div>`;
                    }
                } catch (error) {
                    document.getElementById('hotelResult').innerHTML = `<div class="error">네트워크 오류: ${error.message}</div>`;
                }
            });

            // 전체 데이터 로드
            async function loadAllData() {
                await loadPackages();
                await loadHotels();
            }

            // 패키지 데이터 로드
            async function loadPackages() {
                try {
                    const response = await fetch('/packages');
                    const data = await response.json();
                    
                    let html = '<table class="data-table"><tr><th>패키지명</th><th>목적지</th><th>기간</th><th>가격</th><th>카테고리</th><th>작업</th></tr>';
                    
                    if (data.packages && data.packages.length > 0) {
                        data.packages.forEach(pkg => {
                            html += `<tr>
                                <td>${pkg.name || 'N/A'}</td>
                                <td>${pkg.destination || 'N/A'}</td>
                                <td>${pkg.duration || 'N/A'}일</td>
                                <td>${(pkg.price || 0).toLocaleString()}원</td>
                                <td>${pkg.category || 'N/A'}</td>
                                <td>
                                    <button onclick="editPackage(${pkg.id}, '${(pkg.name || '').replace(/'/g, '\\'')}', '${(pkg.destination || '').replace(/'/g, '\\'')}', ${pkg.duration || 0}, ${pkg.price || 0}, '${pkg.category || ''}', '${(pkg.description || '').replace(/'/g, '\\'')}')">수정</button>
                                    <button class="delete-btn" onclick="deletePackage(${pkg.id})">삭제</button>
                                </td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="6">등록된 패키지가 없습니다.</td></tr>';
                    }
                    
                    html += '</table>';
                    document.getElementById('packagesList').innerHTML = html;
                } catch (error) {
                    document.getElementById('packagesList').innerHTML = '<div class="error">패키지 데이터 로드 실패</div>';
                }
            }

            // 호텔 데이터 로드
            async function loadHotels() {
                try {
                    const response = await fetch('/hotels');
                    const data = await response.json();
                    
                    let html = '<table class="data-table"><tr><th>호텔명</th><th>도시</th><th>별점</th><th>1박 가격</th><th>작업</th></tr>';
                    
                    if (data.hotels && data.hotels.length > 0) {
                        data.hotels.forEach(hotel => {
                            html += `<tr>
                                <td>${hotel.name || 'N/A'}</td>
                                <td>${hotel.city || 'N/A'}</td>
                                <td>${'⭐'.repeat(hotel.star_rating || 0)} ${hotel.star_rating || 0}성급</td>
                                <td>${(hotel.price_per_night || 0).toLocaleString()}원</td>
                                <td>
                                    <button onclick="editHotel(${hotel.id}, '${(hotel.name || '').replace(/'/g, '\\'')}', '${(hotel.city || '').replace(/'/g, '\\'')}', ${hotel.star_rating || 0}, ${hotel.price_per_night || 0}, '${(hotel.address || '').replace(/'/g, '\\'')}', '${(hotel.amenities || '').replace(/'/g, '\\'')}')">수정</button>
                                    <button class="delete-btn" onclick="deleteHotel(${hotel.id})">삭제</button>
                                </td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="5">등록된 호텔이 없습니다.</td></tr>';
                    }
                    
                    html += '</table>';
                    document.getElementById('hotelsList').innerHTML = html;
                } catch (error) {
                    document.getElementById('hotelsList').innerHTML = '<div class="error">호텔 데이터 로드 실패</div>';
                }
            }

            // 패키지 삭제
            async function deletePackage(id) {
                if (confirm('정말 이 패키지를 삭제하시겠습니까?')) {
                    try {
                        const response = await fetch(`/admin/packages/${id}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            alert('패키지가 삭제되었습니다.');
                            loadPackages();
                        } else {
                            alert('삭제 실패');
                        }
                    } catch (error) {
                        alert('네트워크 오류');
                    }
                }
            }

            // 호텔 삭제
            async function deleteHotel(id) {
                if (confirm('정말 이 호텔을 삭제하시겠습니까?')) {
                    try {
                        const response = await fetch(`/admin/hotels/${id}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            alert('호텔이 삭제되었습니다.');
                            loadHotels();
                        } else {
                            alert('삭제 실패');
                        }
                    } catch (error) {
                        alert('네트워크 오류');
                    }
                }
            }

            // 패키지 수정
            function editPackage(id, name, destination, duration, price, category, description) {
                // 수정 폼으로 데이터 채우기
                document.getElementById('pkg-name').value = name;
                document.getElementById('pkg-destination').value = destination;
                document.getElementById('pkg-duration').value = duration;
                document.getElementById('pkg-price').value = price;
                document.getElementById('pkg-category').value = category;
                document.getElementById('pkg-description').value = description;

                // 패키지 관리 탭으로 이동
                showTab('packages');
                
                // 폼 제출 이벤트 변경
                const form = document.getElementById('packageForm');
                const submitButton = form.querySelector('button[type="submit"]');
                submitButton.textContent = '수정 완료';
                submitButton.style.background = '#FF9800';
                
                // 기존 이벤트 리스너 제거 후 새로운 이벤트 리스너 추가
                const newForm = form.cloneNode(true);
                form.parentNode.replaceChild(newForm, form);
                
                newForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const packageData = {
                        name: document.getElementById('pkg-name').value,
                        destination: document.getElementById('pkg-destination').value,
                        duration: parseInt(document.getElementById('pkg-duration').value),
                        price: parseInt(document.getElementById('pkg-price').value),
                        category: document.getElementById('pkg-category').value,
                        description: document.getElementById('pkg-description').value
                    };

                    try {
                        const response = await fetch(`/admin/packages/${id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(packageData)
                        });

                        const result = await response.json();
                        const resultDiv = document.getElementById('packageResult');

                        if (response.ok) {
                            resultDiv.innerHTML = '<div class="success">패키지가 성공적으로 수정되었습니다!</div>';
                            resetPackageForm();
                            loadAllData();
                        } else {
                            resultDiv.innerHTML = `<div class="error">오류: ${result.detail || result.message}</div>`;
                        }
                    } catch (error) {
                        document.getElementById('packageResult').innerHTML = `<div class="error">네트워크 오류: ${error.message}</div>`;
                    }
                });
                
                // 취소 버튼 추가
                if (!form.parentNode.querySelector('.cancel-btn')) {
                    const cancelButton = document.createElement('button');
                    cancelButton.textContent = '취소';
                    cancelButton.className = 'cancel-btn';
                    cancelButton.type = 'button';
                    cancelButton.style.background = '#666';
                    cancelButton.onclick = resetPackageForm;
                    submitButton.parentNode.insertBefore(cancelButton, submitButton.nextSibling);
                }
            }

            // 호텔 수정
            function editHotel(id, name, city, star_rating, price_per_night, address, amenities) {
                // 수정 폼으로 데이터 채우기
                document.getElementById('hotel-name').value = name;
                document.getElementById('hotel-city').value = city;
                document.getElementById('hotel-rating').value = star_rating;
                document.getElementById('hotel-price').value = price_per_night;
                document.getElementById('hotel-address').value = address;
                document.getElementById('hotel-amenities').value = amenities;

                // 호텔 관리 탭으로 이동
                showTab('hotels');
                
                // 폼 제출 이벤트 변경
                const form = document.getElementById('hotelForm');
                const submitButton = form.querySelector('button[type="submit"]');
                submitButton.textContent = '수정 완료';
                submitButton.style.background = '#FF9800';
                
                // 기존 이벤트 리스너 제거 후 새로운 이벤트 리스너 추가
                const newForm = form.cloneNode(true);
                form.parentNode.replaceChild(newForm, form);
                
                newForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const hotelData = {
                        name: document.getElementById('hotel-name').value,
                        city: document.getElementById('hotel-city').value,
                        star_rating: parseInt(document.getElementById('hotel-rating').value),
                        price_per_night: parseInt(document.getElementById('hotel-price').value),
                        address: document.getElementById('hotel-address').value,
                        amenities: document.getElementById('hotel-amenities').value
                    };

                    try {
                        const response = await fetch(`/admin/hotels/${id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(hotelData)
                        });

                        const result = await response.json();
                        const resultDiv = document.getElementById('hotelResult');

                        if (response.ok) {
                            resultDiv.innerHTML = '<div class="success">호텔이 성공적으로 수정되었습니다!</div>';
                            resetHotelForm();
                            loadAllData();
                        } else {
                            resultDiv.innerHTML = `<div class="error">오류: ${result.detail || result.message}</div>`;
                        }
                    } catch (error) {
                        document.getElementById('hotelResult').innerHTML = `<div class="error">네트워크 오류: ${error.message}</div>`;
                    }
                });
                
                // 취소 버튼 추가
                if (!form.parentNode.querySelector('.cancel-btn')) {
                    const cancelButton = document.createElement('button');
                    cancelButton.textContent = '취소';
                    cancelButton.className = 'cancel-btn';
                    cancelButton.type = 'button';
                    cancelButton.style.background = '#666';
                    cancelButton.onclick = resetHotelForm;
                    submitButton.parentNode.insertBefore(cancelButton, submitButton.nextSibling);
                }
            }

            // 패키지 폼 리셋
            function resetPackageForm() {
                const form = document.getElementById('packageForm');
                const submitButton = form.querySelector('button[type="submit"]');
                const cancelButton = form.parentNode.querySelector('.cancel-btn');
                
                form.reset();
                submitButton.textContent = '패키지 추가';
                submitButton.style.background = '#4CAF50';
                
                if (cancelButton) {
                    cancelButton.remove();
                }
                
                // 원래 이벤트 리스너로 복원
                location.reload();
            }

            // 호텔 폼 리셋
            function resetHotelForm() {
                const form = document.getElementById('hotelForm');
                const submitButton = form.querySelector('button[type="submit"]');
                const cancelButton = form.parentNode.querySelector('.cancel-btn');
                
                form.reset();
                submitButton.textContent = '호텔 추가';
                submitButton.style.background = '#4CAF50';
                
                if (cancelButton) {
                    cancelButton.remove();
                }
                
                // 원래 이벤트 리스너로 복원
                location.reload();
            }

            // 엑셀 모드 데이터 로드
            async function loadExcelData() {
                await loadExcelPackages();
                await loadExcelHotels();
            }

            // 엑셀 패키지 테이블 로드
            async function loadExcelPackages() {
                try {
                    const response = await fetch('/packages');
                    const data = await response.json();
                    
                    let html = '<table class="excel-table"><tr><th>ID</th><th>패키지명</th><th>목적지</th><th>기간(일)</th><th>가격(원)</th><th>카테고리</th><th>설명</th><th>작업</th></tr>';
                    
                    if (data.packages && data.packages.length > 0) {
                        data.packages.forEach(pkg => {
                            html += `<tr data-id="${pkg.id}" data-type="package">
                                <td>${pkg.id}</td>
                                <td class="editable-cell" data-field="name" onclick="editCell(this)">${pkg.name || ''}</td>
                                <td class="editable-cell" data-field="destination" onclick="editCell(this)">${pkg.destination || ''}</td>
                                <td class="editable-cell" data-field="duration" onclick="editCell(this)">${pkg.duration || ''}</td>
                                <td class="editable-cell" data-field="price" onclick="editCell(this)">${pkg.price || ''}</td>
                                <td class="editable-cell" data-field="category" onclick="editCell(this)">${pkg.category || ''}</td>
                                <td class="editable-cell" data-field="description" onclick="editCell(this)">${pkg.description || ''}</td>
                                <td class="action-buttons">
                                    <button class="delete-btn" onclick="deleteExcelRow(${pkg.id}, 'packages')">삭제</button>
                                </td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="8">등록된 패키지가 없습니다.</td></tr>';
                    }
                    
                    html += '</table>';
                    document.getElementById('excelPackagesList').innerHTML = html;
                } catch (error) {
                    document.getElementById('excelPackagesList').innerHTML = '<div class="error">패키지 데이터 로드 실패</div>';
                }
            }

            // 엑셀 호텔 테이블 로드
            async function loadExcelHotels() {
                try {
                    const response = await fetch('/hotels');
                    const data = await response.json();
                    
                    let html = '<table class="excel-table"><tr><th>ID</th><th>호텔명</th><th>도시</th><th>별점</th><th>1박가격(원)</th><th>주소</th><th>편의시설</th><th>작업</th></tr>';
                    
                    if (data.hotels && data.hotels.length > 0) {
                        data.hotels.forEach(hotel => {
                            html += `<tr data-id="${hotel.id}" data-type="hotel">
                                <td>${hotel.id}</td>
                                <td class="editable-cell" data-field="name" onclick="editCell(this)">${hotel.name || ''}</td>
                                <td class="editable-cell" data-field="city" onclick="editCell(this)">${hotel.city || ''}</td>
                                <td class="editable-cell" data-field="star_rating" onclick="editCell(this)">${hotel.star_rating || ''}</td>
                                <td class="editable-cell" data-field="price_per_night" onclick="editCell(this)">${hotel.price_per_night || ''}</td>
                                <td class="editable-cell" data-field="address" onclick="editCell(this)">${hotel.address || ''}</td>
                                <td class="editable-cell" data-field="amenities" onclick="editCell(this)">${hotel.amenities || ''}</td>
                                <td class="action-buttons">
                                    <button class="delete-btn" onclick="deleteExcelRow(${hotel.id}, 'hotels')">삭제</button>
                                </td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="8">등록된 호텔이 없습니다.</td></tr>';
                    }
                    
                    html += '</table>';
                    document.getElementById('excelHotelsList').innerHTML = html;
                } catch (error) {
                    document.getElementById('excelHotelsList').innerHTML = '<div class="error">호텔 데이터 로드 실패</div>';
                }
            }

            // 셀 편집 함수
            function editCell(cell) {
                if (cell.classList.contains('editing')) return;
                
                const originalValue = cell.textContent;
                const field = cell.getAttribute('data-field');
                
                cell.classList.add('editing');
                cell.innerHTML = `<input type="text" class="excel-input" value="${originalValue}" onblur="saveCell(this, '${originalValue}')" onkeydown="handleCellKeydown(event, this, '${originalValue}')">`;
                cell.querySelector('input').focus();
                cell.querySelector('input').select();
            }

            // 키보드 이벤트 처리
            function handleCellKeydown(event, input, originalValue) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    saveCell(input, originalValue);
                } else if (event.key === 'Escape') {
                    cancelEdit(input, originalValue);
                }
            }

            // 셀 저장
            async function saveCell(input, originalValue) {
                const cell = input.parentElement;
                const newValue = input.value.trim();
                const row = cell.parentElement;
                const id = row.getAttribute('data-id');
                const type = row.getAttribute('data-type');
                const field = cell.getAttribute('data-field');
                
                if (newValue === originalValue) {
                    cancelEdit(input, originalValue);
                    return;
                }
                
                try {
                    const endpoint = type === 'package' ? `/admin/packages/${id}` : `/admin/hotels/${id}`;
                    const updateData = {};
                    updateData[field] = field === 'duration' || field === 'price' || field === 'star_rating' || field === 'price_per_night' ? 
                        parseInt(newValue) || 0 : newValue;
                    
                    const response = await fetch(endpoint, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(updateData)
                    });
                    
                    if (response.ok) {
                        cell.textContent = newValue;
                        cell.classList.remove('editing');
                        // 성공 애니메이션
                        cell.style.background = '#d4edda';
                        setTimeout(() => {
                            cell.style.background = '';
                        }, 1000);
                    } else {
                        throw new Error('저장 실패');
                    }
                } catch (error) {
                    alert('저장에 실패했습니다: ' + error.message);
                    cancelEdit(input, originalValue);
                }
            }

            // 편집 취소
            function cancelEdit(input, originalValue) {
                const cell = input.parentElement;
                cell.textContent = originalValue;
                cell.classList.remove('editing');
            }

            // 새 행 추가
            async function addNewRow(type) {
                const defaultData = type === 'packages' ? {
                    name: '새 패키지',
                    destination: '목적지',
                    duration: 3,
                    price: 100000,
                    category: 'cultural',
                    description: '설명을 입력하세요'
                } : {
                    name: '새 호텔',
                    city: '도시',
                    star_rating: 3,
                    price_per_night: 80000,
                    address: '주소를 입력하세요',
                    amenities: '편의시설을 입력하세요'
                };
                
                try {
                    const endpoint = `/admin/${type}`;
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(defaultData)
                    });
                    
                    if (response.ok) {
                        loadExcelData();
                        alert('새 항목이 추가되었습니다. 이제 셀을 클릭하여 편집하세요.');
                    } else {
                        alert('추가 실패');
                    }
                } catch (error) {
                    alert('추가에 실패했습니다: ' + error.message);
                }
            }

            // 엑셀 모드에서 행 삭제
            async function deleteExcelRow(id, type) {
                if (!confirm('정말 삭제하시겠습니까?')) return;
                
                try {
                    const endpoint = `/admin/${type}/${id}`;
                    const response = await fetch(endpoint, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        loadExcelData();
                        alert('삭제되었습니다.');
                    } else {
                        alert('삭제 실패');
                    }
                } catch (error) {
                    alert('삭제에 실패했습니다: ' + error.message);
                }
            }

            // 상담 관리 관련 변수
            let currentConsultationSessionId = null;
            let isHumanConsultationMode = false;
            let consultationRefreshInterval = null;

            // 상담 세션 목록 로드 (최신순)
            async function loadConsultationSessions() {
                try {
                    const response = await fetch('/consultation/sessions');
                    const sessions = await response.json();
                    
                    const listContainer = document.getElementById('consultationSessionsList');
                    listContainer.innerHTML = '';
                    
                    if (sessions.length === 0) {
                        listContainer.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">현재 활성 상담 세션이 없습니다.</div>';
                        return;
                    }
                    
                    // 데이터베이스에서 이미 최신순으로 정렬되어 옴
                    
                    sessions.forEach(session => {
                        const sessionItem = document.createElement('div');
                        sessionItem.className = `session-item ${session.human_mode ? 'human-mode' : ''}`;
                        sessionItem.onclick = () => selectConsultationSession(session.session_id);
                        
                        const sessionTime = new Date(session.created_at).toLocaleString('ko-KR', {
                            year: 'numeric',
                            month: '2-digit', 
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                        
                        sessionItem.innerHTML = `
                            <div class="session-time">${sessionTime}</div>
                            <div>ID: ${session.session_id.substring(0, 8)}...</div>
                            <div style="margin-top: 5px;">
                                <span style="font-size: 11px; padding: 2px 6px; border-radius: 10px; background: ${session.human_mode ? '#4CAF50' : '#2196F3'}; color: white;">
                                    ${session.human_mode ? '👨‍💼 인간' : '🤖 AI'}
                                </span>
                                <button onclick="deleteConsultationSession('${session.session_id}', event)" style="font-size: 12px; background: #f44336; color: white; border: none; border-radius: 3px; padding: 2px 5px; margin-left: 10px; cursor: pointer;">🗑️</button>
                            </div>
                        `;
                        
                        listContainer.appendChild(sessionItem);
                    });
                } catch (error) {
                    console.error('상담 세션 목록 로드 실패:', error);
                    document.getElementById('consultationSessionsList').innerHTML = '<div style="color: red; padding: 20px;">세션 목록 로드에 실패했습니다.</div>';
                }
            }

            // 상담 세션 선택
            async function selectConsultationSession(sessionId) {
                // 기존 활성 세션 비활성화
                document.querySelectorAll('.session-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // 현재 세션 활성화
                event.target.closest('.session-item').classList.add('active');
                
                currentConsultationSessionId = sessionId;
                
                // 채팅창 표시
                document.getElementById('consultationPlaceholder').style.display = 'none';
                document.getElementById('consultationChatWindow').style.display = 'flex';
                document.getElementById('consultationChatTitle').textContent = `상담 세션: ${sessionId.substring(0, 8)}...`;
                
                // 세션 상태 확인 및 메시지 로드
                await loadConsultationMessages();
                await checkConsultationSessionStatus();
            }

            // 상담 메시지 로드
            async function loadConsultationMessages() {
                if (!currentConsultationSessionId) return;
                
                try {
                    const response = await fetch(`/consultation/sessions/${currentConsultationSessionId}/messages`);
                    const messages = await response.json();
                    
                    const messagesContainer = document.getElementById('consultationChatMessages');
                    messagesContainer.innerHTML = '';
                    
                    messages.forEach(msg => {
                        if (msg.user_message) {
                            const userMsg = document.createElement('div');
                            userMsg.className = 'consultation-message user';
                            userMsg.innerHTML = `<div style="font-size: 12px; color: #666; margin-bottom: 5px;">${new Date(msg.created_at).toLocaleTimeString()}</div><strong>고객:</strong> ${msg.user_message}`;
                            messagesContainer.appendChild(userMsg);
                        }
                        
                        if (msg.ai_response) {
                            const aiMsg = document.createElement('div');
                            aiMsg.className = 'consultation-message ai';
                            aiMsg.innerHTML = `<div style="font-size: 12px; color: #666; margin-bottom: 5px;">${new Date(msg.created_at).toLocaleTimeString()}</div><strong>🤖 AI:</strong> ${msg.ai_response}`;
                            messagesContainer.appendChild(aiMsg);
                        }
                        
                        if (msg.human_response) {
                            const humanMsg = document.createElement('div');
                            humanMsg.className = 'consultation-message human';
                            humanMsg.innerHTML = `<div style="font-size: 12px; color: #666; margin-bottom: 5px;">${new Date(msg.created_at).toLocaleTimeString()}</div><strong>👨‍💼 상담사:</strong> ${msg.human_response}`;
                            messagesContainer.appendChild(humanMsg);
                        }
                    });
                    
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                } catch (error) {
                    console.error('메시지 로드 실패:', error);
                }
            }

            // 상담 세션 상태 확인
            async function checkConsultationSessionStatus() {
                if (!currentConsultationSessionId) return;
                
                try {
                    const response = await fetch(`/consultation/sessions/${currentConsultationSessionId}/status`);
                    const status = await response.json();
                    
                    isHumanConsultationMode = status?.human_mode || false;
                    
                    const takeOverBtn = document.getElementById('takeOverConsultationBtn');
                    if (isHumanConsultationMode) {
                        takeOverBtn.style.display = 'none';
                    } else {
                        takeOverBtn.style.display = 'inline-block';
                    }
                } catch (error) {
                    console.error('세션 상태 확인 실패:', error);
                }
            }

            // 상담 인계받기
            async function takeOverConsultation() {
                if (!currentConsultationSessionId) return;
                
                try {
                    const response = await fetch(`/consultation/sessions/${currentConsultationSessionId}/takeover`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        isHumanConsultationMode = true;
                        document.getElementById('takeOverConsultationBtn').style.display = 'none';
                        alert('상담을 인계받았습니다! 이제 고객과 직접 대화할 수 있습니다.');
                        loadConsultationSessions(); // 세션 목록 새로고침
                    } else {
                        alert('상담 인계 실패');
                    }
                } catch (error) {
                    console.error('상담 인계 실패:', error);
                    alert('네트워크 오류');
                }
            }

            // 상담사 메시지 전송
            async function sendConsultationMessage() {
                if (!currentConsultationSessionId || !isHumanConsultationMode) {
                    alert('먼저 상담을 인계받아 주세요.');
                    return;
                }
                
                const input = document.getElementById('consultationMessageInput');
                const message = input.value.trim();
                if (!message) return;
                
                try {
                    const response = await fetch(`/consultation/sessions/${currentConsultationSessionId}/message`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            sender_type: 'human'
                        })
                    });
                    
                    if (response.ok) {
                        input.value = '';
                        loadConsultationMessages(); // 메시지 새로고침
                    } else {
                        alert('메시지 전송 실패');
                    }
                } catch (error) {
                    console.error('메시지 전송 실패:', error);
                    alert('네트워크 오류');
                }
            }

            // 개별 상담 세션 삭제
            async function deleteConsultationSession(sessionId, event) {
                event.stopPropagation(); // 세션 선택 방지
                
                if (!confirm('이 상담 세션과 모든 메시지를 삭제하시겠습니까?')) {
                    return;
                }
                
                try {
                    const response = await fetch(`/consultation/sessions/${sessionId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        alert('상담 세션이 삭제되었습니다.');
                        loadConsultationSessions(); // 목록 새로고침
                        
                        // 현재 선택된 세션이 삭제된 경우 채팅창 숨기기
                        if (currentConsultationSessionId === sessionId) {
                            document.getElementById('consultationChatWindow').style.display = 'none';
                            document.getElementById('consultationPlaceholder').style.display = 'block';
                            currentConsultationSessionId = null;
                        }
                    } else {
                        alert('상담 세션 삭제에 실패했습니다.');
                    }
                } catch (error) {
                    console.error('상담 세션 삭제 실패:', error);
                    alert('네트워크 오류');
                }
            }

            // 모든 상담 데이터 삭제
            async function deleteAllConsultationData() {
                if (!confirm('⚠️ 모든 상담 세션과 메시지를 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다!')) {
                    return;
                }
                
                if (!confirm('정말로 모든 상담 데이터를 삭제하시겠습니까?')) {
                    return;
                }
                
                try {
                    const response = await fetch('/consultation/sessions', {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        alert('모든 상담 데이터가 삭제되었습니다.');
                        loadConsultationSessions(); // 목록 새로고침
                        
                        // 채팅창 숨기기
                        document.getElementById('consultationChatWindow').style.display = 'none';
                        document.getElementById('consultationPlaceholder').style.display = 'block';
                        currentConsultationSessionId = null;
                    } else {
                        alert('상담 데이터 삭제에 실패했습니다.');
                    }
                } catch (error) {
                    console.error('상담 데이터 삭제 실패:', error);
                    alert('네트워크 오류');
                }
            }

            // 페이지 로드 시 데이터 로드
            window.onload = function() {
                loadAllData();
            }
        </script>
    </body>
    </html>
    """)

# 패키지 추가 API
@app.post("/admin/packages")
async def add_package(package_data: dict):
    """패키지 추가 API"""
    try:
        result = db.add_package(package_data)
        if result:
            return {"message": "Package added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add package")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 호텔 추가 API
@app.post("/admin/hotels")
async def add_hotel(hotel_data: dict):
    """호텔 추가 API"""
    try:
        result = db.add_hotel(hotel_data)
        if result:
            return {"message": "Hotel added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add hotel")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 패키지 삭제 API
@app.delete("/admin/packages/{package_id}")
async def delete_package(package_id: int):
    """패키지 삭제 API"""
    try:
        result = db.delete_package(package_id)
        if result:
            return {"message": "Package deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Package not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 호텔 삭제 API
@app.delete("/admin/hotels/{hotel_id}")
async def delete_hotel(hotel_id: int):
    """호텔 삭제 API"""
    try:
        result = db.delete_hotel(hotel_id)
        if result:
            return {"message": "Hotel deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Hotel not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 패키지 수정 API
@app.put("/admin/packages/{package_id}")
async def update_package(package_id: int, package_data: dict):
    """패키지 수정 API"""
    try:
        result = db.update_package(package_id, package_data)
        if result:
            return {"message": "Package updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Package not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 호텔 수정 API
@app.put("/admin/hotels/{hotel_id}")
async def update_hotel(hotel_id: int, hotel_data: dict):
    """호텔 수정 API"""
    try:
        result = db.update_hotel(hotel_id, hotel_data)
        if result:
            return {"message": "Hotel updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Hotel not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 상담 관리용 API 엔드포인트들
@app.get("/consultation/sessions")
async def get_consultation_sessions():
    """활성 상담 세션 목록 조회"""
    try:
        sessions = db.get_active_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consultation/sessions/{session_id}/messages")
async def get_consultation_session_messages(session_id: str):
    """세션 메시지 조회"""
    try:
        messages = db.get_session_messages(session_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consultation/sessions/{session_id}/status")
async def get_consultation_session_status(session_id: str):
    """세션 상태 조회"""
    try:
        status = db.get_session_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consultation/sessions/{session_id}/takeover")
async def takeover_consultation_session(session_id: str):
    """상담 세션 인계받기"""
    try:
        result = db.set_session_human_mode(session_id, True)
        if result:
            return {"message": "Session taken over successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to take over session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consultation/sessions/{session_id}/message")
async def send_consultation_message(session_id: str, request: dict):
    """상담사 메시지 전송"""
    try:
        message = request.get("message")
        sender_type = request.get("sender_type", "human")
        
        if sender_type == "human":
            db.save_consultation_message(session_id, "", None, message, "human")
        
        return {"message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/consultation/sessions/{session_id}")
async def delete_consultation_session(session_id: str):
    """개별 상담 세션 삭제"""
    try:
        result = db.delete_consultation_session(session_id)
        if result:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/consultation/sessions")
async def delete_all_consultation_sessions():
    """모든 상담 데이터 삭제"""
    try:
        result = db.delete_all_consultation_data()
        if result:
            return {"message": "All consultation data deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete consultation data")
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
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)