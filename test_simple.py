#!/usr/bin/env python3
"""
Simple DB test without Korean characters
"""
from supabase_db import SupabaseDB

def test_simple():
    print("=== Simple DB Test ===")
    
    db = SupabaseDB()
    if not db.connect():
        print("FAILED: Supabase connection")
        return
    
    print("SUCCESS: Supabase connected")
    
    # 1. Create session
    print("\n1. Creating session...")
    session_id = db.create_consultation_session()
    print(f"Created session ID: {session_id}")
    
    # 2. Save message
    print("\n2. Saving message...")
    try:
        db.save_consultation_message(
            session_id=session_id,
            user_message="Test user message",
            ai_response="Test AI response",
            sender_type="ai"
        )
        print("SUCCESS: Message saved")
    except Exception as e:
        print(f"FAILED: Message save - {e}")
        return
    
    # 3. Retrieve messages
    print("\n3. Retrieving messages...")
    try:
        messages = db.get_session_messages(session_id)
        print(f"Found {len(messages)} messages")
        if messages:
            print("SUCCESS: Message retrieved")
            print(f"First message: {messages[0]}")
        else:
            print("FAILED: No messages found")
    except Exception as e:
        print(f"FAILED: Message retrieval - {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_simple()
