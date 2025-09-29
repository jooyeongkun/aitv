import sys
import os
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

def search_family_packages():
    print("=== Family Pack Tour Search ===")

    # Various keywords to search
    keywords_to_try = [
        ['family'],
        ['pack'],
        [''],  # All tours
    ]

    all_tours = []

    for keywords in keywords_to_try:
        print(f"\nKeywords: {keywords}")
        tours = search_tours(keywords)
        print(f"Search results: {len(tours)} tours")

        for tour in tours:
            if tour not in all_tours:
                all_tours.append(tour)
                print(f"- {tour.get('tour_name', 'Unknown')}")

    print(f"\n=== Total unique tours: {len(all_tours)} ===")

    # Filter family-related tours
    family_tours = []
    for tour in all_tours:
        tour_name = tour.get('tour_name', '').lower()
        if 'family' in tour_name or 'pack' in tour_name:
            family_tours.append(tour)

    print(f"\n=== Family Pack Tour Details ===")
    if family_tours:
        for i, tour in enumerate(family_tours, 1):
            print(f"\n{i}. Tour Name: {tour.get('tour_name', 'N/A')}")
            print(f"   Region: {tour.get('tour_region', 'N/A')}")
            print(f"   Duration: {tour.get('duration', 'N/A')}")

            # Check for price information
            print(f"   All data keys: {list(tour.keys())}")

            # Print description if available
            if tour.get('description'):
                description = tour['description']
                if len(description) > 200:
                    description = description[:200] + "..."
                print(f"   Description: {description}")

            print("-" * 60)
    else:
        print("No family pack tours found.")

        # Print all tour list
        print(f"\n=== All Tours List ({len(all_tours)}) ===")
        for tour in all_tours:
            print(f"- {tour.get('tour_name', 'Unknown')} ({tour.get('tour_region', 'Unknown')})")

if __name__ == "__main__":
    search_family_packages()