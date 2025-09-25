import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_format_english():
    """Test formatting with English"""
    print("=== Testing Format Function ===")

    # 샘플 응답 - 문제가 있던 형태 재현 (영문)
    sample_response = "Child pricing depends on height. 1. **Under 24 months**: Free 2. **100cm to 140cm**: Deposit 30,000 KRW + Balance $165 3. **Over 140cm**: Adult rate applies"

    print("BEFORE formatting:")
    print(sample_response)
    print(f"Lines: {len(sample_response.split('\n'))}")

    # validate_and_fix_response 함수 호출
    formatted = travel_ai.validate_and_fix_response(sample_response, "")

    print("\nAFTER formatting:")
    print(formatted)
    print(f"Lines: {len(formatted.split('\n'))}")

if __name__ == "__main__":
    test_format_english()