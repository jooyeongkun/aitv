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

    def save_consultation_message(self, session_id: str, user_message: str, ai_response: str = None, human_response: str = None, sender_type: str = "ai"):
        """상담 메시지 저장 (AI 또는 인간 상담사)"""
        try:
            data = {
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "human_response": human_response,
                "sender_type": sender_type,  # 'ai', 'human', 'user'
                "created_at": datetime.now().isoformat()
            }
            self.client.table('consultation_messages').insert(data).execute()
            print(f"Message saved to Supabase (sender: {sender_type})")
        except Exception as e:
            print(f"Error saving consultation message: {e}")

    def get_session_messages(self, session_id: str):
        """세션의 모든 메시지 조회"""
        try:
            response = self.client.table('consultation_messages')\
                .select("*")\
                .eq('session_id', session_id)\
                .order('created_at', desc=False)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting session messages: {e}")
            return []

    def set_session_human_mode(self, session_id: str, human_mode: bool = True):
        """세션을 인간 상담사 모드로 전환"""
        try:
            data = {
                "human_mode": human_mode,
                "human_joined_at": datetime.now().isoformat() if human_mode else None
            }
            self.client.table('consultation_sessions').update(data).eq('session_id', session_id).execute()
            return True
        except Exception as e:
            print(f"Error setting human mode: {e}")
            return False

    def get_active_sessions(self):
        """활성 상담 세션 목록 조회 (메시지가 있는 세션만)"""
        try:
            # 먼저 메시지가 있는 세션 ID들을 조회
            messages_response = self.client.table('consultation_messages')\
                .select("session_id")\
                .execute()
            
            if not messages_response.data:
                return []
            
            # 메시지가 있는 세션 ID들 추출
            session_ids = list(set([msg['session_id'] for msg in messages_response.data]))
            
            # 해당 세션들의 정보 조회 (active 상태만)
            sessions = []
            for session_id in session_ids:
                session_response = self.client.table('consultation_sessions')\
                    .select("*")\
                    .eq('session_id', session_id)\
                    .eq('status', 'active')\
                    .execute()
                if session_response.data:
                    sessions.extend(session_response.data)
            
            # 최신순으로 정렬
            sessions.sort(key=lambda x: x['created_at'], reverse=True)
            return sessions
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []

    def get_session_status(self, session_id: str):
        """세션 상태 조회"""
        try:
            response = self.client.table('consultation_sessions')\
                .select("*")\
                .eq('session_id', session_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting session status: {e}")
            return None

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

    def delete_package(self, package_id: int) -> bool:
        """패키지 삭제"""
        try:
            result = self.client.table('packages').delete().eq('id', package_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting package: {e}")
            return False

    def delete_hotel(self, hotel_id: int) -> bool:
        """호텔 삭제"""
        try:
            result = self.client.table('hotels').delete().eq('id', hotel_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting hotel: {e}")
            return False

    def update_package(self, package_id: int, data: Dict) -> bool:
        """패키지 수정"""
        try:
            result = self.client.table('packages').update(data).eq('id', package_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating package: {e}")
            return False

    def update_hotel(self, hotel_id: int, data: Dict) -> bool:
        """호텔 수정"""
        try:
            result = self.client.table('hotels').update(data).eq('id', hotel_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating hotel: {e}")
            return False

    def delete_consultation_session(self, session_id: str) -> bool:
        """상담 세션 및 관련 메시지 삭제"""
        try:
            # 먼저 해당 세션의 메시지들 삭제
            self.client.table('consultation_messages').delete().eq('session_id', session_id).execute()
            
            # 세션 삭제
            result = self.client.table('consultation_sessions').delete().eq('session_id', session_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting consultation session: {e}")
            return False

    def delete_all_consultation_data(self) -> bool:
        """모든 상담 데이터 삭제 (세션 + 메시지)"""
        try:
            # 모든 메시지 삭제
            self.client.table('consultation_messages').delete().neq('id', 0).execute()
            
            # 모든 세션 삭제
            self.client.table('consultation_sessions').delete().neq('id', 0).execute()
            return True
        except Exception as e:
            print(f"Error deleting all consultation data: {e}")
            return False

    def get_consultation_sessions(self) -> List[Dict]:
        """상담 세션 목록 조회 (관리자용)"""
        try:
            # 모든 상담 세션 조회
            response = self.client.table('consultation_sessions')\
                .select("*")\
                .order('created_at', desc=True)\
                .execute()
            
            sessions = response.data if response.data else []
            
            # 각 세션에 메시지 개수 추가
            for session in sessions:
                messages = self.get_session_messages(session['session_id'])
                session['message_count'] = len(messages)
            
            return sessions
        except Exception as e:
            print(f"Error getting consultation sessions: {e}")
            return []

    def get_consultation_messages(self, session_id: str) -> List[Dict]:
        """상담 메시지 조회 (관리자용)"""
        try:
            messages = self.get_session_messages(session_id)
            
            # 메시지를 관리자 페이지용 형식으로 변환
            formatted_messages = []
            for msg in messages:
                # 사용자 메시지
                if msg.get('user_message'):
                    formatted_messages.append({
                        'role': 'user',
                        'content': msg['user_message'],
                        'timestamp': msg['created_at']
                    })
                
                # AI 응답
                if msg.get('ai_response'):
                    formatted_messages.append({
                        'role': 'ai',
                        'content': msg['ai_response'],
                        'timestamp': msg['created_at']
                    })
                
                # 인간 상담사 응답
                if msg.get('human_response'):
                    formatted_messages.append({
                        'role': 'human',
                        'content': msg['human_response'],
                        'timestamp': msg['created_at']
                    })
            
            return formatted_messages
        except Exception as e:
            print(f"Error getting consultation messages: {e}")
            return []

    def clear_all_consultations(self) -> bool:
        """모든 상담 데이터 삭제 (관리자용)"""
        return self.delete_all_consultation_data()