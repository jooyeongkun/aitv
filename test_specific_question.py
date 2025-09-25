import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 encoding setting
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI service initialization
travel_ai = TravelAI()

def test_specific_questions():
    """Test that AI only answers what is specifically asked"""
    print("=== Testing Specific Question Answering ===\n")

    # Test 1: 패밀리팩 성인3명 먼저 물어보기 (컨텍스트 설정)
    print("1. Setting context - Family Pack adult 3:")
    result1 = travel_ai.process_message("패밀리팩 성인3명 가격", conversation_id=601)
    print(f"   Response length: {len(result1['response'])}")

    # Test 2: 아이3명만 물어보기 (성인 정보 추가 금지)
    print("\n2. Testing child-only question (should NOT include adult info):")
    result2 = travel_ai.process_message("아이3명이면?", conversation_id=601)
    try:
        response = result2['response']
        print(f"   Response: {response}")

        # 성인 관련 내용이 포함되어 있는지 확인
        adult_keywords = ['성인', '어른', '성인 3명', '18만원', '$1,092']
        contains_adult_info = any(keyword in response for keyword in adult_keywords)

        if contains_adult_info:
            print("   ❌ ERROR: Response contains adult information when only child was asked")
        else:
            print("   ✅ SUCCESS: Response only contains child information")

    except UnicodeEncodeError:
        print("   Response generated (encoding issue)")

    print(f"   Response length: {len(result2['response'])}")
    print(f"   Tours found: {result2['tours_found']}")

if __name__ == "__main__":
    test_specific_questions()