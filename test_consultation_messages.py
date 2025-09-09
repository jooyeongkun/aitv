"""
상담 메시지 조회 테스트
"""
from supabase_db import SupabaseDB

def test_consultation_messages():
    """상담 메시지 조회 테스트"""
    print("=== 상담 메시지 조회 테스트 ===")
    
    db = SupabaseDB()
    
    # 1. 연결 테스트
    if not db.connect():
        print("❌ Supabase 연결 실패!")
        return
    
    # 2. 상담 세션 목록 조회
    print("\n1. 상담 세션 목록 조회...")
    sessions = db.get_consultation_sessions()
    print(f"상담 세션 개수: {len(sessions)}")
    
    if not sessions:
        print("❌ 상담 세션이 없습니다!")
        return
    
    # 3. 첫 번째 세션의 메시지 조회
    first_session = sessions[0]
    session_id = first_session.get('session_id') or first_session.get('id')
    print(f"\n2. 세션 {session_id}의 메시지 조회...")
    
    # 4. 원본 메시지 조회
    print("\n3. 원본 메시지 조회...")
    raw_messages = db.get_session_messages(session_id)
    print(f"원본 메시지 개수: {len(raw_messages)}")
    
    if raw_messages:
        print("첫 번째 원본 메시지:")
        print(raw_messages[0])
    
    # 5. 포맷된 메시지 조회
    print("\n4. 포맷된 메시지 조회...")
    formatted_messages = db.get_consultation_messages(session_id)
    print(f"포맷된 메시지 개수: {len(formatted_messages)}")
    
    if formatted_messages:
        print("첫 번째 포맷된 메시지:")
        print(formatted_messages[0])
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_consultation_messages()
