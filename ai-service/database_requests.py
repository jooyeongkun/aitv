import requests
import os
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 캐시 (메모리)
DB_CACHE = {}
CACHE_EXPIRY = 300  # 5분

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://svztqkkmiskjfrflxyoi.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2enRxa2ttaXNramZyZmx4eW9pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MDc1NDIsImV4cCI6MjA3NDM4MzU0Mn0.Kf1ls9yp4bHojGkaJRLiWRDU6f36SsEWN9B8qy4ckEI')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def get_cache_key(table_name, query_terms):
    """캐시 키 생성"""
    key_data = f"{table_name}:{','.join(sorted(query_terms))}"
    return hashlib.md5(key_data.encode('utf-8')).hexdigest()

def is_cache_valid(timestamp):
    """캐시 유효성 확인"""
    return time.time() - timestamp < CACHE_EXPIRY

def search_hotels(query_terms):
    """호텔 데이터에서 검색 (캐시 적용)"""
    # 캐시 확인
    cache_key = get_cache_key('hotels', query_terms)
    if cache_key in DB_CACHE and is_cache_valid(DB_CACHE[cache_key]['timestamp']):
        try:
            print(f"Using cached hotel results for: {', '.join(query_terms[:2])}")
        except UnicodeEncodeError:
            print("Using cached hotel results")
        return DB_CACHE[cache_key]['data']

    try:
        # Supabase REST API 호출
        url = f"{SUPABASE_URL}/rest/v1/hotels"
        params = {
            'is_active': 'eq.true',
            'order': 'hotel_region,hotel_name',
            'limit': 10,
            'select': 'hotel_name,hotel_region,adult_price,child_price,promotion_start,promotion_end,is_unlimited,child_criteria,description'
        }

        # 검색어가 있는 경우 필터 추가
        if query_terms and query_terms[0] != '':
            term = query_terms[0].lower()
            params['or'] = f"hotel_name.ilike.%{term}%,hotel_region.ilike.%{term}%,description.ilike.%{term}%"

        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()

        results = response.json()

        # 캐시 저장
        DB_CACHE[cache_key] = {
            'data': results,
            'timestamp': time.time()
        }

        # 캐시 크기 제한 (최대 50개)
        if len(DB_CACHE) > 50:
            oldest_keys = sorted(DB_CACHE.keys(), key=lambda k: DB_CACHE[k]['timestamp'])[:10]
            for key in oldest_keys:
                del DB_CACHE[key]

        return results

    except Exception as e:
        print(f"Hotel search error: {e}")
        return []

def search_tours(query_terms):
    """투어 데이터에서 검색 (캐시 적용)"""
    # 캐시 확인
    cache_key = get_cache_key('tours', query_terms)
    if cache_key in DB_CACHE and is_cache_valid(DB_CACHE[cache_key]['timestamp']):
        try:
            print(f"Using cached tour results for: {', '.join(query_terms[:2])}")
        except UnicodeEncodeError:
            print("Using cached tour results")
        return DB_CACHE[cache_key]['data']

    try:
        # Supabase REST API 호출
        url = f"{SUPABASE_URL}/rest/v1/tours"
        params = {
            'is_active': 'eq.true',
            'order': 'display_order,tour_name',
            'limit': 10,
            'select': 'tour_name,tour_region,description,duration'
        }

        # 검색어가 있는 경우 필터 추가
        if query_terms and query_terms[0] != '':
            term = query_terms[0].lower()
            params['or'] = f"tour_name.ilike.%{term}%,tour_region.ilike.%{term}%,description.ilike.%{term}%"

        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()

        results = response.json()

        # 캐시 저장
        DB_CACHE[cache_key] = {
            'data': results,
            'timestamp': time.time()
        }

        return results

    except Exception as e:
        print(f"Tour search error: {e}")
        return []