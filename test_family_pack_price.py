import sys
import os
sys.path.append('ai-service')

# USE_SUPABASE 환경변수 설정
os.environ['USE_SUPABASE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

from ai_service import TravelAI

def test_family_pack_pricing():
    """패밀리팩 투어의 성인 4명 가격을 확인하는 테스트"""
    print("=== Family Pack Price Test ===")

    travel_ai = TravelAI()

    test_queries = [
        "패밀리팩 성인 4명 가격은?",
        "패밀리팩 투어 성인 4명 얼마인가요?",
        "패밀리팩 성인 4명",
        "family pack adult 4 people price"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)

        try:
            result = travel_ai.process_message(query, conversation_id=f"test_{i}")

            if isinstance(result, dict):
                response = result.get('response', 'No response')
                tours_found = result.get('tours_found', 0)
                hotels_found = result.get('hotels_found', 0)

                print(f"Tours found: {tours_found}")
                print(f"Hotels found: {hotels_found}")
                print(f"Response: {response}")

                # 가격 정보가 포함되어 있는지 확인
                if '$' in response or '원' in response or '달러' in response:
                    print("✅ Price information found in response")
                else:
                    print("❌ No price information found")

                # 패밀리팩 관련 정보가 포함되어 있는지 확인
                if '패밀리' in response.lower() or 'family' in response.lower():
                    print("✅ Family pack context maintained")
                else:
                    print("❌ Family pack context not found")

            else:
                print(f"Response: {result}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_family_pack_pricing()