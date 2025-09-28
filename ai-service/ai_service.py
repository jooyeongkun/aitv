from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# 환경에 따라 다른 데이터베이스 모듈 사용
if os.getenv('USE_SUPABASE', 'false').lower() == 'true':
    try:
        from database_requests import search_hotels, search_tours
    except ImportError:
        from database import search_hotels, search_tours
else:
    from database import search_hotels, search_tours

class TravelAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.last_search_results = {'hotels': [], 'tours': []}  # 마지막 검색 결과 저장
        self.conversation_history = {}  # conversation_id별 대화 히스토리
        self.response_cache = {}  # 응답 캐시
        self.database_cache = {}  # 데이터베이스 쿼리 캐시
        self.validation_logs = []  # 자가 검증 로그
    
    
    def is_greeting(self, user_message):
        """인사말 체크"""
        greetings = ['안녕하세요', '안녕', 'hi', 'hello', '헬로', '하이']
        return any(greeting in user_message.lower().strip() for greeting in greetings)

    def get_welcome_message_with_packages(self):
        """환영 메시지와 함께 패키지 목록 반환"""
        try:
            # 투어 목록만 조회
            tours = search_tours([])    # 모든 투어

            message = "안녕하세요! 😊 여행 상담사입니다.\n\n현재 보유한 패키지는 다음과 같습니다:\n\n"

            # 투어 목록 추가
            if tours:
                message += "🎯 **투어 패키지:**\n"
                for tour in tours:  # 모든 투어 표시
                    message += f"• {tour['tour_name']}\n"
                message += "\n"

            message += "어떤 여행을 계획하고 계신가요? 궁금한 점이 있으시면 언제든 말씀해주세요!"

            return message

        except Exception as e:
            print(f"패키지 목록 조회 오류: {e}")
            return "안녕하세요! 😊 여행 상담사입니다. 무엇을 도와드릴까요?"

    # ========== 자가 검증 시스템 ==========
    def validate_intent_accuracy(self, user_message, detected_intent, keywords, search_results):
        """질문 의도 파악 정확도 검증"""
        validation_score = 0
        issues = []

        # 1. 키워드와 의도 일치성 검증
        if detected_intent == 'price':
            price_indicators = ['얼마', '가격', '비용', '요금', '금액', '돈']
            if any(indicator in user_message for indicator in price_indicators):
                validation_score += 30
            else:
                issues.append("가격 의도이지만 가격 관련 키워드가 없음")

        if detected_intent in ['tour', 'hotel']:
            relevant_keywords = [k for k in keywords if k in ['투어', '여행', '관광', '호텔', '숙박']]
            if relevant_keywords:
                validation_score += 25
            else:
                issues.append(f"{detected_intent} 의도이지만 관련 키워드가 부족함")

        # 2. 검색 결과 적합성 검증
        if detected_intent == 'hotel':
            if search_results['hotels']:
                validation_score += 25
            else:
                issues.append("호텔 의도이지만 호텔 결과가 없음")

        if detected_intent == 'tour':
            if search_results['tours']:
                validation_score += 25
            else:
                issues.append("투어 의도이지만 투어 결과가 없음")

        # 3. 키워드 추출 적절성 검증
        if len(keywords) == 0 and not self.is_greeting(user_message):
            issues.append("키워드가 추출되지 않음")
        elif len(keywords) > 7:
            issues.append("너무 많은 키워드가 추출됨")
        else:
            validation_score += 20

        return {
            'score': validation_score,
            'issues': issues,
            'status': 'good' if validation_score >= 80 else 'warning' if validation_score >= 60 else 'poor'
        }

    def validate_conversation_continuity(self, user_message, conversation_id, current_results):
        """대화 연속성 검증"""
        validation_score = 0
        issues = []

        if not conversation_id or conversation_id not in self.conversation_history:
            return {'score': 100, 'issues': [], 'status': 'good'}  # 첫 대화는 검증 제외

        context = self.conversation_history[conversation_id]
        recent_messages = context.get('messages', [])[-3:]  # 최근 3개 메시지

        if not recent_messages:
            return {'score': 100, 'issues': [], 'status': 'good'}

        # 1. 주제 연속성 검증
        last_message = recent_messages[-1] if recent_messages else None
        if last_message:
            last_user_msg = last_message.get('user', '')
            last_ai_msg = last_message.get('ai', '')

            # 이전 대화에서 특정 투어/호텔을 언급했는지 확인
            mentioned_tours = ['골프', '래프팅', '패밀리', '라이트', '베스트', '바나힐', '호이안']
            prev_tour_type = None
            for tour_type in mentioned_tours:
                if tour_type in last_user_msg or tour_type in last_ai_msg:
                    prev_tour_type = tour_type
                    break

            # 현재 메시지가 연속적인지 확인
            follow_up_patterns = ['추가', '더', '그럼', '아이', '어린이', '성인', '명', '몇', '얼마', '가격']
            is_follow_up = any(pattern in user_message for pattern in follow_up_patterns)

            if prev_tour_type and is_follow_up:
                # 연속 대화인 경우 같은 주제의 결과가 있는지 확인
                if current_results['tours'] or current_results['hotels']:
                    validation_score += 50
                else:
                    issues.append("연속 대화이지만 관련 결과를 찾지 못함")
            else:
                validation_score += 30

        # 2. 맥락 보존 검증
        if context.get('current_topic'):
            if (context['current_topic'] == 'tour' and current_results['tours']) or \
               (context['current_topic'] == 'hotel' and current_results['hotels']):
                validation_score += 30
            elif not any([current_results['tours'], current_results['hotels']]):
                # 새로운 주제로 전환된 경우는 문제 없음
                validation_score += 30
            else:
                issues.append("이전 대화 맥락과 현재 결과가 일치하지 않음")
        else:
            validation_score += 20

        return {
            'score': validation_score,
            'issues': issues,
            'status': 'good' if validation_score >= 80 else 'warning' if validation_score >= 60 else 'poor'
        }

    def validate_response_quality(self, user_message, ai_response, search_results):
        """AI 응답 품질 검증"""
        validation_score = 0
        issues = []

        # 1. 응답 길이 적절성
        if 20 <= len(ai_response) <= 500:
            validation_score += 20
        elif len(ai_response) < 20:
            issues.append("응답이 너무 짧음")
        else:
            issues.append("응답이 너무 길음")

        # 2. 검색 결과 활용도 검증
        total_results = len(search_results.get('hotels', [])) + len(search_results.get('tours', []))
        if total_results > 0:
            # 실제 데이터를 활용한 응답인지 확인
            data_indicators = ['원', '가격', '기간', '투어', '호텔', '예약']
            if any(indicator in ai_response for indicator in data_indicators):
                validation_score += 30
            else:
                issues.append("검색 결과가 있지만 응답에 반영되지 않음")
        else:
            # 검색 결과가 없는 경우 적절한 안내를 했는지
            if '찾을 수 없' in ai_response or '확인할 수 없' in ai_response:
                validation_score += 25
            else:
                issues.append("검색 결과가 없는데 적절한 안내가 없음")

        # 3. 가격 문의에 대한 정확성
        if '얼마' in user_message or '가격' in user_message:
            if '원' in ai_response and any(char.isdigit() for char in ai_response):
                validation_score += 25
            else:
                issues.append("가격 문의이지만 구체적인 금액 정보가 없음")
        else:
            validation_score += 25

        return {
            'score': validation_score,
            'issues': issues,
            'status': 'good' if validation_score >= 80 else 'warning' if validation_score >= 60 else 'poor'
        }

    def perform_self_validation(self, user_message, conversation_id, detected_intent, keywords, search_results, ai_response):
        """종합 자가 검증 수행"""
        import time

        # 개별 검증 수행
        intent_validation = self.validate_intent_accuracy(user_message, detected_intent, keywords, search_results)
        continuity_validation = self.validate_conversation_continuity(user_message, conversation_id, search_results)
        response_validation = self.validate_response_quality(user_message, ai_response, search_results)

        # 종합 점수 계산
        overall_score = (intent_validation['score'] + continuity_validation['score'] + response_validation['score']) / 3

        # 검증 결과 로깅
        validation_result = {
            'timestamp': time.time(),
            'conversation_id': conversation_id,
            'user_message': user_message,
            'detected_intent': detected_intent,
            'keywords_count': len(keywords),
            'search_results_count': len(search_results.get('hotels', [])) + len(search_results.get('tours', [])),
            'response_length': len(ai_response),
            'intent_validation': intent_validation,
            'continuity_validation': continuity_validation,
            'response_validation': response_validation,
            'overall_score': overall_score,
            'overall_status': 'good' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'poor'
        }

        self.validation_logs.append(validation_result)

        # 최근 100개만 유지
        if len(self.validation_logs) > 100:
            self.validation_logs = self.validation_logs[-100:]

        # 검증 결과 출력 (개발용)
        try:
            print(f"Self-Validation Score: {overall_score:.1f} ({validation_result['overall_status'].upper()})")
            if validation_result['overall_status'] != 'good':
                all_issues = intent_validation['issues'] + continuity_validation['issues'] + response_validation['issues']
                if all_issues:
                    print(f"Issues found: {', '.join(all_issues[:3])}")  # 최대 3개만 표시
        except UnicodeEncodeError:
            print(f"Self-Validation Score: {overall_score:.1f}")

        return validation_result

    def get_synonyms(self, word):
        """단어의 유사단어/동의어 반환"""
        synonym_dict = {
            # 투어 유형
            '패밀리': ['패밀리팩', 'family', '가족', '가족투어', '가족패키지'],
            '골프': ['golf', '골프투어', '골프패키지', '골프여행', '골핑'],
            '래프팅': ['rafting', '급류타기', '래프팅투어', '물놀이'],
            '바나힐': ['바나 힐', 'bana hill', 'banahil', '바나힐투어'],
            '스쿠버': ['scuba', '다이빙', 'diving', '스노클링', '스쿠버다이빙'],
            '라이트': ['라이트팩', 'light', '라이트투어'],
            '베스트': ['베스트팩', 'best', '베스트투어'],

            # 지역
            '다낭': ['danang', 'da nang', '다낭시'],
            '호이안': ['hoian', 'hoi an', '호이안시'],
            '나트랑': ['nhatrang', 'nha trang', '나트랑시'],
            '푸꾸옥': ['phuquoc', 'phu quoc', '푸꾸옥섬'],

            # 숙박
            '호텔': ['hotel', '숙박', '숙소', '리조트', 'resort'],
            '리조트': ['resort', '호텔', 'hotel', '펜션'],

            # 가격 관련
            '가격': ['비용', '요금', '얼마', '돈', '금액', '값'],
            '비용': ['가격', '요금', '얼마', '돈', '금액', '값'],

            # 정보 요청
            '구성': ['내용', '포함', '정보', '상세', '설명', '뭐'],
            '내용': ['구성', '포함', '정보', '상세', '설명', '뭐에요'],
            '정보': ['내용', '구성', '상세', '설명', '알려줘'],
        }

        word_lower = word.lower()
        synonyms = []

        # 직접 매칭
        if word_lower in synonym_dict:
            synonyms.extend(synonym_dict[word_lower])

        # 역방향 매칭 (동의어에서 원래 단어 찾기)
        for key, values in synonym_dict.items():
            if word_lower in [v.lower() for v in values]:
                synonyms.append(key)
                synonyms.extend(values)

        # 중복 제거 및 원본 제외
        unique_synonyms = []
        for s in synonyms:
            if s.lower() != word_lower and s not in unique_synonyms:
                unique_synonyms.append(s)

        return unique_synonyms

    def extract_keywords(self, user_message):
        """사용자 메시지에서 키워드 추출"""
        import re
        
        # 빈 메시지 처리
        if not user_message or user_message.strip() == '':
            return []
        
        keywords = []
        
        # 지역 키워드 (데이터베이스에서 동적으로 조회)
        available_regions = self.get_available_regions()
        for region in available_regions:
            if region in user_message:
                keywords.append(region)
        
        # 호텔 관련 키워드
        hotel_keywords = ['호텔', '숙박', '리조트', '펜션', '게스트하우스', '객실', '룸']
        for keyword in hotel_keywords:
            if keyword in user_message:
                keywords.append(keyword)
        
        # 투어 관련 키워드
        tour_keywords = ['투어', '여행', '관광', '체험', '액티비티', '일정', '래프팅', '골프', '바나힐', '호이안', '패밀리', '패밀리팩', '라이트', '라이트팩', '베스트', '베스트팩']

        # 가격 관련 키워드 (유아, 아동 포함)
        price_keywords = ['가격', '얼마', '비용', '요금', '돈', '금액', '값', '성인', '어른', '아이', '아동', '유아', '소아', '어린이', '애기', '몇명', '몇 명', '인원']
        for keyword in tour_keywords:
            if keyword in user_message:
                keywords.append(keyword)

        # 가격/인원 관련 키워드 추가
        for keyword in price_keywords:
            if keyword in user_message:
                keywords.append(keyword)

        # 한글 단어 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', user_message)
        for word in korean_words:
            if word not in keywords:
                keywords.append(word)

        # 영문 단어 추출
        english_words = re.findall(r'[a-zA-Z]{2,}', user_message)
        for word in english_words:
            if word.lower() not in [k.lower() for k in keywords]:
                keywords.append(word)

        # 동의어 확장
        expanded_keywords = []
        for keyword in keywords:
            expanded_keywords.append(keyword)
            # 동의어 추가
            synonyms = self.get_synonyms(keyword)
            expanded_keywords.extend(synonyms[:3])  # 각 키워드당 최대 3개의 동의어만

        # 중복 제거하고 최대 10개만 (동의어 포함)
        unique_keywords = []
        for k in expanded_keywords:
            if k and k.strip() and k not in unique_keywords:
                unique_keywords.append(k)

        return unique_keywords[:10]
    
    def determine_intent(self, user_message):
        """사용자 의도 파악"""
        user_message_lower = user_message.lower()

        # 패키지 목록 문의
        if any(keyword in user_message_lower for keyword in ['무슨 패키지', '어떤 패키지', '패키지가 있', '패키지 뭐', '어떤거 있어', '무엇이 있어']):
            return 'general'
        elif any(keyword in user_message_lower for keyword in ['투어', '관광', '체험', '액티비티', '투어가']):
            return 'tour'
        elif any(keyword in user_message_lower for keyword in ['호텔', '숙박', '리조트', '펜션']):
            return 'hotel'
        elif any(keyword in user_message_lower for keyword in ['가격', '비용', '요금', '얼마', '명은', '명이면', '인은', '인이면', '돈', '금액']):
            return 'price'
        else:
            return 'general'
    
    def get_available_regions(self):
        """데이터베이스에서 실제 사용 가능한 지역 조회"""
        try:
            from database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 호텔과 투어에서 사용 가능한 지역 조회
            cursor.execute("SELECT DISTINCT hotel_region FROM hotels WHERE is_active = true")
            hotel_regions = [row['hotel_region'] for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT tour_region FROM tours WHERE is_active = true")
            tour_regions = [row['tour_region'] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            # 중복 제거하고 정렬
            all_regions = list(set(hotel_regions + tour_regions))
            return sorted(all_regions)
            
        except Exception as e:
            print(f"Error getting available regions: {e}")
            return ['다낭']  # 기본값
    
    def search_database(self, keywords, intent, conversation_id=None):
        """데이터베이스에서 검색"""
        hotels = []
        tours = []

        # 대화 컨텍스트 기반 검색 개선
        context = self.get_conversation_context(conversation_id) if conversation_id else None

        # 주제 전환 감지: 새로운 투어 종류가 명시적으로 언급되면 이전 맥락 무시
        tour_type_keywords = ['패밀리', '베스트', '라이트', '골프', '래프팅', '바나힐', '호이안']
        current_tour_type = None
        for keyword in keywords:
            for tour_type in tour_type_keywords:
                if tour_type in keyword.lower():
                    current_tour_type = tour_type
                    break

        # 새로운 투어 종류가 명시적으로 언급되면 이전 검색 결과 초기화
        if current_tour_type:
            try:
                print(f"New tour type detected: {current_tour_type}. Clearing previous context.")
            except UnicodeEncodeError:
                print("New tour type detected. Clearing previous context.")
            self.last_search_results = {'hotels': [], 'tours': []}
            # 해당 conversation의 current_topic도 초기화
            if context:
                context['current_topic'] = None

        # 가격 문의인 경우 이전 검색 결과를 우선 사용 (단, 새 투어 종류가 없는 경우만)
        if intent == 'price' and not current_tour_type and (self.last_search_results['hotels'] or self.last_search_results['tours']):
            print("Using previous search results for price inquiry")
            return self.last_search_results['hotels'], self.last_search_results['tours']
        
        # 실제 데이터베이스에서 사용 가능한 지역 조회
        available_regions = self.get_available_regions()
        
        # 저장된 현재 투어 종류가 있으면 우선 사용
        if context and context.get('current_tour_type') and not current_tour_type:
            stored_tour_type = context['current_tour_type']
            keywords.append(stored_tour_type)
            try:
                print(f"Using stored tour type from context: {stored_tour_type}")
            except UnicodeEncodeError:
                print("Using stored tour type from context")
            # 저장된 투어 타입이 있을 때는 해당 타입만 검색하도록 current_tour_type 설정
            current_tour_type = stored_tour_type

        # 이전 대화에서 언급된 지역과 투어 유형 정보 추가 (새 투어 종류가 없고 저장된 투어 종류도 없는 경우만)
        elif context and context.get('messages') and not current_tour_type:
            last_regions = []
            last_tour_types = []

            for msg in context['messages'][-3:]:  # 최근 3개 대화
                user_msg = msg.get('user', '')
                ai_msg = msg.get('ai', '')

                # 지역 정보 추출
                for region in available_regions:
                    if region in user_msg and region not in keywords:
                        last_regions.append(region)

                # 투어 유형 정보 추출 (이전 대화에서 언급된 투어 유형)
                if '골프' in user_msg or 'golf' in user_msg.lower() or '골프' in ai_msg:
                    if '골프' not in keywords:
                        last_tour_types.append('골프')
                elif '래프팅' in user_msg or 'rafting' in user_msg.lower() or '래프팅' in ai_msg:
                    if '래프팅' not in keywords:
                        last_tour_types.append('래프팅')
                elif '패밀리' in user_msg or 'family' in user_msg.lower() or '패밀리' in ai_msg:
                    if '패밀리' not in keywords:
                        last_tour_types.append('패밀리')
                elif '라이트' in user_msg or 'light' in user_msg.lower() or '라이트' in ai_msg:
                    if '라이트' not in keywords:
                        last_tour_types.append('라이트')
                elif '베스트' in user_msg or 'best' in user_msg.lower() or '베스트' in ai_msg:
                    if '베스트' not in keywords:
                        last_tour_types.append('베스트')

            if last_regions:
                keywords.extend(last_regions[:1])  # 가장 최근 지역 1개 추가
                try:
                    print(f"Added region from context: {last_regions[0]}")
                except UnicodeEncodeError:
                    print("Added region from context: [Korean region]")

            if last_tour_types:
                keywords.extend(last_tour_types[:1])  # 가장 최근 투어 유형 1개 추가
                try:
                    print(f"Added tour type from context: {last_tour_types[0]}")
                except UnicodeEncodeError:
                    print("Added tour type from context: [Korean tour type]")
        
        if intent == 'hotel':
            hotels = search_hotels(keywords)
        elif intent == 'tour':
            tours = search_tours(keywords)
        elif intent in ['general', 'price']:
            # 일반 질문이나 빈 키워드인 경우
            if not keywords or len([k for k in keywords if k.strip()]) == 0:
                # 이전 검색 결과가 있으면 재사용 (연속 대화 지원)
                if hasattr(self, 'last_search_results') and self.last_search_results:
                    hotels = self.last_search_results.get('hotels', [])
                    tours = self.last_search_results.get('tours', [])
                    try:
                        print("Using previous search results for continuity")
                    except UnicodeEncodeError:
                        print("Using previous search results")
                else:
                    hotels = search_hotels([''])  # 빈 문자열로 검색하면 모든 호텔
                    tours = search_tours([''])    # 빈 문자열로 검색하면 모든 투어
            else:
                hotels = search_hotels(keywords)
                tours = search_tours(keywords)
        
        # 특정 투어 종류가 명시된 경우 해당 종류만 필터링
        if current_tour_type and tours:
            filtered_tours = []
            for tour in tours:
                tour_name_lower = tour.get('tour_name', '').lower()
                if current_tour_type.lower() in tour_name_lower:
                    filtered_tours.append(tour)
            tours = filtered_tours
            try:
                print(f"Filtered tours by type '{current_tour_type}': {len(tours)} tours found")
            except UnicodeEncodeError:
                print(f"Filtered tours by type: {len(tours)} tours found")

        # 검색 결과 저장 (항상 저장)
        if hotels or tours:
            self.last_search_results = {'hotels': hotels, 'tours': tours}

        return hotels, tours
    
    def format_hotel_info(self, hotel):
        """호텔 정보 포맷팅"""
        info = f"🏨 **{hotel['hotel_name']}** ({hotel['hotel_region']})\n"

        if hotel.get('promotion_start') and hotel.get('promotion_end'):
            if hotel.get('is_unlimited'):
                info += f"📅 프로모션: 무제한\n"
            else:
                info += f"📅 프로모션: {hotel['promotion_start']} ~ {hotel['promotion_end']}\n"

        if hotel.get('description'):
            info += f"📝 {hotel['description'][:100]}{'...' if len(hotel['description']) > 100 else ''}\n"

        return info
    
    def format_tour_info(self, tour):
        """투어 정보 포맷팅"""
        info = f"🚌 **{tour['tour_name']}** ({tour['tour_region']})\n"

        # 기간 정보 추가
        if tour.get('duration'):
            info += f"📅 **{tour['duration']}**\n"

        # 가격 정보 추가 (매우 중요!)
        if tour.get('adult_price'):
            info += f"💰 **성인가격**: {tour['adult_price']}\n"

        if tour.get('child_price'):
            info += f"👶 **아동가격**: {tour['child_price']}\n"

        if tour.get('infant_price'):
            info += f"🍼 **유아가격**: {tour['infant_price']}\n"

        if tour.get('child_criteria'):
            info += f"📏 **아동기준**: {tour['child_criteria']}\n"

        if tour.get('infant_criteria'):
            info += f"📏 **유아기준**: {tour['infant_criteria']}\n"

        # 상세 설명은 별도 함수에서 처리

        return info

    def extract_relevant_description(self, description, user_message):
        """사용자 질문에 따라 상세내용에서 관련 부분만 추출"""
        if not description:
            return ""

        user_msg_lower = user_message.lower()
        lines = description.split('\n')
        relevant_lines = []

        # 질문 유형별 키워드 정의
        query_keywords = {
            'price': ['가격', '얼마', '비용', '요금', '돈', '금액', '값', '$', '만원', '원', '유아', '아동', '성인', '어른'],
            'schedule': ['일정', '스케줄', '시간', '몇시', '언제', '일차', '날짜'],
            'content': ['내용', '구성', '포함', '활동', '체험', '프로그램'],
            'location': ['위치', '장소', '어디', '지역', '주소'],
            'criteria': ['기준', '나이', '몇살', '연령', '조건']
        }

        # 사용자 질문이 어떤 유형인지 판단
        detected_types = []
        for query_type, keywords in query_keywords.items():
            if any(keyword in user_msg_lower for keyword in keywords):
                detected_types.append(query_type)

        # 관련 키워드가 포함된 줄 추출
        if detected_types:
            for line in lines:
                line_lower = line.lower()
                for query_type in detected_types:
                    if any(keyword in line_lower for keyword in query_keywords[query_type]):
                        relevant_lines.append(line.strip())
                        break

        # 관련 정보를 찾지 못했으면 전체 설명의 앞부분 반환
        if not relevant_lines:
            return description[:300] + ('...' if len(description) > 300 else '')

        # 관련 정보만 반환 (최대 500자)
        result = '\n'.join(relevant_lines)
        return result[:500] + ('...' if len(result) > 500 else '')

    def get_conversation_context(self, conversation_id):
        """대화 컨텍스트 조회"""
        return self.conversation_history.get(conversation_id, {
            'messages': [],
            'current_topic': None,
            'mentioned_tours': [],
            'mentioned_hotels': [],
            'greeted': False
        })
    
    def update_conversation_context(self, conversation_id, user_message, ai_response, hotels, tours):
        """대화 컨텍스트 업데이트"""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = {
                'messages': [],
                'current_topic': None,
                'mentioned_tours': [],
                'mentioned_hotels': [],
                'greeted': False
            }
        
        context = self.conversation_history[conversation_id]
        context['messages'].append({'user': user_message, 'ai': ai_response})
        
        # 현재 주제 업데이트 - 구체적인 투어 종류도 저장
        if tours:
            context['current_topic'] = 'tour'
            context['mentioned_tours'] = tours

            # 현재 투어의 구체적인 종류 파악
            current_tour_type = None
            tour_type_keywords = ['패밀리', '베스트', '라이트', '골프', '래프팅', '바나힐', '호이안']
            for tour in tours:
                tour_name = tour.get('tour_name', '').lower()
                for tour_type in tour_type_keywords:
                    if tour_type in tour_name:
                        current_tour_type = tour_type
                        break
                if current_tour_type:
                    break

            if current_tour_type:
                context['current_tour_type'] = current_tour_type
                try:
                    print(f"Updated context with tour type: {current_tour_type}")
                except UnicodeEncodeError:
                    print("Updated context with tour type")

        elif hotels:
            context['current_topic'] = 'hotel'
            context['mentioned_hotels'] = hotels
        
        # 최근 10개 메시지만 유지
        if len(context['messages']) > 10:
            context['messages'] = context['messages'][-10:]
    
    def get_cache_key(self, user_message, hotels, tours, conversation_id=None):
        """캐시 키 생성"""
        import hashlib
        
        # 메시지와 검색 결과를 기반으로 캐시 키 생성
        cache_data = {
            'message': user_message.lower().strip(),
            'hotel_count': len(hotels),
            'tour_count': len(tours),
            'hotel_names': [h['hotel_name'] for h in hotels[:2]] if hotels else [],
            'tour_names': [t['tour_name'] for t in tours[:2]] if tours else []
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_str.encode('utf-8')).hexdigest()
    
    def generate_response(self, user_message, hotels, tours, conversation_id=None):
        """AI 응답 생성 (캐시 적용)"""
        try:
            # 캐시 확인
            cache_key = self.get_cache_key(user_message, hotels, tours, conversation_id)
            if cache_key in self.response_cache:
                print(f"Using cached response for key: {cache_key[:8]}...")
                cached_response = self.response_cache[cache_key]

                # 🚨 캐시된 응답도 필터링 적용
                conversation_history = self.get_conversation_context(conversation_id) if conversation_id else []
                filtered_response = self.validate_and_fix_response(cached_response, user_message, conversation_history)
                return filtered_response
            # 대화 컨텍스트 조회
            context = self.get_conversation_context(conversation_id) if conversation_id else None
            
            # 인사말 처리 (처음 인사인 경우에만)
            if self.is_greeting(user_message):
                return "네, 안녕하세요! 어떤 도움이 필요하신가요?"

            # 특정 투어명 또는 투어 유형 언급 감지
            specific_tour_mentioned = False
            mentioned_tour = None
            tour_type_mentioned = False

            # 투어 유형별 키워드 체크
            golf_keywords = ['골프', 'golf', '골프투어']
            rafting_keywords = ['래프팅', 'rafting', '래프팅투어']
            banahil_keywords = ['바나힐', 'banahil', '바나힐투어']
            family_keywords = ['패밀리', 'family', '패밀리팩', 'pack']

            user_message_lower = user_message.lower()

            if tours:
                # 1. 정확한 투어명 매칭
                for tour in tours:
                    tour_name_keywords = tour['tour_name'].lower().replace(' ', '').replace('-', '')
                    user_message_clean = user_message.lower().replace(' ', '').replace('-', '')
                    if tour_name_keywords in user_message_clean or any(keyword in tour_name_keywords for keyword in user_message_clean.split()):
                        specific_tour_mentioned = True
                        mentioned_tour = tour
                        break

                # 🚨 중요: 이전 대화 컨텍스트가 있으면 투어 타입 매칭을 하지 않음 (컨텍스트 유지)
                has_previous_context = (conversation_id and
                                      conversation_id in self.conversation_history and
                                      len(self.conversation_history[conversation_id]) > 0)

                # 2. 투어 유형별 매칭 (정확한 매칭이 없고 이전 컨텍스트도 없을 때만)
                if not specific_tour_mentioned and not has_previous_context:
                    try:
                        print(f"Checking golf keywords: {golf_keywords} in message: {user_message_lower}")
                    except UnicodeEncodeError:
                        print(f"Checking golf keywords in Korean message")

                    if any(keyword in user_message_lower for keyword in golf_keywords):
                        print(f"Golf keyword found! Searching in tours...")
                        for tour in tours:
                            try:
                                print(f"Checking tour: {tour['tour_name']}")
                            except UnicodeEncodeError:
                                print("Checking tour: [Korean tour name]")
                            if '골프' in tour['tour_name'].lower() or 'golf' in tour['tour_name'].lower():
                                tour_type_mentioned = True
                                specific_tour_mentioned = True
                                mentioned_tour = tour
                                try:
                                    print(f"Golf tour matched: {tour['tour_name']}")
                                except UnicodeEncodeError:
                                    print("Golf tour matched: [Korean tour name]")
                                break
                    elif any(keyword in user_message_lower for keyword in rafting_keywords):
                        for tour in tours:
                            if '래프팅' in tour['tour_name'].lower() or 'rafting' in tour['tour_name'].lower():
                                tour_type_mentioned = True
                                specific_tour_mentioned = True
                                mentioned_tour = tour
                                break
                    elif any(keyword in user_message_lower for keyword in family_keywords):
                        for tour in tours:
                            if '패밀리' in tour['tour_name'].lower() or 'family' in tour['tour_name'].lower():
                                tour_type_mentioned = True
                                specific_tour_mentioned = True
                                mentioned_tour = tour
                                try:
                                    print(f"Family tour matched: {tour['tour_name']}")
                                except UnicodeEncodeError:
                                    print("Family tour matched: [Korean tour name]")
                                break

            # 특정 투어 언급시 AI를 통해 정리된 설명 제공 (그대로 복붙 방지)
            if specific_tour_mentioned and mentioned_tour:
                # AI를 통해 투어 정보를 정리해서 설명하도록 함
                tours = [mentioned_tour]  # AI 프롬프트로 넘어가서 정리된 설명을 생성

            # 정보 요청 감지 - 바로 정보 보여주기
            info_request_keywords = ['내용', '정보', '자세한', '구체적인', '보여줘', '알려줘', '설명', '상세', '뭐에요', '뭐야', '무엇', '어떤', '구성', '포함', 'details', 'information']
            is_info_request = any(keyword in user_message.lower() for keyword in info_request_keywords)

            try:
                print(f"Info request check: {is_info_request}, hotels: {len(hotels) if hotels else 0}, tours: {len(tours) if tours else 0}")
                try:
                    print(f"Message: {user_message}, Keywords found: {[k for k in info_request_keywords if k in user_message.lower()]}")
                except UnicodeEncodeError:
                    print("Message: [Korean text], Keywords found: [list]")
            except UnicodeEncodeError:
                print(f"Info request check: {is_info_request}, hotels: {len(hotels) if hotels else 0}, tours: {len(tours) if tours else 0}")

            # 투어 유형별 필터링 처리
            if tour_type_mentioned and mentioned_tour:
                # 특정 투어 유형이 언급된 경우 해당 투어만 표시하고 AI로 넘김
                tours = [mentioned_tour]
                try:
                    print(f"Filtered to specific tour type: {mentioned_tour['tour_name']}")
                except UnicodeEncodeError:
                    print("Filtered to specific tour type: [Korean tour name]")

            # 🚨 중요: 이전 대화 컨텍스트가 있을 때는 투어 목록을 보여주지 않음 (컨텍스트 유지)
            has_conversation_context = (conversation_id and
                                      conversation_id in self.conversation_history and
                                      len(self.conversation_history[conversation_id]) > 0)

            # 특정 투어 유형이 언급되지 않은 일반적인 정보 요청인 경우에만 목록 표시 (컨텍스트가 없을 때만)
            if is_info_request and (hotels or tours) and not (specific_tour_mentioned or tour_type_mentioned) and not has_conversation_context:
                response_parts = []

                if tours:
                    response_parts.append("🎯 **투어 패키지:**")
                    for tour in tours:  # 모든 투어 표시
                        response_parts.append(f"• {tour['tour_name']}")
                    response_parts.append("")

                response_parts.append("어떤 패키지가 궁금하신가요?")
                return "\n".join(response_parts)
            
            # 컨텍스트 준비
            prompt_context = f"사용자 질문: {user_message}\n\n"
            
            # 대화 히스토리 추가 및 맥락 분석
            conversation_context = ""
            context_hint = ""
            if context and context.get('messages'):
                conversation_context = "이전 대화:\n"
                recent_messages = context['messages'][-3:]  # 최근 3개 대화만

                # 가장 최근 대화에서 투어 유형 파악
                last_tour_type = None
                for msg in reversed(recent_messages):
                    user_msg = msg.get('user', '').lower()
                    ai_msg = msg.get('ai', '').lower()

                    if '골프' in user_msg or 'golf' in user_msg or '골프' in ai_msg:
                        last_tour_type = '골프'
                        break
                    elif '래프팅' in user_msg or 'rafting' in user_msg or '래프팅' in ai_msg:
                        last_tour_type = '래프팅'
                        break
                    elif '패밀리' in user_msg or 'family' in user_msg or '패밀리' in ai_msg:
                        last_tour_type = '패밀리'
                        break
                    elif '라이트' in user_msg or 'light' in user_msg or '라이트' in ai_msg:
                        last_tour_type = '라이트'
                        break
                    elif '베스트' in user_msg or 'best' in user_msg or '베스트' in ai_msg:
                        last_tour_type = '베스트'
                        break

                # 맥락 힌트 및 생략된 정보 보완
                context_hint = ""
                if last_tour_type:
                    # 최근 대화에서 구체적인 투어명 추출
                    last_specific_tour = None
                    for msg in reversed(recent_messages):
                        user_msg = msg.get('user', '')
                        ai_msg = msg.get('ai', '')

                        # 구체적인 투어명 패턴 찾기
                        if last_tour_type == '골프':
                            if '골프투어54' in user_msg or '골프투어 54' in user_msg or '54홀' in user_msg or '54' in ai_msg:
                                last_specific_tour = '골프투어54홀'
                                break
                            elif '골프투어72' in user_msg or '골프투어 72' in user_msg or '72홀' in user_msg or '72' in ai_msg:
                                last_specific_tour = '골프투어72홀'
                                break
                        elif last_tour_type == '래프팅':
                            if '래프팅' in user_msg or '래프팅' in ai_msg:
                                last_specific_tour = '래프팅투어'
                                break
                        elif last_tour_type == '패밀리':
                            if '패밀리' in user_msg or '패밀리' in ai_msg:
                                last_specific_tour = '패밀리팩투어'
                                break

                    # 맥락 힌트 생성
                    if last_specific_tour:
                        context_hint = f"**중요: 고객이 계속 {last_specific_tour}에 대해 문의 중입니다. 현재 질문은 {last_specific_tour}에 관한 것으로 해석하고 답변하세요.**\n\n"
                    else:
                        context_hint = f"**중요: 고객이 계속 {last_tour_type} 투어에 대해 문의 중입니다. 다른 투어가 아닌 {last_tour_type} 투어 정보만 제공하세요.**\n\n"

                # 이전 대화를 강조하여 표시
                conversation_context += "**이전 대화 (반드시 참고하세요):**\n"
                for i, msg in enumerate(recent_messages):
                    conversation_context += f"{i+1}. 고객: {msg['user']}\n   상담사: {msg['ai']}\n\n"

                # 가장 최근 대화를 별도 강조
                if recent_messages:
                    last_msg = recent_messages[-1]
                    conversation_context += f"**직전 대화 (가장 중요):**\n고객: {last_msg['user']}\n상담사: {last_msg['ai']}\n\n"
            
            if hotels:
                prompt_context += "호텔 정보:\n"
                for hotel in hotels[:3]:  # 최대 3개만
                    prompt_context += self.format_hotel_info(hotel) + "\n"
            
            # 가격만 묻는 질문인지 확인
            is_price_only_question = any(keyword in user_message for keyword in ['가격', '얼마', '비용', '요금', '돈', '만원', '$'])

            if tours:
                prompt_context += "투어 정보:\n"
                for tour in tours:  # 모든 투어
                    prompt_context += self.format_tour_info(tour)
                    # 사용자 질문에 맞는 상세내용만 추출
                    if tour.get('description'):
                        relevant_description = self.extract_relevant_description(tour['description'], user_message)
                        if relevant_description:
                            prompt_context += f"📝 관련정보: {relevant_description}\n"
                    prompt_context += "\n"
            
            if not hotels and not tours:
                # 이전 대화 컨텍스트 확인
                has_previous_context = (conversation_id and
                                      conversation_id in self.conversation_history and
                                      len(self.conversation_history[conversation_id]) > 0)

                if not has_previous_context:
                    # 주어가 생략된 애매한 질문이면 명확화 요청
                    ambiguous_patterns = ['가격', '얼마', '비용', '요금', '아이', '성인', '호텔', '포함']
                    is_ambiguous = any(pattern in user_message for pattern in ambiguous_patterns)

                    if is_ambiguous:
                        return {
                            'response': "어떤 투어에 대해 문의하시는 건가요? 🤔\n\n현재 이용 가능한 투어:\n• 호이안 투어\n• 베스트팩 투어\n• 래프팅 투어\n• 패밀리팩 투어\n• 골프 투어\n\n구체적인 투어명을 말씀해 주시면 정확한 정보를 안내해드리겠습니다! 😊",
                            'tours_found': 0,
                            'hotels_found': 0
                        }

                # 검색 결과가 없을 때 이전 검색 결과 재사용 (연속 대화 지원)
                if hasattr(self, 'last_search_results') and self.last_search_results:
                    hotels = self.last_search_results.get('hotels', [])
                    tours = self.last_search_results.get('tours', [])
                    try:
                        print("No search results found, using previous search results for continuity")
                    except UnicodeEncodeError:
                        print("Using previous search results for continuity")

                # 여전히 결과가 없으면 기본 안내
                if not hotels and not tours:
                    available_regions = self.get_available_regions()
                    region_mentioned = any(region in user_message for region in available_regions)
                    tour_mentioned = any(keyword in user_message.lower() for keyword in ['투어', '관광', '체험', '액티비티', '투어가'])
                    hotel_mentioned = any(keyword in user_message.lower() for keyword in ['호텔', '숙박', '리조트', '펜션'])
                    general_travel = any(keyword in user_message.lower() for keyword in ['여행지', '여행', '어디'])

                    if general_travel and not region_mentioned:
                        if available_regions:
                            region_list = ", ".join(available_regions[:3])  # 최대 3개 지역만 표시
                            return f"저희는 {region_list} 여행 상품을 다루고 있습니다. 어느 지역에 관심 있으시나요?"
                        else:
                            return "죄송합니다. 현재 이용 가능한 여행 상품이 없습니다."
                    elif tour_mentioned and not region_mentioned:
                        if available_regions:
                            region_list = ", ".join(available_regions[:3])
                            return f"어느 지역 투어를 찾으시나요? ({region_list} 등)"
                        else:
                            return "어느 지역 투어를 찾으시나요?"
                    elif hotel_mentioned and not region_mentioned:
                        if available_regions:
                            region_list = ", ".join(available_regions[:3])
                            return f"어느 지역 호텔을 찾으시나요? ({region_list} 등)"
                        else:
                            return "어느 지역 호텔을 찾으시나요?"
                    elif region_mentioned and not tour_mentioned and not hotel_mentioned:
                        # 지역이 언급되면 해당 지역의 호텔과 투어 정보를 모두 제공
                        response_parts = []
                        if hotels:
                            response_parts.append("🏨 **호텔 정보:**")
                            for hotel in hotels[:2]:
                                response_parts.append(self.format_hotel_info(hotel))
                        if tours:
                            response_parts.append("🎯 **투어 정보:**")
                            for tour in tours[:2]:
                                response_parts.append(self.format_tour_info(tour))

                        if response_parts:
                            return "\n".join(response_parts) + "\n\n더 자세한 정보가 필요하시거나 예약을 원하시면 말씀해주세요!"
                        else:
                            return "숙소가 필요하신가요? 아니면 투어를 찾으시나요?"
                    else:
                        return "죄송합니다. 해당 검색 조건에 맞는 상품을 찾을 수 없습니다. 다른 지역이나 조건으로 검색해 보시겠어요?"
            
            # 복잡한 응답만 AI 호출
            tour_type_hint = ""
            if tour_type_mentioned:
                if any(keyword in user_message_lower for keyword in golf_keywords):
                    tour_type_hint = "고객이 골프 투어에 관심을 보이고 있습니다. 골프 투어 정보를 상세히 제공하세요."
                elif any(keyword in user_message_lower for keyword in rafting_keywords):
                    tour_type_hint = "고객이 래프팅 투어에 관심을 보이고 있습니다. 래프팅 투어 정보를 상세히 제공하세요."
                elif any(keyword in user_message_lower for keyword in family_keywords):
                    tour_type_hint = "고객이 패밀리팩 투어에 관심을 보이고 있습니다. 패밀리팩 구성과 내용을 상세히 설명하세요."

            # 현재 투어 종류가 명시적으로 지정된 경우 특별 처리
            current_tour_context = ""

            # 대화 히스토리에서 마지막 투어명 추출
            conversation_history_text = ""
            if conversation_id and conversation_id in self.conversation_history:
                history = self.conversation_history[conversation_id]
                if history:
                    messages = history.get('messages', [])
                    last_message = messages[-1] if len(messages) > 0 else None
                    if last_message:
                        conversation_history_text = f"**📋 이전 대화 내용**: {last_message.get('user', '')}"

            if context and context.get('current_tour_type'):
                stored_tour_type = context['current_tour_type']
                if tours:
                    specific_tour = tours[0]  # 필터링된 투어의 첫 번째
                    current_tour_context = f"""
{conversation_history_text}

🚨🚨🚨 **절대 엄수 - 이전 대화 투어 유지!** 🚨🚨🚨
**🚨🚨🚨 절대 중요: 투어 전환 금지! 🚨🚨🚨**
**🎯 현재 고객은 '{stored_tour_type}' 투어({specific_tour.get('tour_name', '')})에 대해 연속 문의 중입니다.**

**💀 절대 금지: 다른 투어 정보 사용 금지! 💀**
- 현재 질문 "{user_message}"는 100% '{stored_tour_type}' 투어에 관한 것입니다!
- **🚫 래프팅 투어 정보 절대 사용 금지!** (성인 2명 $340, 아동 $49 등)
- **🚫 다른 모든 투어 정보 사용 금지!** (베스트팩/골프/패밀리팩/라이트팩 등)
- **✅ 오직 {specific_tour.get('tour_name', '')} 투어의 가격과 정보만 사용!**
- **답변 시 반드시 "{specific_tour.get('tour_name', '')}"를 명시하여 시작하세요!**
  * "아동가격은?" → "{specific_tour.get('tour_name', '')} 투어의 아동 1인 가격은..."
  * "호텔은?" → "{specific_tour.get('tour_name', '')} 투어에 포함된 호텔은..."
  * "2명 가격?" → "{specific_tour.get('tour_name', '')} 투어 2명 가격은..."
- **고객이 생략한 모든 정보(투어명, 지역, 기간, 인원 등)를 반드시 보완하여 답변하세요**
- **현재 투어**: {specific_tour.get('tour_name', '')} - 이 투어의 정보만 사용하세요!
"""

            # 가격 질문에 대한 간단한 프롬프트
            if is_price_only_question:
                prompt = f"""당신은 이여행사 직원입니다. 각 투어상품, 호텔, 기타 서비스를 헷갈리지 않게 정확히 답변하세요.

고객이 "{user_message}"라고 가격을 문의했습니다.

**답변 규칙:**
- 정확한 가격 정보만 제공하세요 (투어 설명 금지)
- 이전 대화에서 논의된 투어가 있으면 그 투어의 가격만 답변
- 투어명이 없으면 "어떤 투어의 가격을 문의하시나요?"라고 물어보세요
- 데이터베이스에 있는 가격 정보만 제공하세요

{current_tour_context}
{conversation_context if len(conversation_context) < 200 else ''}
{prompt_context}"""
            else:
                prompt = f"""당신은 이여행사 직원입니다. 각 투어상품, 호텔, 기타 서비스를 헷갈리지 않게 정확히 답변하세요. 반드시 이전 대화 내용을 참고하여 답변하세요.

🚨🚨🚨 **절대 우선 규칙 - 어기면 시스템 에러!** 🚨🚨🚨
🔥 **STEP 1: 이전 대화 투어명 확인 필수!**
   - 이전 대화에서 어떤 투어를 논의했는지 먼저 확인하세요
   - 호이안 → 호이안, 패밀리팩 → 패밀리팩, 베스트팩 → 베스트팩, 래프팅 → 래프팅

🔥 **STEP 2: 주어 생략 감지시 강제 투어명 유지!**
   - "아이가격은?" = "아이 가격은 무엇입니까?" → 이전 대화 투어의 아이 가격!
   - "2명 추가하면?" = "2명 추가하면 어떻게 되나요?" → 이전 대화 투어에 2명 추가!
   - "호텔은?" = "호텔이 어디인가요?" → 이전 대화 투어의 호텔!

🚨🚨 **매우 중요: 계산 방식 절대 변경 금지!** 🚨🚨
   - 이전 "호이안 5명" → 아이 추가시에도 호이안 투어 유지!
   - ❌ **절대 금지**: "성인 2명 + 아동 2명"으로 재계산하지 말기! (5명인데 왜 2명?)
   - ❌ **절대 금지**: 래프팅 투어 가격($340, $49) 사용하지 말기!
   - ✅ **정답**: "호이안 5명" + "아이 2명 추가" = 호이안 총 7명 (5+2)
   - ✅ **정답**: 계속 호이안 투어 가격 구조 사용하기!

🔥 **STEP 3: 절대 투어 바꿈 금지!**
   - 호이안 이후 → 호이안만, 절대 래프팅/베스트팩/골프 언급 금지!
   - 패밀리팩 이후 → 패밀리팩만, 절대 다른 투어 언급 금지!
   - 베스트팩 이후 → 베스트팩만, 절대 다른 투어 언급 금지!

🚨 **절대 금지 - 이 규칙을 어기면 안 됩니다**:
- **정보 섞임 절대 금지**: 다른 투어/호텔의 정보를 절대 섞어서 말하지 마세요!
- **엄격한 데이터 격리**: 베스트팩을 묻는데 래프팅/라이트팩/골프 정보를 사용하면 안 됩니다!
- **오직 해당 투어의 정확한 정보만**: 다른 투어의 가격/내용/호텔 정보를 절대 섞지 마세요
- **확실하지 않으면 거부**: "정확한 정보는 확인 후 안내드리겠습니다"라고 답변하세요
- **데이터베이스에 없는 정보 추가 금지**: "1인 기준", "기본 패키지" 등 없는 표현 사용 절대 금지
- **예시**: 투어A를 물으면 → 투어A 데이터만 사용, 투어B/투어C 등 다른 투어 정보 절대 금지

현재 고객 질문: {user_message}
{current_tour_context}

**핵심 규칙:**
1) **엄격한 데이터 격리 - 가장 중요**: 다른 투어/호텔의 정보를 절대 섞지 마세요!
   - 투어A를 묻는데 → 투어A 데이터만 사용 (투어B/투어C/투어D 데이터 금지)
   - 투어B를 묻는데 → 투어B 데이터만 사용 (투어A/투어C/투어D 데이터 금지)
2) **반드시 이전 대화를 먼저 확인하세요** - 고객이 방금 전에 어떤 투어에 대해 물어봤는지 파악
3) **🔥 주제 고정 - 절대 바꾸지 마세요!**
   - 방금 전 대화: 패밀리팩 → 다음 질문도 패밀리팩 유지
   - 방금 전 대화: 베스트팩 → 다음 질문도 베스트팩 유지
   - 방금 전 대화: 래프팅 → 다음 질문도 래프팅 유지
4) **🔥 생략된 주어 복원 - 반드시 이전 대화 투어명 사용!**
   - "아이가격은?" → "**[바로 직전 대화의 투어명]** 아동 가격은..."
   - "2명 추가하면?" → "**[바로 직전 대화의 투어명]**에 2명 추가하면..."
   - "호텔은?" → "**[바로 직전 대화의 투어명]** 호텔은..."
   - **⚠️ 절대 다른 투어로 바뀌면 안 됩니다! 바로 직전 대화의 투어를 계속 사용하세요!**
   - **🚨 이전 대화가 없거나 불분명하면**: "어떤 투어에 대해 문의하시는 건가요? (호이안/베스트팩/래프팅/패밀리팩 등 중에서)"
5) **한 번에 하나의 투어만 답변하세요** - 여러 투어를 나열하지 말고 이전 대화 맥락의 투어만
6) **확실하지 않으면 "확인 후 안내"**: 다른 투어 정보가 섞일 위험이 있으면 답변 거부
7) **가격 계산은 정확히**: 성인 가격표에서 인원수에 맞는 가격 + (아동 1인 가격 × 아동 수)
8) **데이터베이스 정보만 사용하세요** - 없는 정보는 절대 추가하지 마세요
   - "1인 기준", "기본 패키지" 등 데이터베이스에 없는 표현 사용 금지
   - 추측하거나 일반적인 설명을 추가하지 마세요
   - 오직 제공된 데이터베이스 정보만 정확히 전달하세요
9) **정확히 물어본 것만 답변하세요**:
   - "아이3명"만 물어보면 → 아이3명 가격만 답변 (성인 가격 추가 금지)
   - "성인2명"만 물어보면 → 성인2명 가격만 답변 (아이 가격 추가 금지)
   - 가격만 물어보면 → 가격만 답변 (묻지 않은 투어 상세 내용 설명 금지)
   - 묻지 않은 정보는 절대 추가하지 마세요
10) **완전한 맥락 보완 필수**: 투어명을 반드시 명시하여 정보 혼동 방지

**가격 계산 방법 (매우 중요):**
- 성인 가격표에서 성인 인원수에 맞는 가격 찾기
- 아동은 별도 계산 (아동 1인 기준 × 아동 수)
- 성인과 아동을 합쳐서 계산하지 말 것
- 예: 성인 2명 + 아동 2명 = 성인 2인 가격 + (아동 1인 가격 × 2)

5) 가격 계산 시 데이터베이스의 정확한 가격만 사용하세요
6) 고객이 투어 구성이나 내용을 물을 때는 상세 설명을 제공하세요
7) 데이터베이스에 없는 정보는 절대 추가하지 마세요

🚨🚨🚨 **마지막 체크 - 답변하기 전 반드시 확인!** 🚨🚨🚨
**현재 질문 분석**: "{user_message}"
1️⃣ 이 질문에 투어명이 명시되어 있는가? → YES: 해당 투어 답변 / NO: 아래로
2️⃣ 투어명이 없으면 이전 대화에서 어떤 투어를 논의했는가? → 그 투어 계속 사용!
3️⃣ **이전 대화도 없거나 애매하면 명확화 요청!**
   → "어떤 투어에 대해 문의하시는 건가요? (호이안/베스트팩/래프팅/패밀리팩 등)"
4️⃣ 절대 다른 투어를 언급하지 마세요! (여러 투어 예시도 금지!)
5️⃣ 답변 시작을 "[투어명] 투어의..."로 시작하세요!

{conversation_context if len(conversation_context) < 500 else ''}
{prompt_context}"""
                
            # 프롬프트 디버그 출력
            try:
                print(f"=== PROMPT DEBUG ===")
                print(f"User message: {user_message}")
                print(f"Tours found: {len(tours) if tours else 0}")
                if tours:
                    print(f"Tour names: {[tour.get('tour_name', 'Unknown') for tour in tours]}")
                print(f"Prompt length: {len(prompt)}")
                print(f"Prompt preview: {prompt[:500]}...")
                print(f"=== END DEBUG ===")
            except:
                print("Debug info (Korean text)")

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 이여행사 직원입니다. 다음 규칙을 절대 지켜주세요:\n\n1. 제공된 데이터베이스 정보만 사용하세요\n2. 예약금, 잔금, 결제방법 등 데이터베이스에 없는 정보는 절대 추가하지 마세요\n3. 가격 문의 시 예약금과 현장결제를 모두 포함한 완전한 결제 정보를 제공하세요\n4. 확실하지 않은 정보는 '확인 후 안내드리겠습니다'라고 답변하세요\n5. 각 투어상품, 호텔 정보를 정확히 구분해서 답변하세요"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            response_text = response.choices[0].message.content.strip()
            try:
                print(f"AI Response generated: {response_text[:100]}...")
            except UnicodeEncodeError:
                print("AI Response generated: [Korean response text]")
            
            # 응답 캐시 저장 (24시간)
            import time
            self.response_cache[cache_key] = response_text
            
            # 캐시 크기 제한 (최대 100개)
            if len(self.response_cache) > 100:
                # 가장 오래된 캐시 20개 삭제
                old_keys = list(self.response_cache.keys())[:20]
                for key in old_keys:
                    del self.response_cache[key]
            
            return response_text
            
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            print(f"OpenAI API Error: {error_type}: {error_str}")
            print(f"Full error details: {repr(e)}")
            import traceback
            traceback.print_exc()
            if tours:
                print(f"Available tours: {[t.get('tour_name', 'Unknown') for t in tours]}")

            # 특정 오류에 따른 대응
            if "429" in error_str or "quota" in error_str.lower():
                # API 할당량 초과 시 간단한 응답
                if hotels:
                    hotel_names = [h['hotel_name'] for h in hotels[:2]]
                    return f"다낭에 {', '.join(hotel_names)} 등의 호텔이 있습니다. 자세한 정보는 잠시 후 다시 문의해 주세요."
                elif tours:
                    tour_names = [t['tour_name'] for t in tours[:2]]
                    return f"다낭에 {', '.join(tour_names)} 등의 투어가 있습니다. 자세한 정보는 잠시 후 다시 문의해 주세요."
                else:
                    return "죄송합니다. 현재 서비스 이용량이 많아 잠시 후 다시 시도해 주세요."
            elif "-1" in error_str or "invalid" in error_str.lower():
                # -1 오류나 invalid request 시 간단한 답변 시도
                if tours and ('가격' in user_message or '얼마' in user_message):
                    tour = tours[0]
                    tour_name = tour.get('tour_name', '')
                    if '어린이' in user_message or '아동' in user_message:
                        return f"{tour_name} 아동 가격은 확인 후 안내드리겠습니다."
                    else:
                        return f"{tour_name} 투어 가격 정보가 준비되어 있습니다. 구체적인 인원을 말씀해 주시면 정확한 가격을 안내해드리겠습니다."
                return "죄송합니다. 좀 더 구체적으로 질문해 주시거나, 잠시 후 다시 시도해 주세요."
            return f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}"

    def validate_and_fix_response(self, response, user_message="", conversation_history=None, conversation_id=None):
        """응답 내용 검증 및 잘못된 표현 수정"""
        # 금지된 표현들 (더 포괄적으로)
        forbidden_phrases = [
            '1인 기준', '성인 1인 기준', '기본 패키지', '포함 사항', '일반적으로',
            '보통', '대체로', '추정', '예상', '대략', '기준으로', '기준:',
            '1인당', '인당', '개인당', '1명당', '명당'
        ]

        # 투어별 잘못된 가격 정보 감지 (다른 투어 가격 혼용 방지)
        price_confusion_patterns = [
            # 더 이상 하드코딩된 가격 패턴 사용하지 않음 - 컨텍스트 기반 검증으로 대체
        ]

        original_response = response

        # 사용자 질문 분석 - 정확히 물어본 것만 답변하도록 필터링
        if user_message:
            # 아이/아동만 물어봤는데 성인 정보가 포함된 경우
            child_only_keywords = ['아이', '아동', '애기', '애', '유아', '소아']
            adult_keywords = ['성인', '어른', '성인 3명', '성인3명']

            user_msg_lower = user_message.lower()
            has_child_keyword = any(keyword in user_msg_lower for keyword in child_only_keywords)
            has_no_adult_keyword = not any(keyword in user_msg_lower for keyword in adult_keywords)

            # "아이3명"만 물어봤는데 성인 정보가 포함되어 있으면 제거
            if has_child_keyword and has_no_adult_keyword:
                adult_patterns_to_remove = [
                    '성인 3명:', '성인3명:', '성인 \\d+명:',
                    '예약금 18만원', '18만원', '$1,092', '$1,587',
                    '총합은:', '총 가격은', '를 포함한 총'
                ]

                import re
                for pattern in adult_patterns_to_remove:
                    # 해당 패턴이 포함된 문장 전체를 제거
                    lines = response.split('\n')
                    filtered_lines = []

                    for line in lines:
                        if not re.search(pattern, line):
                            filtered_lines.append(line)
                        else:
                            try:
                                print(f"Warning: Removing adult info from child-only question: {pattern}")
                            except UnicodeEncodeError:
                                print("Warning: Removing adult info from child-only question")

                    response = '\n'.join(filtered_lines)

                # 성인 관련 문장 제거
                response = re.sub(r'[^\n]*성인[^\n]*\n?', '', response)
                response = re.sub(r'[^\n]*총합[^\n]*\n?', '', response)
                response = re.sub(r'[^\n]*총 가격[^\n]*\n?', '', response)

        # 래프팅 가격 오염 감지 및 차단 (에러 처리 추가)
        try:
            has_previous_context = conversation_history and len(conversation_history) > 0

            if has_previous_context:
                # 이전 대화에서 호이안이 언급되었는지 확인 (강화된 로직)
                previous_messages = ' '.join([
                    msg.get('content', '') if isinstance(msg, dict) else str(msg)
                    for msg in conversation_history
                ])

                # 전체 맥락을 고려한 투어 컨텍스트 감지 (특정 이름이 아닌 전체 맥락)
                current_tour_type = None
                if conversation_id and conversation_id in self.conversation_history:
                    context_data = self.conversation_history[conversation_id]
                    current_tour_type = context_data.get('current_tour_type', '')

                # 컨텍스트 기반 오염 방지: 현재 투어 타입과 다른 가격 정보 감지
                is_non_rafting_context = current_tour_type and current_tour_type != 'rafting'

                # 호이안 투어 컨텍스트에서만 래프팅 가격 오염 차단
                is_hoi_an_context = current_tour_type == 'hoi_an'

                # 현재 응답에 래프팅 가격이 포함되어 있는지 확인
                has_rafting_contamination = (
                    '$340' in response or '340달러' in response or
                    '$49' in response or '49달러' in response or
                    ('$438' in response and '$340' in response)  # 래프팅 계산 결과
                )

                if is_hoi_an_context and has_rafting_contamination:
                    print("CRITICAL: Detected rafting price contamination in Hoi An context!")
                    print(f"Previous context: Hoi An, Current response contains rafting prices")
                    # 래프팅 가격 정보가 포함된 문장들을 제거
                    lines = response.split('\n')
                    filtered_lines = []
                    for line in lines:
                        if not any(price in line for price in ['$340', '$49', '$438', '340달러', '49달러']):
                            filtered_lines.append(line)
                        else:
                            print(f"Removing contaminated line (length: {len(line)})")

                    response = '\n'.join(filtered_lines).strip()

                    if not response.strip():
                        response = "죄송합니다. 호이안 투어 관련 정확한 정보를 다시 확인하여 안내해드리겠습니다."

        except Exception as contamination_error:
            print(f"Error in contamination detection: {contamination_error}")
            # 오염 감지에서 오류가 발생하면 원본 응답을 그대로 사용

        # 질문 컨텍스트 확인 - 비슷한 단어와 동의어까지 포함
        user_msg_lower = user_message.lower()

        # 어린이 관련 동의어들
        children_keywords = ['아이', '아동', '애기', '어린이', '소아', '유아', '애들', '꼬마', '꼬마들', '애', '어린애', '작은애', '꼬맹이', '애기들']
        is_children_question = any(keyword in user_msg_lower for keyword in children_keywords)

        # 성인 관련 동의어들
        adult_keywords = ['성인', '어른', '어른들', '어른분', '성인분', '성년', '대인', '어른분들', '성인들']
        is_adult_question = any(keyword in user_msg_lower for keyword in adult_keywords)

        # 인원수 관련 표현들 (숫자 + 단위)
        people_patterns = [
            # 기본 명수
            *[str(i) + '명' for i in range(1, 21)],
            # 한글 숫자
            '한명', '두명', '세명', '네명', '다섯명', '여섯명', '일곱명', '여덟명', '아홉명', '열명',
            # 기타 표현
            '몇명', '몇 명', '몇분', '몇 분', '인원', '사람', '명수', '1인', '2인', '3인', '4인', '5인'
        ]
        is_people_count_question = any(pattern in user_msg_lower for pattern in people_patterns)

        # 가격 관련 동의어들
        price_keywords = [
            '얼마', '가격', '비용', '요금', '돈', '값', '금액', '경비', '료금', '비',
            '추가', '더하면', '플러스', '더해서', '포함해서', '합치면', '총', '전체',
            '얼만', '얼마나', '얼마정도', '얼마쯤', '가격이', '비용이', '요금이',
            '계산', '정산', '지불', '결제', '페이', '지불해야', '내야'
        ]
        is_price_question = any(keyword in user_msg_lower for keyword in price_keywords)

        # 금지된 표현 제거 (모든 가격 질문에서는 완화 - 어린이, 성인, 인원수 관련)
        for phrase in forbidden_phrases:
            if phrase in response:
                # 가격 관련 질문에서는 일부 금지 표현 허용 (모든 투어/호텔/표에 적용)
                if is_price_question and (is_children_question or is_adult_question or is_people_count_question):
                    # 가격 질문에서 허용되는 표현들
                    price_allowed_phrases = [
                        '1인당', '인당', '개인당', '1명당', '명당',  # 인원 관련
                        '기본 패키지', '일반적으로', '보통', '대체로',  # 설명 표현
                        '추정', '예상', '대략', '기준으로', '기준:'  # 가격 설명
                    ]
                    if phrase in price_allowed_phrases:
                        continue  # 이 표현들은 제거하지 않음

                try:
                    print(f"Warning: Removing forbidden phrase '{phrase}' from response")
                except UnicodeEncodeError:
                    print("Warning: Removing forbidden phrase from response")

                # 직접적으로 금지된 표현을 제거
                response = response.replace(phrase, '').strip()

                # 연속된 공백이나 구두점 정리
                response = response.replace('  ', ' ').replace(' :', ':').replace(' -', ' ')
                response = response.replace('- ', '').replace(': ', ' ')

                # 문장 시작 부분의 잘못된 구두점 제거
                while response.startswith((':', '-', ' ', ',')):
                    response = response[1:].strip()

        # 자동 줄바꿈 처리 - 번호가 있는 리스트나 정렬된 정보
        import re

        # 1. 숫자 + 점 + 공백 패턴 (1. 2. 3.)
        response = re.sub(r'(\d+\.\s)', r'\n\1', response)

        # 2. 숫자 + 괄호 + 공백 패턴 (1) 2) 3))
        response = re.sub(r'(\d+\)\s)', r'\n\1', response)

        # 3. **내용**: 패턴 (볼드체로 구분된 항목들)
        response = re.sub(r'(\*\*[^*]+\*\*:)', r'\n\1', response)

        # 4. - 항목들 (대시로 시작하는 리스트)
        response = re.sub(r'(\s-\s)', r'\n- ', response)

        # 5. 첫 줄 빈줄 제거 및 연속 줄바꿈 정리
        response = response.strip()
        response = re.sub(r'\n\n+', '\n\n', response)  # 3개 이상 연속 줄바꿈을 2개로
        response = re.sub(r'^\n', '', response)  # 맨 앞 줄바꿈 제거

        # 빈 문장 정리
        response = response.replace('..', '.').replace('  ', ' ').strip()

        if response != original_response:
            try:
                print("Response was modified to remove forbidden content")
            except UnicodeEncodeError:
                print("Response was modified")

        return response

    def process_message(self, user_message, conversation_id=None):
        """메시지 처리 메인 함수"""
        try:
            try:
                print(f"Processing message: {user_message} (conversation: {conversation_id})")
            except UnicodeEncodeError:
                print(f"Processing message: [Korean text] (conversation: {conversation_id})")
        except UnicodeEncodeError:
            print(f"Processing message: [Korean text] (conversation: {conversation_id})")
        
        # 1. 키워드 추출
        keywords = self.extract_keywords(user_message)
        # print(f"Extracted keywords: {keywords}")
        
        # 2. 의도 파악
        intent = self.determine_intent(user_message)
        print(f"Determined intent: {intent}")
        try:
            print(f"Keywords: {keywords}")
        except UnicodeEncodeError:
            print("Keywords: [Korean keywords]")

        # 3. 데이터베이스 검색
        hotels, tours = self.search_database(keywords, intent, conversation_id)
        print(f"Found hotels: {len(hotels)}, tours: {len(tours)}")
        
        # 4. AI 응답 생성
        response = self.generate_response(user_message, hotels, tours, conversation_id)

        # 응답이 dict 형태인 경우 (명확화 요청) 바로 반환
        if isinstance(response, dict):
            return response

        # 5. 대화 컨텍스트 업데이트
        if conversation_id:
            self.update_conversation_context(conversation_id, user_message, response, hotels, tours)

        # 6. 응답 내용 검증 및 수정
        conversation_history = self.get_conversation_context(conversation_id) if conversation_id else []
        original_response = response
        response = self.validate_and_fix_response(response, user_message, conversation_history, conversation_id)

        # 응답이 필터링으로 인해 너무 짧아졌거나 무효해진 경우 상세 오류 정보 및 안내 제공
        if not response or len(response.strip()) < 10:
            # 사용자 질문 분석하여 맞춤형 안내 제공
            tour_keywords = ['베스트팩', 'bestpack', '호이안', '다낭', '나트랑', '푸꾸옥', '사파', '하롱베이', '칸토', '메콩', '래프팅']
            hotel_keywords = ['호텔', '숙소', '리조트', '펜션']

            detected_tour = None
            detected_service = None

            for keyword in tour_keywords:
                if keyword in user_message.lower():
                    detected_tour = keyword
                    break

            for keyword in hotel_keywords:
                if keyword in user_message.lower():
                    detected_service = '숙박'
                    break

            if not detected_service:
                detected_service = '투어'

            # 구체적인 안내 메시지 생성
            helpful_guidance = []

            if is_children_question:
                helpful_guidance.extend([
                    f"어린이 관련 질문을 더 명확히 해주세요:",
                    f"• 어린이 연령을 구체적으로 알려주세요 (예: 5세, 10세)",
                    f"• 어린이 몇 명인지 정확한 숫자를 알려주세요",
                    f"• 성인과 함께 가는지 알려주세요 (예: 성인 2명 + 어린이 1명)"
                ])

            if detected_tour:
                helpful_guidance.extend([
                    f"'{detected_tour}' {detected_service} 문의를 더 구체적으로 해주세요:",
                    f"• 몇 명이 참가하는지 알려주세요 (예: 성인 2명)",
                    f"• 언제 예약하고 싶은지 알려주세요 (예: 12월 15일)",
                    f"• 특별한 요청사항이 있다면 알려주세요"
                ])
            else:
                helpful_guidance.extend([
                    f"질문을 더 구체적으로 해주세요:",
                    f"• 어떤 {detected_service}에 대해 알고 싶으신지 정확한 이름을 알려주세요",
                    f"• 참가 인원수를 알려주세요",
                    f"• 원하는 날짜나 기간을 알려주세요"
                ])

            if is_price_question:
                helpful_guidance.append(f"• 정확한 가격 안내를 위해 참가 인원과 날짜가 필요합니다")

            guidance_text = "\n".join(helpful_guidance)

            return {
                'response': f"죄송합니다. 더 정확한 답변을 위해 추가 정보가 필요합니다.\n\n{guidance_text}\n\n이렇게 질문해 주시면 정확한 정보를 안내해드릴 수 있습니다!",
                'intent': intent,
                'keywords': keywords,
                'hotels_found': len(hotels),
                'tours_found': len(tours),
                'error_type': 'need_more_info',
                'guidance_provided': helpful_guidance
            }

        # 7. 자가 검증 수행
        search_results = {'hotels': hotels, 'tours': tours}
        validation_result = self.perform_self_validation(
            user_message, conversation_id, intent, keywords, search_results, response
        )

        return {
            'response': response,
            'intent': intent,
            'keywords': keywords,
            'hotels_found': len(hotels),
            'tours_found': len(tours),
            'validation': validation_result
        }