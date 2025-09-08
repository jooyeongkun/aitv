"""
여행 상담 AI 모듈 (Gemini API 연동 + SQLite DB)
"""
import uuid
import os
import sqlite3
from datetime import datetime
import google.generativeai as genai

class TravelConsultantDB:
    def __init__(self, db_config=None):
        self.db_config = db_config
        self.connected = False
        self.db_path = 'travel_consultation.db'
    
    def get_db_connection(self):
        """SQLite 데이터베이스 연결"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def connect(self):
        """DB 연결 확인"""
        try:
            conn = self.get_db_connection()
            conn.close()
            print("SQLite database connected successfully.")
            self.connected = True
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def create_consultation_session(self):
        """상담 세션 생성"""
        session_id = str(uuid.uuid4())
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consultation_sessions (id, created_at, last_activity) VALUES (?, ?, ?)",
            (session_id, datetime.now(), datetime.now())
        )
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_packages(self, destination=None, category=None, max_price=None):
        """패키지 상품 조회 (SQLite에서)"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM packages WHERE 1=1"
        params = []
        
        if destination:
            query += " AND destination LIKE ?"
            params.append(f"%{destination}%")
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
        if max_price:
            query += " AND price <= ?"
            params.append(max_price)
            
        cursor.execute(query, params)
        packages = cursor.fetchall()
        conn.close()
        
        # Row 객체를 dict로 변환
        return [dict(package) for package in packages]
    
    def get_hotels(self, city=None, star_rating=None, max_price=None):
        """호텔 정보 조회 (SQLite에서)"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM hotels WHERE 1=1"
        params = []
        
        if city:
            query += " AND city LIKE ?"
            params.append(f"%{city}%")
        if star_rating:
            query += " AND star_rating = ?"
            params.append(star_rating)
        if max_price:
            query += " AND price_per_night <= ?"
            params.append(max_price)
            
        cursor.execute(query, params)
        hotels = cursor.fetchall()
        conn.close()
        
        # Row 객체를 dict로 변환하고 price 필드명 통일
        result = []
        for hotel in hotels:
            hotel_dict = dict(hotel)
            hotel_dict['price'] = hotel_dict['price_per_night']  # 기존 코드 호환성
            result.append(hotel_dict)
        return result

class TravelAIConsultant:
    def __init__(self, db):
        self.db = db
        # Gemini API 설정
        genai.configure(api_key="AIzaSyDiT1gqT-X8rvXJ1VgjOBP6P_vxri0xqv0")
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.system_prompt = """당신은 전문적인 여행 상담사입니다. 
사용자의 여행 요청에 대해 구체적이고 도움이 되는 여행 계획을 제안해주세요.

다음 정보를 포함하여 답변해주세요:
- 추천 여행지와 코스
- 예상 비용
- 추천 숙소
- 교통편 정보  
- 현지 맛집이나 특별한 경험

친근하고 전문적인 톤으로 답변하며, 이모지를 적절히 사용해서 답변을 생동감 있게 만들어주세요."""
    
    def _get_db_context(self):
        """회사 DB 정보를 AI에게 제공할 컨텍스트 생성 (실제 DB에서 조회)"""
        packages = self.db.get_packages()
        hotels = self.db.get_hotels()
        
        packages_info = "📦 **패키지 상품:**\n"
        for p in packages:
            packages_info += f"- {p['name']}: {p['destination']}, {p['price']:,}원, {p['category']}\n"
        
        hotels_info = "\n🏨 **호텔 정보:**\n"
        for h in hotels:
            hotels_info += f"- {h['name']}: {h['city']}, {h['star_rating']}성급, {h['price_per_night']:,}원/박\n"
        
        return packages_info + hotels_info

    def generate_travel_recommendation(self, user_message, session_id):
        """여행 추천 생성 (Gemini AI + 규칙 기반 백업)"""
        print("Processing travel recommendation request")
        user_message_lower = user_message.lower()
        
        # 먼저 Gemini API 시도
        try:
            # 회사 DB 정보를 AI에게 제공
            db_context = self._get_db_context()
            prompt = f"""당신은 우리 여행사의 전문 상담사입니다. 
아래는 우리 회사에서 제공하는 패키지와 호텔 정보입니다:

{db_context}

중요: 반드시 위의 패키지와 호텔 정보만을 기반으로 상담해주세요. 
다른 외부 여행사나 호텔을 추천하지 마세요.

사용자 질문: {user_message}"""
            
            response = self.gemini_model.generate_content(prompt)
            
            ai_response = response.text
            print("Gemini AI Response received")
            return ai_response
            
        except Exception as e:
            print("Gemini API Error occurred")
            # Gemini 실패시 규칙 기반으로 대체
            
        # 규칙 기반 응답
        if "db" in user_message_lower or "데이터베이스" in user_message_lower or "저장" in user_message_lower:
            packages = self.db.get_packages()
            hotels = self.db.get_hotels()
            packages_info = "\n".join([f"- {p['name']} ({p['destination']}, {p['price']:,}원)" for p in packages])
            hotels_info = "\n".join([f"- {h['name']} ({h['city']}, {h['star_rating']}성급, {h['price_per_night']:,}원)" for h in hotels])
            
            return f"""📊 **현재 데이터베이스에 저장된 정보**:

