import re

with open('ai_service_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add greeting detection method
greeting_method = '''
    def is_greeting(self, user_message):
        """인사말 체크"""
        greetings = ['안녕하세요', '안녕', 'hi', 'hello', '헬로', '하이']
        return any(greeting in user_message.lower().strip() for greeting in greetings)
    '''

# Insert after __init__ method
content = content.replace('def extract_keywords(self, user_message):', 
                         greeting_method + '\n    def extract_keywords(self, user_message):')

# Update generate_response method
old_generate = '''def generate_response(self, user_message, hotels, tours):
        """AI 응답 생성"""
        try:
            # 컨텍스트 준비
            context = f"사용자 질문: {user_message}\n\n"'''

new_generate = '''def generate_response(self, user_message, hotels, tours):
        """AI 응답 생성"""
        try:
            # 인사말 처리
            if self.is_greeting(user_message):
                return "안녕하세요! 😊 여행 상담사입니다. 무엇을 도와드릴까요? 찾으시는 호텔 정보나 투어가 있으신가요?"
            
            # 컨텍스트 준비
            context = f"사용자 질문: {user_message}\n\n"'''

content = content.replace(old_generate, new_generate)

# Update API call to use Gemini
old_api = '''# OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """당신은 여행 상담 전문가입니다. 주어진 호텔/투어 데이터를 바탕으로 고객의 질문에 답변하세요.

규칙:
1. 오직 제공된 데이터베이스 정보만 사용하세요
2. 무조건적인 추천은 하지 마세요
3. 고객의 질문 의도를 파악하고 관련 정보만 제공하세요
4. 정확한 가격과 정보를 제공하세요
5. 친근하고 전문적인 톤을 사용하세요
6. 데이터에 없는 내용은 "해당 정보를 확인할 수 없습니다"라고 안내하세요"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()'''

new_api = '''# Google Gemini API 호출
            prompt = f"""당신은 친근한 여행 상담 전문가입니다. 주어진 호텔/투어 데이터를 바탕으로 고객의 질문에 답변하세요.

규칙:
1. 오직 제공된 데이터베이스 정보만 사용하세요
2. 친근하고 따뜻한 톤으로 응답하세요
3. 정확한 가격과 정보를 제공하세요
4. 이모지를 적절히 사용하여 친근함을 표현하세요

{context}"""

            response = self.model.generate_content(prompt)
            return response.text.strip()'''

content = content.replace(old_api, new_api)

with open('ai_service_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)
