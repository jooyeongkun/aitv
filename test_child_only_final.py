import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 encoding setting
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI service initialization
travel_ai = TravelAI()

def test_child_only_answer():
    """Final test for child-only question"""
    print("=== Final Test: Child Only Question ===\n")

    # 1. 패밀리팩 컨텍스트 설정
    print("1. Setting Family Pack context:")
    result1 = travel_ai.process_message("패밀리팩 성인 3명 가격은?", conversation_id=700)

    # 2. 아이3명만 질문 (핵심 테스트)
    print("\n2. Testing 'child 3 only' question:")
    result2 = travel_ai.process_message("아이3명이면?", conversation_id=700)

    # 결과 분석
    response = result2.get('response', '')
    print(f"   Response length: {len(response)}")
    print(f"   Tours found: {result2.get('tours_found', 0)}")

    # 성인 관련 키워드 체크
    adult_indicators = ['성인', '18만원', '$1,092', '$1,587', '총합', '총 가격']
    found_adult_content = [keyword for keyword in adult_indicators if keyword in response]

    if found_adult_content:
        print(f"   ❌ FAILED: Found adult content: {found_adult_content}")
    else:
        print("   ✅ SUCCESS: No adult content found!")

    # 아이 관련 키워드가 있는지 확인
    child_indicators = ['아동', '아이', '9만원', '$495']
    found_child_content = [keyword for keyword in child_indicators if keyword in response]

    if found_child_content:
        print(f"   ✅ SUCCESS: Found appropriate child content: {found_child_content}")
    else:
        print("   ❌ FAILED: No child content found!")

    try:
        print(f"\n   Full response: {response}")
    except UnicodeEncodeError:
        print("   Full response: [Korean text - encoding issue]")

if __name__ == "__main__":
    test_child_only_answer()