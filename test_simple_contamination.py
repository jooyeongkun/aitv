import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_simple_contamination():
    """Simple test for contamination without Korean text issues"""
    print("=== Simple Contamination Test ===\n")

    # Test 1: Hoi An 5 people
    print("1. Testing Hoi An 5 people:")
    result1 = travel_ai.process_message("호이안 5명 얼마", conversation_id=9002)
    print(f"   Tours found: {result1['tours_found']}")

    response1 = result1.get('response', '')

    # Check for prices
    has_340 = '$340' in response1 or '340달러' in response1
    has_485 = '$485' in response1

    print(f"   Has $340 (rafting): {has_340}")
    print(f"   Has $485 (Hoi An): {has_485}")

    # Test 2: Follow-up question
    print("\n2. Follow-up - adding children:")
    result2 = travel_ai.process_message("아이 2명 추가하면?", conversation_id=9002)
    print(f"   Tours found: {result2['tours_found']}")

    response2 = result2.get('response', '')

    # Check for contamination
    has_340_2 = '$340' in response2 or '340달러' in response2
    has_485_2 = '$485' in response2
    mentions_hoi_an = 'hoi' in response2.lower() or '호이안' in response2.lower()

    print(f"   Has $340 (rafting): {has_340_2}")
    print(f"   Has $485 (Hoi An): {has_485_2}")
    print(f"   Mentions Hoi An: {mentions_hoi_an}")

    # Final analysis
    if has_340_2:
        print("\n   ❌ CONTAMINATION DETECTED: Rafting price in Hoi An context!")
    else:
        print("\n   ✅ SUCCESS: No rafting contamination!")

    if mentions_hoi_an:
        print("   ✅ SUCCESS: Maintains Hoi An context")
    else:
        print("   ⚠️ WARNING: Doesn't mention Hoi An explicitly")

if __name__ == "__main__":
    test_simple_contamination()