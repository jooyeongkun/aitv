"""
여행 상담 AI 모듈 (Supabase 연동 버전)
"""
import os
import google.generativeai as genai
from supabase_db import SupabaseDB

class TravelAIConsultantSupabase:
    def __init__(self, db: SupabaseDB):
        self.db = db
        # Gemini API 설정
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDiT1gqT-X8rvXJ1VgjOBP6P_vxri0xqv0")
        genai.configure(api_key=api_key)
        # 최신 Gemini 모델 사용
        try:
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("Gemini 1.5-flash model initialized successfully")
        except Exception as e:
            print(f"Gemini model initialization failed: {e}")
            self.gemini_model = None
        
    def generate_travel_recommendation(self, user_message: str, session_id: str) -> str:
        """여행 추천 생성 (Gemini AI + Supabase 데이터)"""
        try:
            print(f"Processing travel recommendation request: {user_message}")
        except UnicodeEncodeError:
            print("Processing travel recommendation request (contains Korean characters)")
        user_message_lower = user_message.lower()
        try:
            print(f"Lowercase message: {user_message_lower}")
        except UnicodeEncodeError:
            print("Lowercase message (contains Korean characters)")
        
        # Gemini API 시도
        try:
            if self.gemini_model is None:
                raise Exception("Gemini model not initialized")
                
            # DB 데이터를 활용한 프롬프트
            db_info = self.db.get_all_data_summary()
            try:
                print(f"Database info for AI: {db_info}")
            except UnicodeEncodeError:
                print("Database info retrieved (contains Korean characters)")
            
            prompt = f"""
            여행 전문 상담사로서 아래 상품을 활용해 간결하게 답변하세요:

            {db_info}

            질문: {user_message}

            답변 규칙:
            1. 인사말 없이 바로 추천
            2. 2-3문장으로 구체적인 상품 추천
            3. 가격, 포함사항, 기간 등 핵심 정보 포함
            4. 간결하되 충분한 정보 제공

            예시: "제주도 3박4일 힐링 패키지 45만원 추천합니다. 항공료, 숙박, 렌터카, 주요 관광지 입장료가 포함되어 있어요. 추가로 제주 오션뷰 호텔(28만원/박)도 있으니 예산에 맞게 선택하세요."
            """
            
            print("Calling Gemini API...")
            response = self.gemini_model.generate_content(prompt)
            ai_response = response.text
            
            try:
                print(f"Gemini response received: {ai_response[:50]}...")
            except UnicodeEncodeError:
                print("Gemini response received (contains Korean characters)")
            
            # 상담 메시지를 Supabase에 저장
            self.db.save_consultation_message(session_id, user_message, ai_response)
            
            return ai_response
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            # API 할당량 초과시 자체 응답 시스템 사용
            print("Using fallback response system due to API error")
            pass  # 아래 규칙 기반 응답으로 진행
            
        # 규칙 기반 응답 (백업) - 구체적인 키워드부터 확인
        print(f"Checking keywords in message: '{user_message}'")
        
        # 다낭/해외 여행 키워드 감지 (우선순위 높음)
        if "다낭" in user_message or "danang" in user_message_lower:
            print("Detected Danang keyword")
            packages = self.db.get_packages()
            overseas_packages = [pkg for pkg in packages if "다낭" in pkg.get('destination', '')]
            
            if overseas_packages:
                response = "🌴 다낭 여행 상품을 소개해드릴게요!\\n\\n"
                response += "추천 해외 패키지:\\n"
                for pkg in overseas_packages:
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원 ({pkg.get('duration', 'N/A')}일)\\n"
                    response += f"  목적지: {pkg.get('destination', 'N/A')}\\n"
                    response += f"  포함사항: {pkg.get('includes', 'N/A')}\\n\\n"
                response += "더 자세한 정보가 필요하시면 언제든 문의해주세요!"
            else:
                response = "현재 다낭 여행 상품을 준비 중입니다! 곧 더 많은 해외 패키지를 선보일 예정이에요. 🌟"
            
            # 상담 내용 저장
            self.db.save_consultation_message(session_id, user_message, response)
            return response
        
        # 해외 여행 일반 키워드 감지
        elif "해외" in user_message or "해외여행" in user_message or "international" in user_message_lower:
            packages = self.db.get_packages()
            overseas_packages = [pkg for pkg in packages if "다낭" in pkg.get('destination', '')]
            
            if overseas_packages:
                response = "🌴 해외 여행 상품을 소개해드릴게요!\\n\\n"
                response += "추천 해외 패키지:\\n"
                for pkg in overseas_packages:
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원 ({pkg.get('duration', 'N/A')}일)\\n"
                    response += f"  목적지: {pkg.get('destination', 'N/A')}\\n"
                    response += f"  포함사항: {pkg.get('includes', 'N/A')}\\n\\n"
                response += "더 자세한 정보가 필요하시면 언제든 문의해주세요!"
            else:
                response = "현재 다낭 여행 상품을 준비 중입니다! 곧 더 많은 해외 패키지를 선보일 예정이에요. 🌟"
            
            # 상담 내용 저장
            self.db.save_consultation_message(session_id, user_message, response)
            return response
        
        # 제주도 키워드 감지 (인코딩 문제 대응)
        elif "제주" in user_message or "jeju" in user_message_lower:
            print("Detected Jeju keyword")
            packages = self.db.get_packages(destination="제주")
            hotels = self.db.get_hotels(city="제주")
            
            response = "🌺 제주도 여행 추천드립니다!\\n\\n"
            
            if packages:
                response += "추천 패키지:\\n"
                for pkg in packages:
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원 ({pkg.get('duration', 'N/A')}일)\\n"
                    response += f"  포함사항: {pkg.get('includes', 'N/A')}\\n\\n"
            
            if hotels:
                response += "추천 호텔:\\n"
                for hotel in hotels:
                    response += f"• {hotel.get('name', 'N/A')}: {hotel.get('price_per_night', 0):,}원/박 ({hotel.get('star_rating', 'N/A')}성급)\\n"
                    response += f"  위치: {hotel.get('address', 'N/A')}\\n\\n"
                    
            response += "더 자세한 정보가 필요하시면 언제든 문의해주세요!"
            
            # 상담 내용 저장
            self.db.save_consultation_message(session_id, user_message, response)
            return response
        
        elif "db" in user_message_lower or "데이터베이스" in user_message_lower or "저장" in user_message_lower:
            packages = self.db.get_packages()
            hotels = self.db.get_hotels()
            
            response = f"현재 저장된 데이터:\\n"
            response += f"- 패키지: {len(packages)}개\\n"
            response += f"- 호텔: {len(hotels)}개\\n\\n"
            
            if packages:
                response += "주요 패키지:\\n"
                for pkg in packages[:3]:  # 상위 3개만
                    response += f"• {pkg.get('name', 'N/A')} - {pkg.get('price', 0):,}원\\n"
            
            if hotels:
                response += "\\n주요 호텔:\\n"
                for hotel in hotels[:3]:  # 상위 3개만
                    response += f"• {hotel.get('name', 'N/A')} - {hotel.get('price_per_night', 0):,}원/박\\n"
                    
            return response
        
        elif "부산" in user_message_lower or "busan" in user_message_lower:
            packages = self.db.get_packages(destination="부산")
            hotels = self.db.get_hotels(city="부산")
            
            response = "🌊 부산 여행 추천드립니다!\\n\\n"
            
            if packages:
                response += "추천 패키지:\\n"
                for pkg in packages:
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원\\n"
                    
            if hotels:
                response += "\\n추천 숙소:\\n"
                for hotel in hotels:
                    response += f"• {hotel.get('name', 'N/A')}: {hotel.get('price_per_night', 0):,}원/박\\n"
                    
            return response
        
        # 추가 키워드 감지
        elif "강릉" in user_message or "gangneung" in user_message_lower:
            packages = self.db.get_packages(destination="강릉")
            hotels = self.db.get_hotels(city="강릉")
            response = "🌊 강릉 여행 추천드립니다!\\n\\n"
            if packages:
                response += "추천 패키지:\\n"
                for pkg in packages:
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원 ({pkg.get('duration', 'N/A')}일)\\n"
            if hotels:
                response += "\\n추천 숙소:\\n"
                for hotel in hotels:
                    response += f"• {hotel.get('name', 'N/A')}: {hotel.get('price_per_night', 0):,}원/박\\n"
            response += "\\n더 자세한 정보가 필요하시면 언제든 문의해주세요!"
            self.db.save_consultation_message(session_id, user_message, response)
            return response
        
        elif "경주" in user_message or "gyeongju" in user_message_lower:
            packages = self.db.get_packages(destination="경주")
            hotels = self.db.get_hotels(city="경주")
            response = "🏛️ 경주 문화유산 여행 추천드립니다!\\n\\n"
            if packages:
                response += "추천 패키지:\\n"
                for pkg in packages:
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원 ({pkg.get('duration', 'N/A')}일)\\n"
            if hotels:
                response += "\\n추천 숙소:\\n"
                for hotel in hotels:
                    response += f"• {hotel.get('name', 'N/A')}: {hotel.get('price_per_night', 0):,}원/박\\n"
            response += "\\n더 자세한 정보가 필요하시면 언제든 문의해주세요!"
            self.db.save_consultation_message(session_id, user_message, response)
            return response
        
        elif "패키지" in user_message or "상품" in user_message or "추천" in user_message:
            # 일반적인 패키지 문의
            packages = self.db.get_packages()
            response = "✨ 현재 준비된 여행 패키지를 소개해드릴게요!\\n\\n"
            
            destinations = {}
            for pkg in packages:
                dest = pkg.get('destination', '기타')
                if dest not in destinations:
                    destinations[dest] = []
                destinations[dest].append(pkg)
            
            for dest, pkgs in destinations.items():
                response += f"📍 {dest}:\\n"
                for pkg in pkgs[:2]:  # 각 지역별 상위 2개
                    response += f"• {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,}원\\n"
                response += "\\n"
            
            response += "원하시는 지역이나 예산을 말씀해주시면 더 자세히 추천해드릴게요!"
            self.db.save_consultation_message(session_id, user_message, response)
            return response
        
        # 기본 응답
        response = """안녕하세요! 저희 여행사에 문의해 주셔서 감사합니다. 🌟
        
현재 제주도, 부산, 강릉, 경주 등 다양한 국내 여행 상품과 다낭 해외 패키지를 준비하고 있습니다.

어떤 여행을 원하시나요?
• 여행 목적지 (제주도, 부산, 강릉, 경주, 다낭)
• 여행 기간  
• 예산 범위
• 선호하는 여행 스타일

자세히 알려주시면 맞춤 추천해드리겠습니다!"""
        
        # 기본 응답도 저장
        self.db.save_consultation_message(session_id, user_message, response)
        return response