import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_bestpack_children():
    """Test bestpack with children addition"""
    print("=== Testing Bestpack + Children Addition ===\n")

    # Test 1: 베스트팩 3명 얼마 (Bestpack 3 people)
    print("1. Testing 'Bestpack 3 people price':")
    result1 = travel_ai.process_message("베스트팩 3명 얼마", conversation_id=5001)
    response1 = result1.get('response', '')
    print(f"   Response: {response1[:100]}...")

    import re
    prices1 = re.findall(r'\$([\d,]+)', response1)
    print(f"   Prices found: ${', $'.join(prices1) if prices1 else 'none'}")
    print(f"   Tours found: {result1['tours_found']}")

    # Test 2: 아이 2명 추가하면? (Add 2 children)
    print("\n2. Follow-up - 'If we add 2 children':")
    result2 = travel_ai.process_message("아이 2명 추가하면?", conversation_id=5001)
    response2 = result2.get('response', '')
    print(f"   Response: {response2[:100]}...")

    prices2 = re.findall(r'\$([\d,]+)', response2)
    print(f"   Prices found: ${', $'.join(prices2) if prices2 else 'none'}")
    print(f"   Tours found: {result2['tours_found']}")

    # Check for errors
    has_error = response2 == "-1" or "오류" in response2 or len(response2) < 10
    print(f"   Has error: {has_error}")

    if has_error:
        print("   ❌ ERROR: Response indicates failure")
    else:
        print("   ✅ SUCCESS: Valid response received")

if __name__ == "__main__":
    test_bestpack_children()