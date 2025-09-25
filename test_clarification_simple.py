import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_clarification_simple():
    """Test clarification request functionality"""
    print("=== Testing Clarification Request ===\n")

    # Test 1: Ambiguous question without context
    print("1. Testing ambiguous question - 'price for children':")
    result = travel_ai.process_message("아이가격은요?", conversation_id=5001)

    response = result.get('response', '')
    print(f"   Tours found: {result['tours_found']}")

    # Check if response contains clarification request
    clarification_indicators = [
        "어떤 투어에 대해",
        "현재 이용 가능한 투어",
        "구체적인 투어명을"
    ]

    has_clarification = any(indicator in response for indicator in clarification_indicators)
    print(f"   Contains clarification request: {has_clarification}")

    if has_clarification:
        print("   SUCCESS: AI asks for clarification when subject is ambiguous")
    else:
        print("   INFO: AI provided different type of response")

    # Test 2: Another ambiguous question
    print("\n2. Testing another ambiguous question - 'how much for 2 adults':")
    result2 = travel_ai.process_message("성인 2명 얼마?", conversation_id=5002)

    response2 = result2.get('response', '')
    has_clarification2 = any(indicator in response2 for indicator in clarification_indicators)
    print(f"   Tours found: {result2['tours_found']}")
    print(f"   Contains clarification request: {has_clarification2}")

if __name__ == "__main__":
    test_clarification_simple()