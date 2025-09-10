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
    session_number: str = "N/A"

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
                        addMessage('ai', data.response, data.session_number);
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
            
            function addMessage(type, text, sessionNumber = null) {
                const chatbox = document.getElementById('chatbox');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + type;
                
                let messageText = '<strong>' + (type === 'user' ? 'You' : 'AI') + ':</strong> ' + text.replace(/\\n/g, '<br>');
                if (sessionNumber && type === 'ai' && sessionNumber !== 'N/A') {
                    messageText = '<div style="background: #e3f2fd; padding: 5px; border-radius: 5px; margin-bottom: 5px; font-size: 0.9em;"><strong>상담 #' + sessionNumber + '</strong></div>' + messageText;
                }
                
                messageDiv.innerHTML = messageText;
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
            print(f"Creating new session for message: {request.message[:50]}...")
            session_id = db.create_consultation_session()
            print(f"Created session ID: {session_id}")
        else:
            print(f"Using existing session ID: {request.session_id}")
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
            
        return ChatResponse(response=response, session_id=session_id, session_number="N/A")
    
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏨 Travel AI 데이터 관리</h1>
            
            <div class="tabs">
                <button class="tab active" data-tab="consultation" onclick="showTab('consultation', event)">상담 관리</button>
                <button class="tab" data-tab="excel-mode" onclick="showTab('excel-mode', event)">엑셀 모드</button>
            </div>

            <!-- 상담 관리 탭 -->
            <div id="consultation" class="content active">
                <h2>💬 상담 관리</h2>
                
                <div style="margin-bottom: 20px;">
                    <button onclick="loadConsultationData()" style="background: #4CAF50;">🔄 새로고침</button>
                    <button onclick="clearAllConsultations()" style="background: #f44336;">🗑️ 전체 삭제</button>
            </div>

                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px; height: 500px;">
                    <div>
                        <h3>상담 세션 목록</h3>
                        <div id="consultationSessions" style="border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px;">
                            상담 세션을 선택하세요
                            </div>
                            </div>
                    <div>
                        <h3>상담 내용</h3>
                        <div id="consultationChat" style="border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; background: #f9f9f9;">
                            좌측 목록에서 세션을 클릭하세요
                            </div>
                        <div style="margin-top: 10px;">
                            <button onclick="takeOverConsultation()" style="background: #2196F3;">상담 인계받기</button>
                            <button onclick="sendMessage()" style="background: #4CAF50;">전송</button>
                            </div>
                            </div>
                            </div>
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
                
                // 해당 콘텐츠에 active 추가
                const targetContent = document.getElementById(tabName);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                // 탭별 데이터 로드
                if (tabName === 'excel-mode') {
                    loadExcelData();
                } else if (tabName === 'consultation') {
                    loadConsultationData();
                }
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

            // 상담 데이터 로드
            async function loadConsultationData() {
                try {
                    const response = await fetch('/admin/consultations');
                    const data = await response.json();
                    
                    let html = '';
                    if (data.sessions && data.sessions.length > 0) {
                        data.sessions.forEach(session => {
                            const date = new Date(session.created_at).toLocaleString();
                            const sessionId = session.session_id || session.id;
                            html += `<div class="session-item" onclick="selectSession('${sessionId}')" style="padding: 10px; border: 1px solid #ddd; margin: 5px 0; cursor: pointer; border-radius: 5px;">
                                <strong>상담 세션</strong><br>
                                <small>ID: ${sessionId.substring(0, 8)}...</small><br>
                                <small>${date}</small><br>
                                <small>메시지: ${session.message_count || 0}개</small>
                            </div>`;
                        });
                    } else {
                        html = '<div style="text-align: center; color: #666; padding: 20px;">등록된 상담 세션이 없습니다.</div>';
                    }
                    
                    document.getElementById('consultationSessions').innerHTML = html;
                } catch (error) {
                    document.getElementById('consultationSessions').innerHTML = '<div class="error">상담 데이터 로드 실패</div>';
                }
            }

            // 상담 세션 선택
            async function selectSession(sessionId) {
                console.log('세션 선택:', sessionId);
                
                try {
                    const response = await fetch(`/admin/consultations/${sessionId}`);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('메시지 개수:', data.messages ? data.messages.length : 0);
                    
                    let html = '';
                    if (data.messages && data.messages.length > 0) {
                        data.messages.forEach(msg => {
                            const type = msg.role === 'user' ? 'user' : 'ai';
                            const time = new Date(msg.timestamp).toLocaleString();
                            html += `<div class="message ${type}" style="margin: 10px 0; padding: 10px; border-radius: 10px; background: ${type === 'user' ? '#e3f2fd' : '#f3e5f5'};">
                                <strong>${type === 'user' ? '사용자' : 'AI'}:</strong> ${msg.content}<br>
                                <small style="color: #666;">${time}</small>
                            </div>`;
                        });
                    } else {
                        html = `<div style="text-align: center; color: #666; padding: 20px;">
                            <h4>이 세션에는 메시지가 없습니다</h4>
                            <p>세션 ID: ${sessionId}</p>
                            <p>메인 페이지에서 채팅을 시작해보세요.</p>
                        </div>`;
                    }
                    
                    document.getElementById('consultationChat').innerHTML = html;
                    
                    // 선택된 세션 하이라이트
                    document.querySelectorAll('.session-item').forEach(item => {
                        item.style.background = '';
                    });
                    // 클릭된 세션 아이템 찾기
                    const clickedItem = document.querySelector(`[onclick*="${sessionId}"]`);
                    if (clickedItem) {
                        clickedItem.style.background = '#e3f2fd';
                    }
                } catch (error) {
                    console.error('Error loading consultation messages:', error);
                    document.getElementById('consultationChat').innerHTML = `<div class="error">상담 내용 로드 실패: ${error.message}</div>`;
                }
            }

            // 상담 인계받기
            function takeOverConsultation() {
                alert('상담 인계받기 기능은 준비 중입니다.');
            }

            // 메시지 전송
            function sendMessage() {
                alert('메시지 전송 기능은 준비 중입니다.');
            }

            // 전체 상담 삭제
            async function clearAllConsultations() {
                if (confirm('정말 모든 상담 세션을 삭제하시겠습니까?')) {
                    try {
                        const response = await fetch('/admin/consultations', {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            alert('모든 상담 세션이 삭제되었습니다.');
                            loadConsultationData();
                        } else {
                            alert('삭제 실패');
                        }
                    } catch (error) {
                        alert('삭제에 실패했습니다: ' + error.message);
                    }
                }
            }

            // 페이지 로드 시 데이터 로드
            window.onload = function() {
                loadConsultationData();
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

# 상담 세션 조회 API
@app.get("/admin/consultations")
async def get_consultations():
    """상담 세션 목록 조회"""
    try:
        print("Getting consultation sessions...")
        sessions = db.get_consultation_sessions()
        print(f"Found {len(sessions)} sessions")
        return {"sessions": sessions}
    except Exception as e:
        print(f"Error getting consultations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-consultations")
async def test_consultations():
    """상담 API 테스트"""
    try:
        return {"status": "ok", "message": "Consultation API is working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 특정 상담 세션 조회 API
@app.get("/admin/consultations/{session_id}")
async def get_consultation_session(session_id: str):
    """특정 상담 세션의 메시지 조회"""
    try:
        messages = db.get_consultation_messages(session_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 상담 세션 삭제 API
@app.delete("/admin/consultations")
async def clear_all_consultations():
    """모든 상담 세션 삭제"""
    try:
        result = db.clear_all_consultations()
        if result:
            return {"message": "All consultations cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear consultations")
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