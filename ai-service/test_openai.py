import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print(f"API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 확실히 작동하는 모델로 테스트
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, say hi back"}
        ],
        max_tokens=50
    )

    print("OpenAI API 연결 성공!")
    print("응답:", response.choices[0].message.content)

except Exception as e:
    print(f"OpenAI API 오류: {e}")