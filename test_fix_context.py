import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_hoi_an_context_fix():
    """Test that AI maintains Hoi An context and doesn't show rafting"""
    print("=== Testing Hoi An Context Fix ===\n")

    # Test 1: 호이안 4명 질문 (컨텍스트 설정)
    print("1. Setting Hoi An context - '호이안 4명 얼마?'")
    result1 = travel_ai.process_message("호이안 4명 얼마?", conversation_id=6001)
    print(f"   Tours found: {result1['tours_found']}")
    print("   Context set successfully")

    # Test 2: 아이 2명 포함 질문 (컨텍스트 유지 테스트)
    print("\n2. Follow-up question - '아이 2명 포함하면?'")
    result2 = travel_ai.process_message("아이 2명 포함하면?", conversation_id=6001)

    response = result2.get('response', '').lower()
    print(f"   Tours found: {result2['tours_found']}")

    # Check if response maintains Hoi An context
    hoi_an_indicators = ['호이안', 'hoi an']
    has_hoi_an = any(indicator in response for indicator in hoi_an_indicators)

    # Check if response incorrectly shows tour packages (rafting etc.)
    tour_package_indicators = ['🎯', '투어 패키지', '래프팅']
    shows_tour_packages = any(indicator in response for indicator in tour_package_indicators)

    # Check specifically for rafting
    has_rafting = '래프팅' in response

    print(f"   Mentions Hoi An: {has_hoi_an}")
    print(f"   Shows tour packages: {shows_tour_packages}")
    print(f"   Mentions rafting: {has_rafting}")

    if not shows_tour_packages and not has_rafting:
        print("   ✅ SUCCESS: No incorrect tour packages shown")
    elif shows_tour_packages or has_rafting:
        print("   ❌ ERROR: Still showing incorrect tour packages/rafting")

    if has_hoi_an:
        print("   ✅ SUCCESS: Maintains Hoi An context")
    else:
        print("   ⚠️  WARNING: Doesn't mention Hoi An explicitly")

if __name__ == "__main__":
    test_hoi_an_context_fix()