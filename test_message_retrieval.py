#!/usr/bin/env python3
"""
메시지 조회 디버그 테스트
"""
from supabase_db import SupabaseDB
from datetime import datetime
import uuid

def test_message_retrieval():
    print("=== 메시지 조회 디버그 테스트 ===")
    
    db = SupabaseDB()
    if not db.connect():
        print("❌ Supabase 연결 실패")
        return
    
    print("✅ Supabase 연결 성공")
    
    # 1. 세션 생성
    print("\n1. 세션 생성...")
    session_id = db.create_consultation_session()
    print(f"생성된 세션 ID: {session_id}")
    
    # 2. 메시지 저장 (명시적으로 세션 ID 전달)
    print("\n2. 메시지 저장...")
    try:
        print(f"저장할 세션 ID: {session_id}")
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
    
    # 3. 직접 메시지 조회 (get_session_messages)
    print("\n3. 직접 메시지 조회 (get_session_messages)...")
    try:
        raw_messages = db.get_session_messages(session_id)
        print(f"원본 메시지 개수: {len(raw_messages)}")
        if raw_messages:
            print("원본 메시지:")
            print(raw_messages[0])
        else:
            print("❌ 원본 메시지가 조회되지 않음")
    except Exception as e:
        print(f"❌ 원본 메시지 조회 실패: {e}")
    
    # 4. 포맷된 메시지 조회 (get_consultation_messages)
    print("\n4. 포맷된 메시지 조회 (get_consultation_messages)...")
    try:
        formatted_messages = db.get_consultation_messages(session_id)
        print(f"포맷된 메시지 개수: {len(formatted_messages)}")
        if formatted_messages:
            print("포맷된 메시지:")
            print(formatted_messages[0])
        else:
            print("❌ 포맷된 메시지가 조회되지 않음")
    except Exception as e:
        print(f"❌ 포맷된 메시지 조회 실패: {e}")
    
    # 5. 모든 메시지 조회 (디버그용)
    print("\n5. 모든 메시지 조회 (디버그용)...")
    try:
        all_messages = db.client.table('consultation_messages').select("*").execute()
        print(f"전체 메시지 개수: {len(all_messages.data)}")
        if all_messages.data:
            print("전체 메시지 중 하나:")
            print(all_messages.data[0])
    except Exception as e:
        print(f"❌ 전체 메시지 조회 실패: {e}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_message_retrieval()
