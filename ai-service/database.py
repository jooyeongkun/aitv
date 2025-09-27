import psycopg2
from psycopg2.extras import RealDictCursor
import os
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 캐시 (메모리)
DB_CACHE = {}
CACHE_EXPIRY = 300  # 5분

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'chat_consulting'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASS', 'admin123'),
        cursor_factory=RealDictCursor
    )

def get_cache_key(table_name, query_terms):
    """캐시 키 생성"""
    comma = ","
    key_data = f"{table_name}:{comma.join(sorted(query_terms))}"
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

    # 빈 검색어 처리 - 모든 호텔 반환
    if not query_terms or (len(query_terms) == 1 and query_terms[0] == ''):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            search_sql = """
                SELECT hotel_name, hotel_region, adult_price, child_price,
                       TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
                       TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
                       is_unlimited, child_criteria, description
                FROM hotels
                WHERE is_active = true
                ORDER BY hotel_region, hotel_name
                LIMIT 10
            """

            cursor.execute(search_sql)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            # 캐시 저장
            DB_CACHE[cache_key] = {
                'data': results,
                'timestamp': time.time()
            }

            return results
        except Exception as e:
            print(f"Hotel search error: {e}")
            return []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 최적화된 검색 쿼리 (LIMIT 추가)
        search_sql = """
            SELECT hotel_name, hotel_region, adult_price, child_price, 
                   TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
                   TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
                   is_unlimited, child_criteria, description
            FROM hotels 
            WHERE is_active = true 
            AND (LOWER(hotel_name) LIKE ANY(%s) 
                 OR LOWER(hotel_region) LIKE ANY(%s)
                 OR LOWER(description) LIKE ANY(%s))
            ORDER BY hotel_region, hotel_name
            LIMIT 10
        """
        
        search_patterns = [f'%{term.lower()}%' for term in query_terms]
        cursor.execute(search_sql, (search_patterns, search_patterns, search_patterns))
        
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
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
    
    # 빈 검색어 처리 - 모든 투어 반환
    if not query_terms or (len(query_terms) == 1 and query_terms[0] == ''):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            search_sql = """
                SELECT tour_name, tour_region, description, duration
                FROM tours
                WHERE is_active = true
                ORDER BY tour_region, tour_name
                LIMIT 10
            """

            cursor.execute(search_sql)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            # 캐시 저장
            DB_CACHE[cache_key] = {
                'data': results,
                'timestamp': time.time()
            }

            return results
        except Exception as e:
            print(f"Tour search error: {e}")
            return []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 최적화된 검색 쿼리 (LIMIT 추가)
        search_sql = """
            SELECT tour_name, tour_region, description, duration
            FROM tours
            WHERE is_active = true
            AND (LOWER(tour_name) LIKE ANY(%s)
                 OR LOWER(tour_region) LIKE ANY(%s)
                 OR LOWER(description) LIKE ANY(%s))
            ORDER BY tour_region, tour_name
            LIMIT 10
        """

        search_patterns = [f'%{term.lower()}%' for term in query_terms]
        cursor.execute(search_sql, (search_patterns, search_patterns, search_patterns))
        
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        # 캐시 저장
        DB_CACHE[cache_key] = {
            'data': results,
            'timestamp': time.time()
        }
        
        return results
        
    except Exception as e:
        print(f"Tour search error: {e}")
        return []
