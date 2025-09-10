#!/usr/bin/env python3
"""
문제 진단 스크립트
"""
from supabase_db import SupabaseDB
from datetime import datetime
import uuid

def diagnose_issue():
    print("=== 문제 진단 시작 ===")
    
    db = SupabaseDB()
    
    # 1. Supabase 연결 테스트
    print("\n1. Supabase 연결 테스트...")
    if not db.connect():
        print("❌ FAILED: Supabase 연결 실패")
        print("   → Python-Render-Supabase 연동 문제")
        return
    print("✅ SUCCESS: Supabase 연결 성공")
    
    # 2. 테이블 구조 확인
    print("\n2. 테이블 구조 확인...")
    try:
        # consultation_sessions 테이블 구조 확인
        sessions_response = db.client.table('consultation_sessions').select("*").limit(1).execute()
        if sessions_response.data:
            print("✅ consultation_sessions 테이블 존재")
            print(f"   컬럼: {list(sessions_response.data[0].keys())}")
        else:
            print("⚠️ consultation_sessions 테이블 비어있음")
        
        # consultation_messages 테이블 구조 확인
        messages_response = db.client.table('consultation_messages').select("*").limit(1).execute()
        if messages_response.data:
            print("✅ consultation_messages 테이블 존재")
            print(f"   컬럼: {list(messages_response.data[0].keys())}")
        else:
            print("⚠️ consultation_messages 테이블 비어있음")
            
    except Exception as e:
        print(f"❌ FAILED: 테이블 구조 확인 실패 - {e}")
        return
    
    # 3. 최소한의 데이터로 저장 테스트
    print("\n3. 최소한의 데이터로 저장 테스트...")
    try:
        session_id = str(uuid.uuid4())
        
        # 세션 생성 (최소한의 필드만)
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "test"
        }
        db.client.table('consultation_sessions').insert(session_data).execute()
        print("✅ SUCCESS: 세션 생성 성공")
        
        # 메시지 저장 (최소한의 필드만)
        message_data = {
            "session_id": session_id,
            "user_message": "Test message",
            "ai_response": "Test response",
            "created_at": datetime.now().isoformat()
        }
        db.client.table('consultation_messages').insert(message_data).execute()
        print("✅ SUCCESS: 메시지 저장 성공")
        
        # 조회 테스트
        messages = db.get_session_messages(session_id)
        print(f"✅ SUCCESS: 메시지 조회 성공 - {len(messages)}개")
        
    except Exception as e:
        print(f"❌ FAILED: 저장/조회 테스트 실패 - {e}")
        print("   → 스키마 불일치 또는 권한 문제")
        return
    
    print("\n=== 진단 결과 ===")
    print("✅ 모든 테스트 통과")
    print("   → 문제는 코드의 스키마 불일치")
    print("   → Supabase-Python-Render 연동은 정상")

if __name__ == "__main__":
    diagnose_issue()
