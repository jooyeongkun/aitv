#!/usr/bin/env python3
"""
DB 저장 테스트
"""
from supabase_db import SupabaseDB
from datetime import datetime
import uuid

def test_db_save():
    print("=== DB 저장 테스트 ===")
    
    db = SupabaseDB()
    if not db.connect():
        print("❌ Supabase 연결 실패")
        return
    
    print("✅ Supabase 연결 성공")
    
    # 1. 세션 생성 테스트
    print("\n1. 세션 생성 테스트...")
    session_id = db.create_consultation_session()
    print(f"세션 ID: {session_id}")
    
    # 2. 메시지 저장 테스트
    print("\n2. 메시지 저장 테스트...")
    try:
        db.save_consultation_message(
            session_id=session_id,
            user_message="테스트 사용자 메시지",
            ai_response="테스트 AI 응답",
            sender_type="ai"
        )
        print("✅ 메시지 저장 성공")
    except Exception as e:
        print(f"❌ 메시지 저장 실패: {e}")
        return
    
    # 3. 메시지 조회 테스트
    print("\n3. 메시지 조회 테스트...")
    try:
        messages = db.get_consultation_messages(session_id)
        print(f"조회된 메시지 개수: {len(messages)}")
        if messages:
            print("첫 번째 메시지:")
            print(messages[0])
        else:
            print("❌ 메시지가 조회되지 않음")
    except Exception as e:
        print(f"❌ 메시지 조회 실패: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_db_save()
