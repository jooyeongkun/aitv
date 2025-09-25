import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_error_reporting():
    """Test improved error reporting system"""
    print("=== Testing Improved Error Reporting System ===\n")

    # Test 1: 베스트팩 3명 얼마 (should work now)
    print("1. Testing 'Bestpack 3 people price':")
    result1 = travel_ai.process_message("베스트팩 3명 얼마", conversation_id=6001)
    response1 = result1.get('response', '')

    print(f"   Tours found: {result1['tours_found']}")
    print(f"   Response length: {len(response1)}")
    print(f"   Has error_type: {'error_type' in result1}")

    if 'error_type' in result1:
        print(f"   Error type: {result1['error_type']}")
        if 'error_details' in result1:
            print(f"   Error details: {result1['error_details']}")

    has_valid_response = len(response1) > 10 and 'error_type' not in result1
    print(f"   Valid response: {has_valid_response}")

    # Test 2: 아이 2명 추가하면? (should also work with improved filtering)
    print("\n2. Follow-up - 'If we add 2 children':")
    result2 = travel_ai.process_message("아이 2명 추가하면?", conversation_id=6001)
    response2 = result2.get('response', '')

    print(f"   Tours found: {result2['tours_found']}")
    print(f"   Response length: {len(response2)}")
    print(f"   Has error_type: {'error_type' in result2}")

    if 'error_type' in result2:
        print(f"   Error type: {result2['error_type']}")
        if 'error_details' in result2:
            print(f"   Error details: {result2['error_details']}")

    has_valid_response_2 = len(response2) > 10 and 'error_type' not in result2
    print(f"   Valid response: {has_valid_response_2}")

    # Final analysis
    print("\n=== Final Analysis ===")
    if has_valid_response and has_valid_response_2:
        print("✅ SUCCESS: Both questions now work correctly!")
    elif has_valid_response:
        print("⚠️  PARTIAL: First question works, second still has issues")
    else:
        print("❌ ERROR: First question still fails")

    if not has_valid_response_2:
        print("The second question (children addition) may still need fixes")

if __name__ == "__main__":
    test_error_reporting()