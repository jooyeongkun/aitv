import sys
import os
sys.path.append('ai-service')
from ai_service import TravelAI

# UTF-8 encoding setting
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AI service initialization
travel_ai = TravelAI()

def test_subject_preservation():
    """Test that AI preserves the tour subject when the subject is omitted"""
    print("=== Testing Subject Preservation ===\n")

    # Test 1: 패밀리팩 성인 4명 문의 (주제 설정)
    print("1. Setting context - Family Pack adult 4:")
    result1 = travel_ai.process_message("패밀리팩 성인 4명은?", conversation_id=1001)
    print(f"   Response length: {len(result1['response'])}")
    print(f"   Tours found: {result1['tours_found']}")

    # Test 2: 주어 생략 - "아이 가격은요?" (패밀리팩이어야 함)
    print("\n2. Testing subject omission - should maintain Family Pack context:")
    result2 = travel_ai.process_message("아이 가격은요?", conversation_id=1001)

    response = result2.get('response', '')
    print(f"   Response length: {len(response)}")
    print(f"   Tours found: {result2['tours_found']}")

    # 응답 분석
    try:
        response_text = response.lower()

        # 패밀리팩 관련 키워드가 있는지 확인
        family_keywords = ['패밀리', 'family']
        has_family = any(keyword in response_text for keyword in family_keywords)

        # 래프팅 관련 키워드가 있는지 확인 (잘못된 경우)
        rafting_keywords = ['래프팅', 'rafting']
        has_rafting = any(keyword in response_text for keyword in rafting_keywords)

        if has_family and not has_rafting:
            print("   ✅ SUCCESS: Response mentions Family Pack, not Rafting")
        elif has_rafting and not has_family:
            print("   ❌ ERROR: Response mentions Rafting instead of Family Pack")
        elif has_rafting and has_family:
            print("   ❌ ERROR: Response mentions both tours (information mixing)")
        else:
            print("   ⚠️  WARNING: Response doesn't clearly mention tour type")

        print(f"   Contains 'Family' keywords: {has_family}")
        print(f"   Contains 'Rafting' keywords: {has_rafting}")

    except Exception as e:
        print(f"   Error analyzing response: {e}")

if __name__ == "__main__":
    test_subject_preservation()