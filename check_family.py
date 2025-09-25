import sys
import os
sys.path.append('ai-service')
from database import search_hotels, search_tours

# UTF-8 인코딩 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=== Family Package Search ===")
hotels = search_hotels(['패밀리'])
tours = search_tours(['패밀리'])

print("\n=== Hotels ===")
for h in hotels:
    try:
        print(f"{h.get('hotel_name')} - {h.get('description', '')[:100]}")
    except:
        print("Hotel found but encoding issue")

print("\n=== Tours ===")
for t in tours:
    try:
        print(f"{t.get('tour_name')} - {t.get('description', '')[:100]}")
    except:
        print("Tour found but encoding issue")