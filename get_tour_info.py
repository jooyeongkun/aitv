import sys
import os
import json
sys.path.append('ai-service')

# USE_SUPABASE 환경변수 설정
os.environ['USE_SUPABASE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from database_supabase import search_tours, search_hotels
    print("Using Supabase database")
except ImportError:
    from database import search_tours, search_hotels
    print("Using PostgreSQL database")

def get_all_tour_info():
    print("Getting all tour information...")

    try:
        # Get all tours
        tours = search_tours([''])
        print(f"Found {len(tours)} tours")

        # Save to file to avoid encoding issues
        tour_data = []
        for i, tour in enumerate(tours):
            tour_info = {
                'index': i + 1,
                'tour_name': tour.get('tour_name', 'Unknown'),
                'tour_region': tour.get('tour_region', 'Unknown'),
                'duration': tour.get('duration', 'Unknown'),
                'description': tour.get('description', '')[:300] + ('...' if len(tour.get('description', '')) > 300 else ''),
                'all_keys': list(tour.keys())
            }
            tour_data.append(tour_info)

        # Save to JSON file
        with open('tour_info.json', 'w', encoding='utf-8') as f:
            json.dump(tour_data, f, ensure_ascii=False, indent=2)

        print(f"Tour information saved to tour_info.json")
        print("Check the JSON file for detailed tour information.")

        # Try to identify family pack tours
        family_tours = []
        for tour in tours:
            tour_name = str(tour.get('tour_name', '')).lower()
            if 'family' in tour_name or 'pack' in tour_name or '패밀리' in tour_name:
                family_tours.append(tour)

        print(f"\nFound {len(family_tours)} potential family pack tours")

        return tours

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    get_all_tour_info()