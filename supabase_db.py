"""
Supabase 데이터베이스 연동 모듈
"""
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "https://nqxlbxwkgaxrqubadblh.supabase.co")
        self.key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5xeGxieHdrZ2F4cnF1YmFkYmxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczNDMyNTYsImV4cCI6MjA3MjkxOTI1Nn0.TQDVUO0ap8-DED-JhBpCGRWQYvlWBWiI--thzJd3K5g")
        self.client: Client = create_client(self.url, self.key)
        self.connected = False

    def connect(self):
        """Supabase 연결 확인"""
        try:
            # 간단한 테스트 쿼리로 연결 확인
            response = self.client.table('packages').select("count", count='exact').execute()
            print("Supabase connected successfully")
            self.connected = True
            return True
        except Exception as e:
            print(f"Supabase connection failed: {e}")
            return False

    def create_consultation_session(self) -> str:
        """상담 세션 생성"""
        session_id = str(uuid.uuid4())
        try:
            data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            self.client.table('consultation_sessions').insert(data).execute()
            return session_id
        except Exception as e:
            print(f"Error creating consultation session: {e}")
            return session_id

    def save_consultation_message(self, session_id: str, user_message: str, ai_response: str):
        """상담 메시지 저장"""
        try:
            data = {
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "created_at": datetime.now().isoformat()
            }
            self.client.table('consultation_messages').insert(data).execute()
            print("Message saved to Supabase")
        except Exception as e:
            print(f"Error saving consultation message: {e}")

    def get_packages(self, destination: str = None, category: str = None, max_price: int = None) -> List[Dict]:
        """패키지 조회"""
        try:
            query = self.client.table('packages').select("*")
            
            if destination:
                query = query.ilike('destination', f'%{destination}%')
            if category:
                query = query.eq('category', category)
            if max_price:
                query = query.lte('price', max_price)
                
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error getting packages: {e}")
            return []

    def get_hotels(self, city: str = None, max_price: int = None, min_rating: int = None) -> List[Dict]:
        """호텔 조회"""
        try:
            query = self.client.table('hotels').select("*")
            
            if city:
                query = query.ilike('city', f'%{city}%')
            if max_price:
                query = query.lte('price_per_night', max_price)
            if min_rating:
                query = query.gte('star_rating', min_rating)
                
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error getting hotels: {e}")
            return []

    def get_all_data_summary(self) -> str:
        """모든 데이터 요약 반환 (AI 상담용)"""
        try:
            packages = self.get_packages()
            hotels = self.get_hotels()
            
            packages_info = "Available Travel Packages:\\n"
            for pkg in packages:
                packages_info += f"- {pkg.get('name', 'N/A')} to {pkg.get('destination', 'N/A')}: {pkg.get('price', 0):,}KRW for {pkg.get('duration', 'N/A')} days\\n"
            
            hotels_info = "\\nAvailable Hotels:\\n"
            for hotel in hotels:
                hotels_info += f"- {hotel.get('name', 'N/A')} in {hotel.get('city', 'N/A')}: {hotel.get('price_per_night', 0):,}KRW/night ({hotel.get('star_rating', 'N/A')} stars)\\n"
            
            return packages_info + hotels_info
        except Exception as e:
            print(f"Error getting data summary: {e}")
            return "Database information temporarily unavailable."

    def add_package(self, data: Dict) -> bool:
        """패키지 추가"""
        try:
            data['created_at'] = datetime.now().isoformat()
            self.client.table('packages').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error adding package: {e}")
            return False

    def add_hotel(self, data: Dict) -> bool:
        """호텔 추가"""
        try:
            data['created_at'] = datetime.now().isoformat()
            self.client.table('hotels').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error adding hotel: {e}")
            return False