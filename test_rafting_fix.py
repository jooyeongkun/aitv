import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_no_rafting_default():
    """Test that AI no longer defaults to rafting calculations"""
    print("=== Testing No Rafting Default ===\n")

    # Test 1: 호이안 5명 얼마 (should get Hoi An price, not rafting)
    print("1. Testing 'Hoi An 5 people price':")
    result1 = travel_ai.process_message("호이안 5명 얼마", conversation_id=8001)
    print(f"   Tours found: {result1['tours_found']}")

    response1 = result1.get('response', '')

    # Check for $485 (correct Hoi An 5 people price) vs $340 (wrong rafting price)
    import re
    prices = re.findall(r'\$(\d+)', response1)
    print(f"   Prices found: ${', $'.join(prices) if prices else 'none'}")

    has_rafting_price = '340' in response1
    has_hoi_an_price = '485' in response1 or '420' in response1  # Either 4 or 5 people price

    if has_rafting_price:
        print("   ERROR: Still showing rafting price ($340)")
    elif has_hoi_an_price:
        print("   SUCCESS: Shows correct Hoi An pricing")
    else:
        print("   INFO: Shows different pricing structure")

    # Test 2: 아이 2명 추가하면? (should maintain Hoi An context)
    print("\n2. Follow-up question - 'If we add 2 children':")
    result2 = travel_ai.process_message("아이 2명 추가하면?", conversation_id=8001)
    print(f"   Tours found: {result2['tours_found']}")

    response2 = result2.get('response', '')
    prices2 = re.findall(r'\$(\d+)', response2)
    print(f"   Prices found: ${', $'.join(prices2) if prices2 else 'none'}")

    has_rafting_price_2 = '340' in response2
    mentions_hoi_an = '호이안' in response2.lower()

    if has_rafting_price_2:
        print("   ERROR: Switched to rafting price ($340)")
    elif mentions_hoi_an:
        print("   SUCCESS: Maintains Hoi An context")
    else:
        print("   INFO: Provides pricing without explicit tour mention")

if __name__ == "__main__":
    test_no_rafting_default()