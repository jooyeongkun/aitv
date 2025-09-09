#!/usr/bin/env python3
"""
Supabase 연결 테스트 스크립트
"""
from supabase_db import SupabaseDB

def test_connection_and_data():
    print("=== Supabase 연결 테스트 ===")
    
    db = SupabaseDB()
    
    # 1. 연결 테스트
    print("\n1. Supabase 연결 테스트...")
    if db.connect():
        print("✅ Supabase 연결 성공")
    else:
        print("❌ Supabase 연결 실패")
        return
    
    # 2. 패키지 데이터 테스트
    print("\n2. 패키지 데이터 테스트...")
    try:
        packages = db.get_packages()
        print(f"✅ 패키지 개수: {len(packages)}")
        if packages:
            print(f"   첫 번째 패키지: {packages[0]}")
    except Exception as e:
        print(f"❌ 패키지 조회 실패: {e}")
    
    # 3. 호텔 데이터 테스트
    print("\n3. 호텔 데이터 테스트...")
    try:
        hotels = db.get_hotels()
        print(f"✅ 호텔 개수: {len(hotels)}")
        if hotels:
            print(f"   첫 번째 호텔: {hotels[0]}")
    except Exception as e:
        print(f"❌ 호텔 조회 실패: {e}")
    
    # 4. 상담 세션 테스트
    print("\n4. 상담 세션 테스트...")
    try:
        sessions = db.get_consultation_sessions()
        print(f"✅ 상담 세션 개수: {len(sessions)}")
        if sessions:
            print(f"   첫 번째 세션: {sessions[0]}")
            
            # 5. 특정 세션의 메시지 테스트
            print("\n5. 상담 메시지 테스트...")
            test_session_id = sessions[0]['session_id']
            messages = db.get_consultation_messages(test_session_id)
            print(f"✅ 세션 {test_session_id}의 메시지 개수: {len(messages)}")
            if messages:
                print(f"   첫 번째 메시지: {messages[0]}")
            else:
                print("   메시지가 없습니다.")
        else:
            print("   상담 세션이 없습니다.")
    except Exception as e:
        print(f"❌ 상담 세션 조회 실패: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_connection_and_data()