import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# AI service initialization
travel_ai = TravelAI()

def test_helpful_guidance():
    """Test AI providing helpful guidance when information is insufficient"""
    print("=== Testing AI Helpful Guidance System ===\n")

    # Test scenarios that might trigger insufficient information errors
    test_cases = [
        {
            'message': '아이 요금',
            'description': 'Vague children pricing question',
            'conversation_id': 7001
        },
        {
            'message': '베스트팩 아이 추가하면',
            'description': 'Bestpack children addition without specifics',
            'conversation_id': 7002
        },
        {
            'message': '호이안 어린이',
            'description': 'Hoi An children question without details',
            'conversation_id': 7003
        },
        {
            'message': '투어 가격',
            'description': 'Generic tour pricing question',
            'conversation_id': 7004
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['description']}:")
        print(f"   Question: '{test_case['message']}'")

        result = travel_ai.process_message(test_case['message'], conversation_id=test_case['conversation_id'])
        response = result.get('response', '')

        print(f"   Response length: {len(response)}")
        print(f"   Has error_type: {'error_type' in result}")

        if 'error_type' in result:
            print(f"   Error type: {result['error_type']}")

        # Check if response provides helpful guidance
        helpful_indicators = [
            '구체적으로', '알려주세요', '예:', '정확한', '몇 명', '언제', '연령'
        ]

        has_guidance = any(indicator in response for indicator in helpful_indicators)
        print(f"   Provides guidance: {has_guidance}")

        if has_guidance:
            print("   ✅ SUCCESS: AI provides helpful guidance")
        else:
            print("   ❌ NEEDS IMPROVEMENT: Limited guidance provided")

        print()

    print("=== Test Complete ===")

if __name__ == "__main__":
    test_helpful_guidance()