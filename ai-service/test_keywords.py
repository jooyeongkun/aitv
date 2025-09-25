from ai_service import TravelAI

ai = TravelAI()
message = "다낭 호텔 추천해주세요"
keywords = ai.extract_keywords(message)
intent = ai.determine_intent(message)

print(f"메시지: {message}")
print(f"키워드: {keywords}")
print(f"의도: {intent}")

# 데이터베이스 검색 테스트
from database import search_hotels
hotels = search_hotels(keywords)
print(f"검색된 호텔: {len(hotels)}개")
for hotel in hotels:
    print(f"- {hotel['hotel_name']} ({hotel['hotel_region']})")