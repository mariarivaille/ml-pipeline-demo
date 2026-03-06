from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import time
import json

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, HealthResponse
from app.utils.logger import logger, setup_logger
from app.services.llama_service import LlamaCppService
from app.services.demo_service import DemoService

# Глобальная переменная для сервиса
model_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и очистка ресурсов при старте/остановке"""
    global model_service
    
    logger.info(f"Starting application in DEMO_MODE={settings.DEMO_MODE}")
    
    if settings.DEMO_MODE:
        model_service = DemoService()
        logger.info("Demo service initialized")
    else:
        model_service = LlamaCppService()
        logger.info("Llama.cpp service initialized")
    
    yield
    
    # Очистка при остановке
    if model_service:
        await model_service.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS для доступа из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "LLM ChatBot API is running",
        "docs": "/docs",
        "demo_mode": settings.DEMO_MODE
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка работоспособности сервиса"""
    is_healthy = await model_service.health_check() if not settings.DEMO_MODE else True
    
    return HealthResponse(
        status="ok" if is_healthy else "degraded",
        model=settings.MODEL_NAME,
        demo_mode=settings.DEMO_MODE,
        version=settings.API_VERSION
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Обычный (не потоковый) чат"""
    start_time = time.time()
    
    try:
        response_text = await model_service.generate(request)
        latency_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Chat request completed in {latency_ms:.2f}ms")
        
        return ChatResponse(
            response=response_text,
            model=settings.MODEL_NAME,
            demo_mode=settings.DEMO_MODE,
            usage={
                "prompt_tokens": len(str(request.messages)),
                "completion_tokens": len(response_text),
                "latency_ms": int(latency_ms)
            }
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Потоковый чат (текст появляется по мере генерации)"""
    try:
        async def generate_stream():
            async for chunk in model_service.generate_stream(request):
                # Формат SSE (Server-Sent Events)
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )