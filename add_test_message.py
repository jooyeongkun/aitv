#!/usr/bin/env python3
"""
테스트용 메시지 추가 스크립트
"""
from supabase_db import SupabaseDB
from datetime import datetime

def add_test_message():
    print("=== 테스트 메시지 추가 ===")
    
    db = SupabaseDB()
    if not db.connect():
        print("Supabase 연결 실패")
        return
    
    # 기존 세션 중 하나 선택
    sessions = db.get_consultation_sessions()
    if not sessions:
        print("상담 세션이 없습니다.")
        return
    
    test_session_id = sessions[0]['session_id']
    print(f"테스트 세션 ID: {test_session_id}")
    
    # 테스트 메시지 추가
    try:
        db.save_consultation_message(
            session_id=test_session_id,
            user_message="안녕하세요! 테스트 메시지입니다.",
            ai_response="안녕하세요! AI 상담사입니다. 무엇을 도와드릴까요?",
            sender_type="ai"
        )
        print("✅ 테스트 메시지 추가 완료")
        
        # 메시지 확인
        messages = db.get_consultation_messages(test_session_id)
        print(f"메시지 개수: {len(messages)}")
        if messages:
            print("첫 번째 메시지:")
            print(messages[0])
        
    except Exception as e:
        print(f"❌ 메시지 추가 실패: {e}")

if __name__ == "__main__":
    add_test_message()
