import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_context_preservation():
    """Test that AI preserves tour context when subject is omitted"""
    print("=== Testing Context Preservation ===\n")

    # Test 1: First question to establish context
    print("1. Setting context - Hoi An adult 3:")
    result1 = travel_ai.process_message("호이안 성인 3명 얼마?", conversation_id=3001)
    print(f"   Tours found: {result1['tours_found']}")
    print("   Response created successfully")

    # Test 2: Subject omitted question
    print("\n2. Testing subject omission:")
    result2 = travel_ai.process_message("아이가격은요?", conversation_id=3001)
    print(f"   Tours found: {result2['tours_found']}")

    # Analyze response without printing Korean text
    response = result2.get('response', '').lower()

    # Check for Hoi An keywords
    hoi_an_keywords = ['호이안', 'hoi an']
    has_hoi_an = any(keyword in response for keyword in hoi_an_keywords)

    # Check for other tour keywords
    other_keywords = ['래프팅', 'rafting', '베스트팩', 'bestpack', '골프', 'golf', '패밀리팩']
    has_others = any(keyword in response for keyword in other_keywords)

    if has_hoi_an and not has_others:
        print("   ✅ SUCCESS: Maintains Hoi An context")
    elif has_others:
        print("   ❌ ERROR: Mentions other tours")
        print(f"   Found: {[kw for kw in other_keywords if kw in response]}")
    else:
        print("   ⚠️  WARNING: No clear tour reference")

    print(f"   Has Hoi An reference: {has_hoi_an}")
    print(f"   Has other tours: {has_others}")

if __name__ == "__main__":
    test_context_preservation()