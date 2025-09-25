import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI 서비스 초기화
travel_ai = TravelAI()

print("=== Testing Bestpack Response ===")

result = travel_ai.process_message("베스트팩 성인 얼마?", conversation_id=100)

print("Tours found:", result['tours_found'])
print("Response length:", len(result['response']))
try:
    # 응답 내용 확인 - 1인 기준이 들어있는지
    response = result['response']
    print("Response contains '1인 기준':", '1인' in response and '기준' in response)
    print("Response contains '1인':", '1인' in response)
    print("Response contains '기준':", '기준' in response)
except Exception as e:
    print("Error checking response:", e)

if 'validation' in result:
    print("Validation Score:", result['validation']['overall_score'])