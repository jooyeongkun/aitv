#!/usr/bin/env python3
"""
간단한 Supabase 연결 테스트
"""
import os
from supabase import create_client, Client

def test_supabase_connection():
    print("=== Supabase 연결 테스트 ===")
    
    # Supabase 설정
    url = os.getenv("SUPABASE_URL", "https://nqxlbxwkgaxrqubadblh.supabase.co")
    key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5xeGxieHdrZ2F4cnF1YmFkYmxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczNDMyNTYsImV4cCI6MjA3MjkxOTI1Nn0.TQDVUO0ap8-DED-JhBpCGRWQYvlWBWiI--thzJd3K5g")
    
    print(f"URL: {url}")
    print(f"Key: {key[:20]}...")
    
    try:
        # Supabase 클라이언트 생성
        client = create_client(url, key)
        print("✅ Supabase 클라이언트 생성 성공")
        
        # 간단한 테스트 쿼리
        response = client.table('packages').select("count", count='exact').execute()
        print(f"✅ 테스트 쿼리 성공: {response}")
        
        # 세션 생성 테스트
        from datetime import datetime
        import uuid
        
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "session_number": 999,
            "created_at": datetime.now().isoformat(),
            "status": "test"
        }
        
        print(f"세션 생성 테스트: {session_data}")
        result = client.table('consultation_sessions').insert(session_data).execute()
        print(f"✅ 세션 생성 성공: {result}")
        
        # 메시지 저장 테스트
        message_data = {
            "session_id": session_id,
            "user_message": "테스트 메시지",
            "ai_response": "테스트 응답",
            "sender_type": "ai",
            "created_at": datetime.now().isoformat()
        }
        
        print(f"메시지 저장 테스트: {message_data}")
        result = client.table('consultation_messages').insert(message_data).execute()
        print(f"✅ 메시지 저장 성공: {result}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    test_supabase_connection()
