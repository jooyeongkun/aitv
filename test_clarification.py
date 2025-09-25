import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_clarification_request():
    """Test that AI asks for clarification when context is ambiguous"""
    print("=== Testing Clarification Request ===\n")

    # Test 1: 새로운 대화에서 바로 모호한 질문
    print("1. Ambiguous question without context:")
    result1 = travel_ai.process_message("아이가격은요?", conversation_id=4001)
    print(f"   Tours found: {result1['tours_found']}")

    response = result1.get('response', '').lower()

    # Check if AI asks for clarification
    clarification_keywords = ['어떤 투어', 'which tour', '투어에 대해', '문의하시는']
    asks_clarification = any(keyword in response for keyword in clarification_keywords)

    # Check if it mentions multiple tour options
    tour_options = ['호이안', '베스트팩', '래프팅', '패밀리팩']
    mentions_options = sum(1 for option in tour_options if option in response)

    if asks_clarification and mentions_options >= 2:
        print("   ✅ SUCCESS: AI asks for clarification with options")
    elif asks_clarification:
        print("   ⚠️  PARTIAL: AI asks for clarification but lacks tour options")
    else:
        print("   ❌ ERROR: AI doesn't ask for clarification")

    print(f"   Asks clarification: {asks_clarification}")
    print(f"   Mentions tour options: {mentions_options}")

    print("\n2. Test response content analysis:")
    print(f"   Response contains clarification words: {asks_clarification}")

    # Test 2: 이전 컨텍스트 지우고 다시 테스트
    print("\n3. New conversation - clear context test:")
    result2 = travel_ai.process_message("2명 가격은?", conversation_id=4002)  # 새로운 conversation_id
    response2 = result2.get('response', '').lower()

    asks_clarification2 = any(keyword in response2 for keyword in clarification_keywords)
    print(f"   New conversation asks clarification: {asks_clarification2}")

if __name__ == "__main__":
    test_clarification_request()