import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 인코딩 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI 서비스 초기화
travel_ai = TravelAI()

print("=== Testing Light Pack Follow-up Conversation ===")

# 첫 번째 질문 - 라이트팩 가격 문의
print("\n1. First question: Light Pack adult 2 price")
result1 = travel_ai.process_message("라이트팩 성인 2명 얼마죠", conversation_id=99)
try:
    print(f"Keywords found: {result1['keywords']}")
    print(f"Tours found: {result1['tours_found']}")
    print(f"Response length: {len(result1['response'])}")
    if 'validation' in result1:
        validation = result1['validation']
        print(f"Validation Score: {validation['overall_score']:.1f} ({validation['overall_status'].upper()})")
except UnicodeEncodeError:
    print("Response generated (encoding issue)")
    print(f"Tours found: {result1['tours_found']}")
    if 'validation' in result1:
        print(f"Validation Score: {result1['validation']['overall_score']:.1f}")

print("\n" + "="*50)

# 두 번째 질문 - 아이 2명 추가 문의 (follow-up)
print("\n2. Follow-up question: Add 2 children")
result2 = travel_ai.process_message("아이2명 추가하면요?", conversation_id=99)
try:
    print(f"Keywords found: {result2['keywords']}")
    print(f"Tours found: {result2['tours_found']}")
    print(f"Response length: {len(result2['response'])}")
    if 'validation' in result2:
        validation = result2['validation']
        print(f"Validation Score: {validation['overall_score']:.1f} ({validation['overall_status'].upper()})")
    if result2['tours_found'] > 0:
        print("SUCCESS: Context preserved - found tours for follow-up question")
    else:
        print("ISSUE: No tours found for follow-up question")
except UnicodeEncodeError:
    print("Response generated (encoding issue)")
    print(f"Tours found: {result2['tours_found']}")
    if 'validation' in result2:
        print(f"Validation Score: {result2['validation']['overall_score']:.1f}")