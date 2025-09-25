#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ai_service import TravelAI

ai = TravelAI()
message = "다낭 호텔 추천해주세요"

print(f"메시지: {message}")
print(f"키워드: {ai.extract_keywords(message)}")
print(f"의도: {ai.determine_intent(message)}")

# 데이터베이스 검색 테스트
keywords = ai.extract_keywords(message)
intent = ai.determine_intent(message)
hotels, tours = ai.search_database(keywords, intent)

print(f"검색된 호텔 수: {len(hotels)}")
print(f"검색된 투어 수: {len(tours)}")

if hotels:
    print("호텔 데이터:")
    for hotel in hotels[:2]:
        print(f"  - {hotel}")