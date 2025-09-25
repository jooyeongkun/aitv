import sys
import os
sys.path.append('ai-service')
from database import search_tours

# UTF-8 인코딩 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=== Bestpack Tour Data Check ===")
tours = search_tours(['베스트'])

for tour in tours:
    try:
        print(f"\n투어명: {tour['tour_name']}")
        print(f"지역: {tour['tour_region']}")
        print(f"설명: {tour.get('description', 'N/A')}")
        print(f"기간: {tour.get('duration', 'N/A')}")
        # 모든 키 출력
        print("전체 데이터:")
        for key, value in tour.items():
            print(f"  {key}: {value}")
    except UnicodeEncodeError:
        print("투어 정보 (인코딩 문제)")
        print("전체 데이터:")
        for key, value in tour.items():
            try:
                print(f"  {key}: {value}")
            except:
                print(f"  {key}: [한글 데이터]")
    print("-" * 50)