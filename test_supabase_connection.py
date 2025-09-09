"""
Supabase 연결 및 데이터 조회 테스트
"""
from supabase_db import SupabaseDB

def test_supabase():
    """Supabase 연결 및 데이터 조회 테스트"""
    print("=== Supabase 연결 테스트 ===")
    
    db = SupabaseDB()
    
    # 1. 연결 테스트
    print("1. 연결 테스트...")
    if db.connect():
        print("✅ Supabase 연결 성공!")
    else:
        print("❌ Supabase 연결 실패!")
        return
    
    # 2. 패키지 데이터 조회
    print("\n2. 패키지 데이터 조회...")
    try:
        packages = db.get_packages()
        print(f"패키지 개수: {len(packages)}")
        if packages:
            print("첫 번째 패키지:")
            print(f"  - 이름: {packages[0].get('name', 'N/A')}")
            print(f"  - 목적지: {packages[0].get('destination', 'N/A')}")
            print(f"  - 가격: {packages[0].get('price', 'N/A')}")
        else:
            print("❌ 패키지 데이터가 없습니다!")
    except Exception as e:
        print(f"❌ 패키지 조회 오류: {e}")
    
    # 3. 호텔 데이터 조회
    print("\n3. 호텔 데이터 조회...")
    try:
        hotels = db.get_hotels()
        print(f"호텔 개수: {len(hotels)}")
        if hotels:
            print("첫 번째 호텔:")
            print(f"  - 이름: {hotels[0].get('name', 'N/A')}")
            print(f"  - 도시: {hotels[0].get('city', 'N/A')}")
            print(f"  - 가격: {hotels[0].get('price_per_night', 'N/A')}")
        else:
            print("❌ 호텔 데이터가 없습니다!")
    except Exception as e:
        print(f"❌ 호텔 조회 오류: {e}")
    
    # 4. 상담 세션 조회
    print("\n4. 상담 세션 조회...")
    try:
        sessions = db.get_consultation_sessions()
        print(f"상담 세션 개수: {len(sessions)}")
        if sessions:
            print("첫 번째 세션:")
            print(f"  - ID: {sessions[0].get('session_id', 'N/A')}")
            print(f"  - 생성일: {sessions[0].get('created_at', 'N/A')}")
            print(f"  - 메시지 수: {sessions[0].get('message_count', 'N/A')}")
        else:
            print("❌ 상담 세션이 없습니다!")
    except Exception as e:
        print(f"❌ 상담 세션 조회 오류: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_supabase()
