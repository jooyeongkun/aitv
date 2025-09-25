import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_final_fix():
    """Test final fix for tour context preservation"""
    print("=== Testing Final Fix - Tour Context Preservation ===\n")

    # Test 1: 호이안 5명 얼마 (Hoi An 5 people)
    print("1. Testing 'Hoi An 5 people price':")
    result1 = travel_ai.process_message("호이안 5명 얼마", conversation_id=9001)
    response1 = result1.get('response', '')
    print(f"   Response: {response1[:100]}...")

    import re
    prices1 = re.findall(r'\$(\d+)', response1)
    print(f"   Prices found: ${', $'.join(prices1) if prices1 else 'none'}")
    print(f"   Tours found: {result1['tours_found']}")

    # Test 2: 아이 2명 추가하면? (Add 2 children)
    print("\n2. Follow-up - 'If we add 2 children':")
    result2 = travel_ai.process_message("아이 2명 추가하면?", conversation_id=9001)
    response2 = result2.get('response', '')
    print(f"   Response: {response2[:100]}...")

    prices2 = re.findall(r'\$(\d+)', response2)
    print(f"   Prices found: ${', $'.join(prices2) if prices2 else 'none'}")
    print(f"   Tours found: {result2['tours_found']}")

    # Check for tour consistency
    mentions_hoi_an = '호이안' in response2.lower()
    has_rafting_price = '340' in response2

    print(f"\n   Analysis:")
    print(f"   - Mentions Hoi An in 2nd response: {mentions_hoi_an}")
    print(f"   - Contains rafting price ($340): {has_rafting_price}")

    if not has_rafting_price and mentions_hoi_an:
        print("   ✅ SUCCESS: Context preserved, no rafting contamination!")
    elif has_rafting_price:
        print("   ❌ ERROR: Still showing rafting price despite context")
    else:
        print("   ⚠️ PARTIAL: No rafting contamination, but unclear context")

if __name__ == "__main__":
    test_final_fix()