"""
깨진 상담 메시지 데이터 정리
"""
from supabase_db import SupabaseDB

def fix_consultation_messages():
    """깨진 상담 메시지 데이터 정리"""
    print("=== 상담 메시지 데이터 정리 ===")
    
    db = SupabaseDB()
    
    if not db.connect():
        print("❌ Supabase 연결 실패!")
        return
    
    # 모든 상담 세션 조회
    sessions = db.get_consultation_sessions()
    print(f"총 상담 세션 개수: {len(sessions)}")
    
    fixed_count = 0
    
    for session in sessions:
        session_id = session.get('session_id') or session.get('id')
        print(f"\n세션 {session_id} 처리 중...")
        
        # 원본 메시지 조회
        raw_messages = db.get_session_messages(session_id)
        
        for msg in raw_messages:
            # 깨진 메시지 확인
            user_msg = msg.get('user_message', '')
            ai_msg = msg.get('ai_response', '')
            
            if '???' in user_msg or '???' in ai_msg:
                print(f"  깨진 메시지 발견: {msg['id']}")
                print(f"  사용자 메시지: {user_msg}")
                print(f"  AI 응답: {ai_msg[:50]}...")
                
                # 깨진 메시지는 삭제하거나 수정
                try:
                    # 메시지 삭제
                    db.client.table('consultation_messages').delete().eq('id', msg['id']).execute()
                    print(f"  메시지 {msg['id']} 삭제됨")
                    fixed_count += 1
                except Exception as e:
                    print(f"  삭제 실패: {e}")
    
    print(f"\n=== 정리 완료 ===")
    print(f"총 {fixed_count}개의 깨진 메시지가 정리되었습니다.")

if __name__ == "__main__":
    fix_consultation_messages()
