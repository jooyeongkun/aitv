import sys
import os
sys.path.append('ai-service')

# USE_SUPABASE 환경변수 설정
os.environ['USE_SUPABASE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

from ai_service import TravelAI

def test_family_pack_english():
    """Test family pack pricing with English queries"""
    print("=== Family Pack Price Test (English) ===")

    travel_ai = TravelAI()

    test_queries = [
        "family pack adult 4 people price",
        "family pack tour 4 adults cost",
        "family pack pricing 4 people"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)

        try:
            result = travel_ai.process_message(query, conversation_id=f"test_eng_{i}")

            if isinstance(result, dict):
                response = result.get('response', 'No response')
                tours_found = result.get('tours_found', 0)
                hotels_found = result.get('hotels_found', 0)

                print(f"Tours found: {tours_found}")
                print(f"Hotels found: {hotels_found}")
                print(f"Response length: {len(response)} characters")

                # Check for price information
                has_price = any(indicator in response for indicator in ['$', 'won', 'dollar', 'USD', 'price', 'cost'])
                print(f"Contains price info: {has_price}")

                # Check for family pack context
                has_family = any(indicator in response.lower() for indicator in ['family', 'pack'])
                print(f"Contains family context: {has_family}")

                # Print first 200 characters of response
                print(f"Response preview: {response[:200]}...")

            else:
                print(f"Response: {result}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_family_pack_english()