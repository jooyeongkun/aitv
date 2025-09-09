"""
데이터베이스 데이터 확인 및 샘플 데이터 추가
"""
from supabase_db import SupabaseDB
from travel_ai_consultant_supabase import TravelAIConsultantSupabase

def main():
    # DB 연결
    db = SupabaseDB()
    if not db.connect():
        print("DB connection failed")
        return
        
    print("DB connected successfully")
    
    # 현재 데이터 확인
    packages = db.get_packages()
    hotels = db.get_hotels()
    
    print(f"\nCurrent packages: {len(packages)}")
    for pkg in packages:
        print(f"  - {pkg.get('name', 'N/A')}: {pkg.get('price', 0):,} KRW")
    
    print(f"\nCurrent hotels: {len(hotels)}") 
    for hotel in hotels:
        print(f"  - {hotel.get('name', 'N/A')}: {hotel.get('price_per_night', 0):,} KRW/night")
    
    # 데이터가 없으면 샘플 데이터 추가
    if len(packages) == 0:
        print("\nAdding sample package data...")
        sample_packages = [
            {
                "name": "Jeju Island 4-day Healing Trip",
                "destination": "제주",
                "price": 450000,
                "duration": 4,
                "includes": "Flight, accommodation, rental car, attraction tickets",
                "category": "Family"
            },
            {
                "name": "Busan 3-day Ocean Trip", 
                "destination": "부산",
                "price": 280000,
                "duration": 3,
                "includes": "Accommodation, Haeundae/Gwangalli tour, Jagalchi market",
                "category": "Couple"
            },
            {
                "name": "Gyeongju 3-day Culture Trip",
                "destination": "경주", 
                "price": 320000,
                "duration": 3,
                "includes": "Accommodation, Bulguksa/Seokguram tickets, Hanbok experience",
                "category": "Culture"
            }
        ]
        
        for pkg in sample_packages:
            if db.add_package(pkg):
                print(f"  Added: {pkg['name']}")
            else:
                print(f"  Failed: {pkg['name']}")
    
    if len(hotels) == 0:
        print("\nAdding sample hotel data...")
        sample_hotels = [
            {
                "name": "Jeju Ocean View Hotel",
                "city": "제주",
                "price_per_night": 120000,
                "star_rating": 4,
                "address": "Jeju-si Yeon-dong"
            },
            {
                "name": "Busan Haeundae Resort",
                "city": "부산", 
                "price_per_night": 150000,
                "star_rating": 5,
                "address": "Busan Haeundae-gu"
            },
            {
                "name": "Gyeongju Hanok Stay",
                "city": "경주",
                "price_per_night": 90000, 
                "star_rating": 3,
                "address": "Gyeongju Bulguk-dong"
            }
        ]
        
        for hotel in sample_hotels:
            if db.add_hotel(hotel):
                print(f"  Added: {hotel['name']}")
            else:
                print(f"  Failed: {hotel['name']}")
    
    # AI 테스트
    print("\n=== AI Consultation Test ===")
    consultant = TravelAIConsultantSupabase(db)
    test_message = "Recommend Jeju trip"
    session_id = db.create_consultation_session()
    
    print(f"Test question: {test_message}")
    response = consultant.generate_travel_recommendation(test_message, session_id)
    print(f"AI response: {response}")

if __name__ == "__main__":
    main()