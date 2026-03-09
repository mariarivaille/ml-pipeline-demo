import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from llama_cpp import Llama

# Пути и настройки
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/qwen2.5-0.5b-instruct-q5_k_m.gguf")
llm = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Загрузка модели один раз при старте приложения"""
    global llm
    print("🔄 Инициализация приложения...")
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"❌ Модель не найдена: {MODEL_PATH}. "
            "Убедитесь, что файл модели существует в контейнере."
        )
    
    print(f"🧠 Загрузка модели: {MODEL_PATH}")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=4,
        verbose=False
    )
    print("✅ Модель загружена в память")
    
    yield
    
    print("👋 Приложение остановлено")

app = FastAPI(lifespan=lifespan, title="Qwen 2.5 Chatbot")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": llm is not None}

@app.post("/api/chat")
async def chat(message: str = Form(...)):
    if not message.strip():
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    if llm is None:
        raise HTTPException(status_code=503, detail="Модель ещё не загружена")
    
    messages = [
        {"role": "system", "content": "Ты полезный ассистент."},
        {"role": "user", "content": message}
    ]
    
    output = llm.create_chat_completion(
        messages=messages,
        max_tokens=512,
        temperature=0.7,
        stop=["