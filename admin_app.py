"""
여행사 관리자 대시보드 (FastAPI)
패키지와 호텔 CRUD 관리 시스템
"""

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from datetime import datetime
from typing import Optional
import uvicorn

app = FastAPI(title="여행사 관리자 대시보드")

def get_db_connection():
    """SQLite 데이터베이스 연결"""
    conn = sqlite3.connect('travel_consultation.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def admin_home():
    """관리자 메인 페이지"""
    conn = get_db_connection()
    
    # 통계 정보 조회
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM packages")
    package_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM hotels")
    hotel_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM consultation_sessions")
    session_count = cursor.fetchone()['count']
    
    conn.close()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>여행사 관리자 대시보드</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .menu {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .menu-item {{ background: white; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.2s; }}
            .menu-item:hover {{ transform: translateY(-2px); }}
            .menu-item a {{ text-decoration: none; color: #333; }}
            .menu-item h3 {{ color: #007bff; margin-bottom: 10px; }}
            .icon {{ font-size: 3em; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏢 여행사 관리자 대시보드</h1>
                <p>여행 패키지와 호텔 정보를 관리하세요</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{package_count}</div>
                    <div>등록된 패키지</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{hotel_count}</div>
                    <div>등록된 호텔</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{session_count}</div>
                    <div>상담 세션</div>
                </div>
            </div>
            
            <div class="menu">
                <div class="menu-item">
                    <a href="/packages">
                        <div class="icon">📦</div>
                        <h3>패키지 관리</h3>
                        <p>여행 패키지 추가, 수정, 삭제</p>
                    </a>
                </div>
                <div class="menu-item">
                    <a href="/hotels">
                        <div class="icon">🏨</div>
                        <h3>호텔 관리</h3>
                        <p>호텔 정보 추가, 수정, 삭제</p>
                    </a>
                </div>
                <div class="menu-item">
                    <a href="/consultations">
                        <div class="icon">💬</div>
                        <h3>상담 내역</h3>
                        <p>고객 상담 기록 조회</p>
                    </a>
                </div>
                <div class="menu-item">
                    <a href="http://localhost:8000" target="_blank">
                        <div class="icon">🤖</div>
                        <h3>AI 상담 서비스</h3>
                        <p>고객용 AI 상담 페이지</p>
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/packages", response_class=HTMLResponse)
async def packages_list():
    """패키지 목록 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM packages ORDER BY created_at DESC")
    packages = cursor.fetchall()
    conn.close()
    
    packages_html = ""
    for package in packages:
        packages_html += f"""
        <tr>
            <td>{package['id']}</td>
            <td>{package['name']}</td>
            <td>{package['destination']}</td>
            <td>{package['category']}</td>
            <td>{package['duration_days']}일</td>
            <td>{package['price']:,}원</td>
            <td>
                <button onclick="editPackage({package['id']})" class="btn-edit">수정</button>
                <button onclick="deletePackage({package['id']})" class="btn-delete">삭제</button>
            </td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>패키지 관리</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-edit {{ background: #28a745; color: white; margin-right: 5px; }}
            .btn-delete {{ background: #dc3545; color: white; }}
            .btn:hover {{ opacity: 0.8; }}
            table {{ width: 100%; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .back-btn {{ background: #6c757d; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>📦 패키지 관리</h1>
                    <p>여행 패키지 정보를 관리하세요</p>
                </div>
                <div>
                    <a href="/" class="btn back-btn">← 대시보드</a>
                    <a href="/packages/add" class="btn btn-primary">+ 패키지 추가</a>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>패키지명</th>
                        <th>목적지</th>
                        <th>카테고리</th>
                        <th>기간</th>
                        <th>가격</th>
                        <th>관리</th>
                    </tr>
                </thead>
                <tbody>
                    {packages_html}
                </tbody>
            </table>
        </div>
        
        <script>
            function editPackage(id) {{
                window.location.href = '/packages/edit/' + id;
            }}
            
            function deletePackage(id) {{
                if (confirm('이 패키지를 삭제하시겠습니까?')) {{
                    fetch('/packages/delete/' + id, {{
                        method: 'POST'
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            location.reload();
                        }} else {{
                            alert('삭제 중 오류가 발생했습니다.');
                        }}
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.get("/packages/add", response_class=HTMLResponse)
async def add_package_form():
    """패키지 추가 폼"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>패키지 추가</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
            textarea { height: 100px; resize: vertical; }
            .btn { padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
            .btn-primary { background: #007bff; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn:hover { opacity: 0.8; }
            .header { margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📦 새 패키지 추가</h1>
                <p>새로운 여행 패키지 정보를 입력하세요</p>
            </div>
            
            <div class="form-container">
                <form action="/packages/add" method="post">
                    <div class="form-group">
                        <label for="name">패키지명 *</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="destination">목적지 *</label>
                        <input type="text" id="destination" name="destination" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="category">카테고리 *</label>
                        <select id="category" name="category" required>
                            <option value="">선택하세요</option>
                            <option value="힐링">힐링</option>
                            <option value="관광">관광</option>
                            <option value="자연">자연</option>
                            <option value="문화">문화</option>
                            <option value="맛집">맛집</option>
                            <option value="액티비티">액티비티</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="duration_days">여행 기간 (일) *</label>
                        <input type="number" id="duration_days" name="duration_days" min="1" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="price">가격 (원) *</label>
                        <input type="number" id="price" name="price" min="0" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">패키지 설명</label>
                        <textarea id="description" name="description"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="inclusions">포함 사항</label>
                        <textarea id="inclusions" name="inclusions"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="exclusions">불포함 사항</label>
                        <textarea id="exclusions" name="exclusions"></textarea>
                    </div>
                    
                    <div style="text-align: right;">
                        <a href="/packages" class="btn btn-secondary">취소</a>
                        <button type="submit" class="btn btn-primary">저장</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/packages/add")
async def add_package(
    name: str = Form(...),
    destination: str = Form(...),
    category: str = Form(...),
    duration_days: int = Form(...),
    price: int = Form(...),
    description: str = Form(""),
    inclusions: str = Form(""),
    exclusions: str = Form("")
):
    """패키지 추가 처리"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO packages (name, destination, category, duration_days, price, description, inclusions, exclusions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, destination, category, duration_days, price, description, inclusions, exclusions))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/packages", status_code=302)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/packages/delete/{package_id}")
async def delete_package(package_id: int):
    """패키지 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM packages WHERE id = ?", (package_id,))
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hotels", response_class=HTMLResponse)
async def hotels_list():
    """호텔 목록 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hotels ORDER BY created_at DESC")
    hotels = cursor.fetchall()
    conn.close()
    
    hotels_html = ""
    for hotel in hotels:
        hotels_html += f"""
        <tr>
            <td>{hotel['id']}</td>
            <td>{hotel['name']}</td>
            <td>{hotel['city']}</td>
            <td>{'★' * hotel['star_rating']}</td>
            <td>{hotel['price_per_night']:,}원/박</td>
            <td>{hotel['phone'] or '-'}</td>
            <td>
                <button onclick="editHotel({hotel['id']})" class="btn-edit">수정</button>
                <button onclick="deleteHotel({hotel['id']})" class="btn-delete">삭제</button>
            </td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>호텔 관리</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-edit {{ background: #28a745; color: white; margin-right: 5px; }}
            .btn-delete {{ background: #dc3545; color: white; }}
            .btn:hover {{ opacity: 0.8; }}
            table {{ width: 100%; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .back-btn {{ background: #6c757d; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>🏨 호텔 관리</h1>
                    <p>호텔 정보를 관리하세요</p>
                </div>
                <div>
                    <a href="/" class="btn back-btn">← 대시보드</a>
                    <a href="/hotels/add" class="btn btn-primary">+ 호텔 추가</a>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>호텔명</th>
                        <th>도시</th>
                        <th>등급</th>
                        <th>1박 요금</th>
                        <th>전화번호</th>
                        <th>관리</th>
                    </tr>
                </thead>
                <tbody>
                    {hotels_html}
                </tbody>
            </table>
        </div>
        
        <script>
            function editHotel(id) {{
                window.location.href = '/hotels/edit/' + id;
            }}
            
            function deleteHotel(id) {{
                if (confirm('이 호텔을 삭제하시겠습니까?')) {{
                    fetch('/hotels/delete/' + id, {{
                        method: 'POST'
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            location.reload();
                        }} else {{
                            alert('삭제 중 오류가 발생했습니다.');
                        }}
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.get("/hotels/add", response_class=HTMLResponse)
async def add_hotel_form():
    """호텔 추가 폼"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>호텔 추가</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
            textarea { height: 100px; resize: vertical; }
            .btn { padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
            .btn-primary { background: #007bff; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn:hover { opacity: 0.8; }
            .header { margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏨 새 호텔 추가</h1>
                <p>새로운 호텔 정보를 입력하세요</p>
            </div>
            
            <div class="form-container">
                <form action="/hotels/add" method="post">
                    <div class="form-group">
                        <label for="name">호텔명 *</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="city">도시 *</label>
                        <input type="text" id="city" name="city" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="star_rating">호텔 등급 *</label>
                        <select id="star_rating" name="star_rating" required>
                            <option value="">선택하세요</option>
                            <option value="1">1성급</option>
                            <option value="2">2성급</option>
                            <option value="3">3성급</option>
                            <option value="4">4성급</option>
                            <option value="5">5성급</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="price_per_night">1박 요금 (원) *</label>
                        <input type="number" id="price_per_night" name="price_per_night" min="0" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="amenities">편의시설</label>
                        <textarea id="amenities" name="amenities" placeholder="예: 수영장, 피트니스, 스파, WiFi, 주차장"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">호텔 설명</label>
                        <textarea id="description" name="description"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="address">주소</label>
                        <input type="text" id="address" name="address">
                    </div>
                    
                    <div class="form-group">
                        <label for="phone">전화번호</label>
                        <input type="text" id="phone" name="phone" placeholder="예: 02-1234-5678">
                    </div>
                    
                    <div style="text-align: right;">
                        <a href="/hotels" class="btn btn-secondary">취소</a>
                        <button type="submit" class="btn btn-primary">저장</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/hotels/add")
async def add_hotel(
    name: str = Form(...),
    city: str = Form(...),
    star_rating: int = Form(...),
    price_per_night: int = Form(...),
    amenities: str = Form(""),
    description: str = Form(""),
    address: str = Form(""),
    phone: str = Form("")
):
    """호텔 추가 처리"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO hotels (name, city, star_rating, price_per_night, amenities, description, address, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, city, star_rating, price_per_night, amenities, description, address, phone))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/hotels", status_code=302)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hotels/delete/{hotel_id}")
async def delete_hotel(hotel_id: int):
    """호텔 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotels WHERE id = ?", (hotel_id,))
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consultations", response_class=HTMLResponse)
async def consultations_list():
    """상담 내역 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.created_at, s.last_activity,
               COUNT(m.id) as message_count
        FROM consultation_sessions s
        LEFT JOIN consultation_messages m ON s.id = m.session_id
        GROUP BY s.id, s.created_at, s.last_activity
        ORDER BY s.last_activity DESC
    """)
    sessions = cursor.fetchall()
    conn.close()
    
    sessions_html = ""
    for session in sessions:
        sessions_html += f"""
        <tr>
            <td>{session['id'][:8]}...</td>
            <td>{session['created_at']}</td>
            <td>{session['last_activity']}</td>
            <td>{session['message_count']}</td>
            <td>
                <button onclick="viewSession('{session['id']}')" class="btn-view">상세보기</button>
            </td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>상담 내역</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .btn-view {{ background: #17a2b8; color: white; }}
            .btn:hover {{ opacity: 0.8; }}
            table {{ width: 100%; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .back-btn {{ background: #6c757d; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>💬 상담 내역</h1>
                    <p>고객 상담 기록을 확인하세요</p>
                </div>
                <div>
                    <a href="/" class="btn back-btn">← 대시보드</a>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>세션 ID</th>
                        <th>시작 시간</th>
                        <th>마지막 활동</th>
                        <th>메시지 수</th>
                        <th>관리</th>
                    </tr>
                </thead>
                <tbody>
                    {sessions_html}
                </tbody>
            </table>
        </div>
        
        <script>
            function viewSession(sessionId) {{
                window.location.href = '/consultations/' + sessionId;
            }}
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)