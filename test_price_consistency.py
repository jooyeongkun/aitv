import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_price_consistency():
    """Test that prices remain consistent when adding children"""
    print("=== Testing Price Consistency ===\n")

    # Test 1: 호이안 성인 4명 가격
    print("1. Initial question - Hoi An 4 adults:")
    result1 = travel_ai.process_message("호이안 성인 4명 얼마죠", conversation_id=7001)
    print(f"   Tours found: {result1['tours_found']}")

    response1 = result1.get('response', '')

    # Extract price from first response
    import re
    adult_prices = re.findall(r'\$(\d+)', response1)
    if adult_prices:
        initial_adult_price = adult_prices[0]
        print(f"   Initial adult price: ${initial_adult_price}")
    else:
        initial_adult_price = "not found"
        print("   Could not extract adult price from response")

    # Test 2: 아이 2명 추가 질문
    print("\n2. Follow-up question - adding 2 children:")
    result2 = travel_ai.process_message("아이 2명 더 있어요.", conversation_id=7001)
    print(f"   Tours found: {result2['tours_found']}")

    response2 = result2.get('response', '')

    # Extract prices from second response
    adult_prices_2 = re.findall(r'\$(\d+)', response2)
    if adult_prices_2:
        final_adult_price = adult_prices_2[0]  # Should be same as initial
        print(f"   Final adult price: ${final_adult_price}")
    else:
        final_adult_price = "not found"
        print("   Could not extract adult price from second response")

    # Check consistency
    if initial_adult_price != "not found" and final_adult_price != "not found":
        if initial_adult_price == final_adult_price:
            print("   ✅ SUCCESS: Adult price remains consistent")
        else:
            print(f"   ❌ ERROR: Adult price changed from ${initial_adult_price} to ${final_adult_price}")
            print("   This indicates tour context switching!")

    # Check if mentions Hoi An consistently
    mentions_hoi_an_1 = '호이안' in response1.lower()
    mentions_hoi_an_2 = '호이안' in response2.lower()

    print(f"   First response mentions Hoi An: {mentions_hoi_an_1}")
    print(f"   Second response mentions Hoi An: {mentions_hoi_an_2}")

    if mentions_hoi_an_1 and mentions_hoi_an_2:
        print("   ✅ SUCCESS: Consistently mentions Hoi An")
    elif not mentions_hoi_an_1 and not mentions_hoi_an_2:
        print("   ⚠️  WARNING: Neither response mentions Hoi An explicitly")
    else:
        print("   ❌ ERROR: Inconsistent tour naming")

if __name__ == "__main__":
    test_price_consistency()