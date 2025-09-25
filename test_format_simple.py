import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_format_direct():
    """Test formatting directly"""
    print("=== Testing Direct Format Function ===")

    # 샘플 응답 - 문제가 있던 형태 재현
    sample_response = "아이의 가격은 아동의 키에 따라 다릅니다. 1. **24개월 미만**: 무료 2. **키 100cm 이상 ~ 키 140cm 미만**: 예약금 3만원 + 잔금 $165 3. **키 140cm 이상**: 성인 요금 적용"

    print("BEFORE formatting:")
    print(sample_response)
    print(f"Lines: {len(sample_response.split('\\n'))}")

    # validate_and_fix_response 함수 호출
    formatted = travel_ai.validate_and_fix_response(sample_response, "")

    print("\nAFTER formatting:")
    print(formatted)
    print(f"Lines: {len(formatted.split('\\n'))}")

if __name__ == "__main__":
    test_format_direct()