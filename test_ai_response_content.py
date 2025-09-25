import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 인코딩 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI 서비스 초기화
travel_ai = TravelAI()

print("=== Testing AI Response Content ===")

# 첫 번째 질문 - 라이트팩 가격 문의
print("\n1. First question: Light Pack adult 3 price")
result1 = travel_ai.process_message("라이트팩 성인3명 가격 은 어떠헝돼", conversation_id=99)
try:
    print(f"AI Response: {result1['response']}")
    print(f"Tours found: {result1['tours_found']}")
    print(f"Validation Score: {result1['validation']['overall_score']:.1f}")
except UnicodeEncodeError:
    print("Response generated (encoding issue)")
    print(f"Tours found: {result1['tours_found']}")
    if 'validation' in result1:
        print(f"Validation Score: {result1['validation']['overall_score']:.1f}")

print("\n" + "="*50)

# 두 번째 질문 - 아이 가격 문의 (follow-up)
print("\n2. Follow-up question: Child price")
result2 = travel_ai.process_message("아이가격은?", conversation_id=99)
try:
    print(f"AI Response: {result2['response']}")
    print(f"Tours found: {result2['tours_found']}")

    # 응답에 "라이트" 또는 라이트팩과 관련된 내용이 있는지 확인
    response_text = result2['response'].lower()
    if '라이트' in response_text:
        print("✅ SUCCESS: Response contains '라이트'")
    else:
        print("❌ ERROR: Response does NOT contain '라이트'")

    if '래프팅' in response_text:
        print("❌ ERROR: Response incorrectly contains '래프팅'")
    else:
        print("✅ SUCCESS: Response does NOT contain '래프팅'")

    print(f"Validation Score: {result2['validation']['overall_score']:.1f}")
except UnicodeEncodeError:
    print("Response generated (encoding issue)")
    print(f"Tours found: {result2['tours_found']}")
    if 'validation' in result2:
        print(f"Validation Score: {result2['validation']['overall_score']:.1f}")