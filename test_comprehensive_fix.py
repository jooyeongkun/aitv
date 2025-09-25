import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 encoding setting
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI service initialization
travel_ai = TravelAI()

def test_tour_isolation():
    """Test that tour information doesn't get mixed between different tours"""
    print("=== Testing Tour Information Isolation ===\n")

    # Test 1: Bestpack inquiry
    print("1. Testing Bestpack inquiry:")
    result1 = travel_ai.process_message("베스트팩 성인 얼마?", conversation_id=501)
    print(f"   Tours found: {result1['tours_found']}")
    print(f"   Response length: {len(result1['response'])}")
    print(f"   Contains forbidden phrases: {'1인 기준' in result1.get('response', '')}")
    print(f"   Validation score: {result1['validation']['overall_score']:.1f}")

    # Test 2: Light pack inquiry (new conversation)
    print("\n2. Testing Light Pack inquiry (new conversation):")
    result2 = travel_ai.process_message("라이트팩 성인 2명 가격", conversation_id=502)
    print(f"   Tours found: {result2['tours_found']}")
    print(f"   Response length: {len(result2['response'])}")
    print(f"   Contains forbidden phrases: {'1인 기준' in result2.get('response', '')}")
    print(f"   Validation score: {result2['validation']['overall_score']:.1f}")

    # Test 3: Follow-up question should maintain context
    print("\n3. Testing follow-up question (should maintain Light Pack context):")
    result3 = travel_ai.process_message("아이가격은?", conversation_id=502)
    print(f"   Tours found: {result3['tours_found']}")
    print(f"   Response length: {len(result3['response'])}")
    print(f"   Contains forbidden phrases: {'1인 기준' in result3.get('response', '')}")
    print(f"   Validation score: {result3['validation']['overall_score']:.1f}")

    # Test 4: Rafting inquiry (new conversation)
    print("\n4. Testing Rafting inquiry (new conversation):")
    result4 = travel_ai.process_message("래프팅 투어 가격", conversation_id=503)
    print(f"   Tours found: {result4['tours_found']}")
    print(f"   Response length: {len(result4['response'])}")
    print(f"   Contains forbidden phrases: {'1인 기준' in result4.get('response', '')}")
    print(f"   Validation score: {result4['validation']['overall_score']:.1f}")

    print("\n=== Test Results Summary ===")
    print("✅ All tests should show:")
    print("   - Tours found: 1 (strict filtering)")
    print("   - No forbidden phrases like '1인 기준'")
    print("   - Reasonable validation scores")
    print("   - Follow-up maintains correct context")

if __name__ == "__main__":
    test_tour_isolation()