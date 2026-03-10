import os
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from gigachat import GigaChat  # ← Импортируем официальную библиотеку
from gigachat.exceptions import (
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    ServerError,
)
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GigaChat Bot API")
templates = Jinja2Templates(directory="app/templates")

# Конфигурация — теперь достаточно только ключа
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_API_URL = os.getenv("GIGACHAT_API_URL")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL")

if not GIGACHAT_CREDENTIALS:
    logger.warning("GIGACHAT_CREDENTIALS не найден в переменных окружения!")
if not GIGACHAT_API_URL:
    logger.warning("GIGACHAT_API_URL не найден в переменных окружения!")
if not GIGACHAT_MODEL:
    logger.warning("GIGACHAT_MODEL не найден в переменных окружения!")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.1


class ChatResponse(BaseModel):
    response: str


@app.get("/", response_class=HTMLResponse)
async def get_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_gigachat(chat_request: ChatRequest):
    if not GIGACHAT_CREDENTIALS:
        raise HTTPException(status_code=500, detail="API Key не настроен")

    try:
        async with GigaChat(
            base_url=GIGACHAT_API_URL,
            credentials=GIGACHAT_CREDENTIALS,
            access_token=GIGACHAT_CREDENTIALS,
            model=GIGACHAT_MODEL,
            verify_ssl_certs=False,
            timeout=300,
            profanity_check=False,
            scope="GIGACHAT_API_CORP"
        ) as client:
            response = await client.achat(  # ← асинхронный метод
                messages=[msg.dict() for msg in chat_request.messages],
                temperature=chat_request.temperature,
                top_p=chat_request.top_p,
            )
            
            if response.choices:
                return ChatResponse(response=response.choices[0].message.content)
            raise HTTPException(status_code=502, detail="Пустой ответ от GigaChat")

    except (AuthenticationError, RateLimitError, BadRequestError, ServerError) as e:
        logger.error(f"GigaChat error: {type(e).__name__} - {e}")
        status_map = {
            AuthenticationError: 401,
            RateLimitError: 429,
            BadRequestError: 400,
            ServerError: 502,
        }
        raise HTTPException(
            status_code=status_map.get(type(e), 500),
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/health")
async def health_check():
    return {"status": "ok"}