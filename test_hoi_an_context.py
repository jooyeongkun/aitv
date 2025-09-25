import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 encoding setting
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI service initialization
travel_ai = TravelAI()

def test_hoi_an_context_preservation():
    """Test that AI preserves Hoi An tour context when subject is omitted"""
    print("=== Testing Hoi An Context Preservation ===\n")

    # Test 1: 호이안 성인 3명 질문 (투어 주제 설정)
    print("1. Setting context - Hoi An adult 3:")
    result1 = travel_ai.process_message("호이안 성인 3명 얼마?", conversation_id=2001)
    print(f"   Response: {result1['response'][:100]}...")
    print(f"   Tours found: {result1['tours_found']}")

    # Test 2: 주어 생략 - "아이가격은요?" (호이안 투어여야 함)
    print("\n2. Testing subject omission - should maintain Hoi An context:")
    result2 = travel_ai.process_message("아이가격은요?", conversation_id=2001)

    response = result2.get('response', '')
    print(f"   Response: {response[:200]}...")
    print(f"   Tours found: {result2['tours_found']}")

    # 응답 분석
    try:
        response_text = response.lower()

        # 호이안 관련 키워드가 있는지 확인
        hoi_an_keywords = ['호이안', 'hoi an']
        has_hoi_an = any(keyword in response_text for keyword in hoi_an_keywords)

        # 다른 투어 관련 키워드가 있는지 확인 (잘못된 경우)
        other_tour_keywords = ['래프팅', 'rafting', '베스트팩', 'bestpack', '골프', 'golf', '패밀리팩', 'family']
        has_other_tours = any(keyword in response_text for keyword in other_tour_keywords)

        if has_hoi_an and not has_other_tours:
            print("   ✅ SUCCESS: Response mentions Hoi An only, no other tours")
        elif has_other_tours:
            print("   ❌ ERROR: Response mentions other tours instead of maintaining Hoi An context")
            print(f"   Found other tour keywords: {[kw for kw in other_tour_keywords if kw in response_text]}")
        else:
            print("   ⚠️  WARNING: Response doesn't clearly mention tour type")

        print(f"   Contains 'Hoi An' keywords: {has_hoi_an}")
        print(f"   Contains other tour keywords: {has_other_tours}")

    except Exception as e:
        print(f"   Error analyzing response: {e}")

if __name__ == "__main__":
    test_hoi_an_context_preservation()