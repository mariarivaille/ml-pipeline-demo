import asyncio
from typing import AsyncGenerator, Optional
from llama_cpp import Llama
from app.config import settings
from app.schemas import ChatRequest
from app.services.base import BaseModelService
from app.utils.logger import logger

class LlamaCppService(BaseModelService):
    """Сервис для работы с моделью через llama-cpp-python"""
    
    _instance: Optional['LlamaCppService'] = None
    
    def __new__(cls):
        """Singleton: загружаем модель только один раз"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Загрузка модели при старте сервиса"""
        logger.info(f"Loading model from {settings.MODEL_PATH}...")
        
        self.llm = Llama(
            model_path=settings.MODEL_PATH,
            n_ctx=settings.MAX_TOKENS * 2,  # Контекст: вход + выход
            n_threads=4,  # Количество потоков процессора
            n_gpu_layers=0,  # 0 = только CPU
            verbose=False,
            chat_format="chatml"  # Формат промптов для Qwen
        )
        logger.info("Model loaded successfully!")
    
    def _format_messages(self, messages: list) -> list:
        """Преобразует сообщения в формат ChatML для Qwen"""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return formatted
    
    async def generate(self, request: ChatRequest) -> str:
        """Синхронная генерация ответа"""
        try:
            # Блокирующий вызов модели — запускаем в thread pool
            loop = asyncio.get_event_loop()
            
            messages = self._format_messages([m.model_dump() for m in request.messages])
            
            response = await loop.run_in_executor(
                None,
                lambda: self.llm.create_chat_completion(
                    messages=messages,
                    max_tokens=request.max_tokens or settings.MAX_TOKENS,
                    temperature=request.temperature or settings.TEMPERATURE,
                    top_p=settings.TOP_P,
                    stream=False
                )
            )
            
            return response["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise Exception(f"Model service error: {str(e)}")
    
    async def generate_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Потоковая генерация ответа"""
        try:
            messages = self._format_messages([m.model_dump() for m in request.messages])
            
            # Стриминг через итератор
            stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=request.max_tokens or settings.MAX_TOKENS,
                temperature=request.temperature or settings.TEMPERATURE,
                top_p=settings.TOP_P,
                stream=True
            )
            
            for chunk in stream:
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta
                    
        except Exception as e:
            logger.error(f"Stream error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка, что модель загружена"""
        return hasattr(self, 'llm') and self.llm is not None
    
    async def close(self):
        """Очистка ресурсов (опционально)"""
        pass