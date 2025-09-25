import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_line_breaks():
    print("=== Testing Auto Line Breaks ===")

    # 아이 가격 구조 문의 (1. 2. 3. 형태로 응답 예상)
    result = travel_ai.process_message("아이 가격 구조 설명해줘", conversation_id=900)

    response = result.get('response', '')
    print(f"Response length: {len(response)}")
    print(f"Tours found: {result.get('tours_found', 0)}")

    print("\n=== Response (formatted) ===")
    try:
        print(response)
    except UnicodeEncodeError:
        print("[Korean response with auto line breaks - encoding issue]")

    # 줄바꿈이 제대로 되었는지 확인
    lines = response.split('\n')
    print(f"\nTotal lines: {len(lines)}")

    # 패턴 확인
    numbered_lines = [line for line in lines if any(char.isdigit() for char in line[:5])]
    print(f"Lines with numbers: {len(numbered_lines)}")

if __name__ == "__main__":
    test_line_breaks()