🎁 **패키지 상품** ({len(packages)}개):
{packages_info}

🏨 **호텔 정보** ({len(hotels)}개):
{hotels_info}

💡 이 정보들을 바탕으로 여행 추천을 해드리고 있어요!
구체적인 여행 계획이 필요하시면 말씀해주세요. 😊"""
        
        elif "호텔" in user_message_lower or "숙소" in user_message_lower:
            if "4성급" in user_message_lower or "4성" in user_message_lower:
                hotels_4star = self.db.get_hotels(star_rating=4)
                hotel_list = "\n".join([f"- {h['name']} ({h['city']}, {h['price_per_night']:,}원/박)" for h in hotels_4star])
                return f"""🏨 **4성급 호텔 추천**:

{hotel_list}

💡 **4성급 호텔 특징**:
- 우수한 시설과 서비스
- 합리적인 가격대
- 편안한 휴식 공간

더 자세한 정보나 예약이 필요하시면 말씀해주세요! 😊"""
            
            elif "5성급" in user_message_lower or "5성" in user_message_lower:
                hotels_5star = self.db.get_hotels(star_rating=5)
                hotel_list = "\n".join([f"- {h['name']} ({h['city']}, {h['price_per_night']:,}원/박)" for h in hotels_5star])
                return f"""🌟 **5성급 호텔 추천**:

{hotel_list}

💎 **5성급 호텔 특징**:
- 최고급 시설과 서비스
- 프리미엄 어메니티
- 럭셔리 휴식 공간

특별한 날을 위한 완벽한 선택입니다! ✨"""
            
            else:
                all_hotels = self.db.get_hotels()
                hotel_list = "\n".join([f"- {h['name']} ({h['city']}, {h['star_rating']}성급, {h['price_per_night']:,}원/박)" for h in all_hotels])
                return f"""🏨 **전체 호텔 추천**:

{hotel_list}

⭐ 성급별로 문의하시면 더 자세한 정보를 드릴 수 있어요!
예: "4성급 호텔 추천", "5성급 호텔 정보" 등"""
        
        elif "제주" in user_message_lower or "제주도" in user_message_lower:
            return """🏝️ 제주도 여행 추천드립니다!

📍 **추천 코스**:
- 1일차: 성산일출봉 → 우도 → 섭지코지
- 2일차: 한라산 둘레길 → 천지연폭포
- 3일차: 협재해수욕장 → 카페거리 → 올레길

🏨 **추천 숙소**: 제주 그랜드 호텔 (오션뷰)
💰 **예상 비용**: 50만원 (3박4일 기준)
🚗 **교통**: 렌터카 또는 버스 투어
🍽️ **맛집**: 흑돼지구이, 해산물 전문점

어떤 스타일의 여행을 원하시나요? (힐링/관광/자연/맛집) 😊"""
        
        elif "부산" in user_message_lower:
            return """🌊 부산 여행 추천드립니다!

📍 **추천 코스**:
- 1일차: 해운대 → 동백섬 → 누리마루 APEC 하우스
- 2일차: 감천문화마을 → 자갈치시장 → 부산타워

🏨 **추천 숙소**: 부산 비즈니스 호텔
💰 **예상 비용**: 30만원 (2박3일 기준)
🚇 **교통**: 지하철, 버스 (부산 시티투어)
🍽️ **맛집**: 돼지국밥, 회센터, 씨앗호떡

부산의 야경과 해산물이 최고예요! 🍲✨"""
        
        elif "강릉" in user_message_lower:
            return """🏔️ 강릉 자연 여행 추천드립니다!

📍 **추천 코스**:
- 1일차: 정동진 해돋이 → 경포대 해수욕장
- 2일차: 오죽헌 → 안목해변 카페거리

🏨 **추천 숙소**: 강릉 오션뷰 호텔
💰 **예상 비용**: 40만원 (2박3일 기준)
🚗 **교통**: KTX + 렌터카 또는 버스
☕ **특별 경험**: 안목항 커피거리, 테라로사 본점

강릉 커피거리는 꼭 들러보세요! ☕️🌊"""
        
        elif any(keyword in user_message_lower for keyword in ["추천", "여행", "계획", "도움"]):
            return """안녕하세요! 여행 계획을 도와드릴게요 🌟

**인기 여행지**:
- 🏝️ **제주도** (힐링, 자연, 드라이브)
- 🌊 **부산** (도시, 해변, 야경)  
- 🏔️ **강릉** (자연, 카페, 기차여행)
- 🏯 **경주** (역사, 문화, 한옥스테이)
- 🌸 **전주** (한옥마을, 맛집투어)

구체적인 지역이나 선호하는 여행 스타일을 말씀해주시면 
더 맞춤형 추천을 드릴 수 있어요!

예: "제주도 3박4일 힐링여행", "부산 맛집투어" 등"""
        
        else:
            return """더 구체적인 여행 정보를 알려주시면 
맞춤형 추천을 드릴 수 있어요! 

**이렇게 물어보세요**:
- "제주도 3박4일 힐링여행 추천해주세요"
- "부산 2박3일 맛집 위주 여행"
- "강릉 1박2일 커피투어"
- "경주 역사 문화 여행"

어떤 여행을 계획하고 계신가요? 😊"""