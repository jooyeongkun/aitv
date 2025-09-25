import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def simple_test():
    print("=== Simple Child Only Test ===")

    # 1. 패밀리팩 컨텍스트 설정
    result1 = travel_ai.process_message("패밀리팩 성인 3명 가격은?", conversation_id=800)
    print(f"Context set - Response length: {len(result1['response'])}")

    # 2. 아이3명만 질문
    result2 = travel_ai.process_message("아이3명이면?", conversation_id=800)
    response = result2.get('response', '')

    print(f"Child only response length: {len(response)}")
    print(f"Tours found: {result2.get('tours_found', 0)}")

    # 성인 관련 키워드 체크
    adult_keywords = ['성인', '18만원', '$1,092', '$1,587', '총합', '총 가격']
    found_adult = [kw for kw in adult_keywords if kw in response]

    if found_adult:
        print(f"FAILED: Found adult keywords: {found_adult}")
    else:
        print("SUCCESS: No adult keywords found")

    # 아이 관련 키워드 체크
    child_keywords = ['아동', '아이', '9만원', '$495']
    found_child = [kw for kw in child_keywords if kw in response]

    if found_child:
        print(f"SUCCESS: Found child keywords: {found_child}")
    else:
        print("FAILED: No child keywords found")

if __name__ == "__main__":
    simple_test()