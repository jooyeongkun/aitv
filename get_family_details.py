import sys
import os
import json
sys.path.append('ai-service')

# USE_SUPABASE 환경변수 설정
os.environ['USE_SUPABASE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client, Client

# Supabase 클라이언트 초기화
supabase: Client = create_client(
    os.getenv('SUPABASE_URL', 'https://svztqkkmiskjfrflxyoi.supabase.co'),
    os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2enRxa2ttaXNramZyZmx4eW9pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MDc1NDIsImV4cCI6MjA3NDM4MzU0Mn0.Kf1ls9yp4bHojGkaJRLiWRDU6f36SsEWN9B8qy4ckEI')
)

def get_family_pack_details():
    print("Getting detailed family pack information...")

    try:
        # Get all columns from tours table to see what's available
        response = supabase.table('tours').select('*').eq('is_active', True).execute()

        tours = response.data
        print(f"Found {len(tours)} tours")

        # Find family pack tour
        family_tour = None
        for tour in tours:
            if '패밀리팩' in str(tour.get('tour_name', '')):
                family_tour = tour
                break

        if family_tour:
            print("\n=== FAMILY PACK TOUR DETAILS ===")

            # Save detailed info to JSON
            with open('family_pack_details.json', 'w', encoding='utf-8') as f:
                json.dump(family_tour, f, ensure_ascii=False, indent=2, default=str)

            print("Family pack details saved to family_pack_details.json")

            # Print key information
            print(f"Tour Name: {family_tour.get('tour_name', 'N/A')}")
            print(f"Region: {family_tour.get('tour_region', 'N/A')}")
            print(f"Duration: {family_tour.get('duration', 'N/A')}")
            print(f"Adult Price: {family_tour.get('adult_price', 'N/A')}")
            print(f"Child Price: {family_tour.get('child_price', 'N/A')}")
            print(f"Description: {family_tour.get('description', 'N/A')}")
            print(f"All available fields: {list(family_tour.keys())}")

        else:
            print("Family pack tour not found")

        # Also save all tours for reference
        with open('all_tours_detailed.json', 'w', encoding='utf-8') as f:
            json.dump(tours, f, ensure_ascii=False, indent=2, default=str)

        print(f"\nAll tours detailed info saved to all_tours_detailed.json")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_family_pack_details()