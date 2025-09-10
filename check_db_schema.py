#!/usr/bin/env python3
"""
DB 스키마 확인 스크립트
"""
from supabase_db import SupabaseDB

def check_db_schema():
    print("=== DB 스키마 확인 ===")
    
    db = SupabaseDB()
    if not db.connect():
        print("❌ Supabase 연결 실패")
        return
    
    print("✅ Supabase 연결 성공")
    
    # 1. consultation_sessions 테이블 구조
    print("\n1. consultation_sessions 테이블 구조:")
    try:
        response = db.client.table('consultation_sessions').select("*").limit(1).execute()
        if response.data:
            print("✅ 테이블 존재")
            print(f"   컬럼: {list(response.data[0].keys())}")
        else:
            print("⚠️ 테이블 비어있음")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 2. consultation_messages 테이블 구조
    print("\n2. consultation_messages 테이블 구조:")
    try:
        response = db.client.table('consultation_messages').select("*").limit(1).execute()
        if response.data:
            print("✅ 테이블 존재")
            print(f"   컬럼: {list(response.data[0].keys())}")
        else:
            print("⚠️ 테이블 비어있음")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 3. packages 테이블 구조
    print("\n3. packages 테이블 구조:")
    try:
        response = db.client.table('packages').select("*").limit(1).execute()
        if response.data:
            print("✅ 테이블 존재")
            print(f"   컬럼: {list(response.data[0].keys())}")
        else:
            print("⚠️ 테이블 비어있음")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 4. hotels 테이블 구조
    print("\n4. hotels 테이블 구조:")
    try:
        response = db.client.table('hotels').select("*").limit(1).execute()
        if response.data:
            print("✅ 테이블 존재")
            print(f"   컬럼: {list(response.data[0].keys())}")
        else:
            print("⚠️ 테이블 비어있음")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n=== 스키마 확인 완료 ===")

if __name__ == "__main__":
    check_db_schema()
