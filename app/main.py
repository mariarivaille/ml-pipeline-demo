import os
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GigaChat Bot API")

# Подключение шаблонов
templates = Jinja2Templates(directory="app/templates")

# Конфигурация GigaChat
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
GIGACHAT_URL = "https://gigachat.devices.sberbank.ru/api/v2/chat/completions"
MODEL_NAME = "GigaChat"

if not GIGACHAT_API_KEY:
    logger.warning("GIGACHAT_API_KEY не найден в переменных окружения!")


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
    """Отдаёт главную страницу с интерфейсом чата."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_gigachat(chat_request: ChatRequest):
    """API эндпоинт для общения с GigaChat."""
    if not GIGACHAT_API_KEY:
        raise HTTPException(status_code=500, detail="API Key не настроен на сервере")

    headers = {
        "Authorization": f"Bearer {GIGACHAT_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [msg.dict() for msg in chat_request.messages],
        "temperature": chat_request.temperature,
        "top_p": chat_request.top_p,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GIGACHAT_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                bot_message = data["choices"][0]["message"]["content"]
                return ChatResponse(response=bot_message)
            else:
                raise HTTPException(status_code=502, detail="Некорректный ответ от GigaChat API")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Ошибка при запросе к GigaChat")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья сервиса."""
    return {"status": "ok"}