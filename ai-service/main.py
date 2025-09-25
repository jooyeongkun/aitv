from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from ai_service import TravelAI
import uvicorn

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI 서비스 인스턴스
travel_ai = TravelAI()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    keywords: List[str]
    hotels_found: int
    tours_found: int

@app.get("/")
def read_root():
    return {"message": "Travel AI Service is running"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        # UTF-8 디코딩 확인
        message = request.message
        try:
            print(f"Raw message received: {repr(message)}")
        except UnicodeEncodeError:
            print("Raw message received: [Korean text]")
        
        # 한글 인코딩 문제 해결 시도
        try:
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            elif '??' in message or len(message.encode('utf-8')) != len(message.encode('cp949', errors='ignore')):
                # 인코딩이 깨진 경우 복구 시도
                message = message.encode('latin1').decode('utf-8')
        except:
            pass
        
        try:
            print(f"Processed message: {message}")
        except UnicodeEncodeError:
            print("Processed message: [Korean text]")
        result = travel_ai.process_message(message, request.conversation_id)
        return ChatResponse(
            response=result['response'],
            intent=result['intent'],
            keywords=result['keywords'],
            hotels_found=result['hotels_found'],
            tours_found=result['tours_found']
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5002))
    uvicorn.run(app, host="0.0.0.0", port=port)