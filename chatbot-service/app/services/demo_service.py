import asyncio
import random
from typing import AsyncGenerator
from app.config import settings
from app.schemas import ChatRequest
from app.services.base import BaseModelService
from app.utils.logger import logger

class DemoService(BaseModelService):
    """Сервис-заглушка для демонстрации без реальной модели"""
    
    DEMO_RESPONSES = [
        "Это демо-ответ. В продакшене здесь была бы реальная нейросеть.",
        "Отличный вопрос! Я работаю в демо-режиме, но архитектура полностью готова.",
        "Спасибо за вопрос! Сейчас я имитирую работу модели для экономии ресурсов.",
        "Интересная тема! В реальной версии я бы сгенерировал более подробный ответ.",
        "Демо-режим активен. Этот ответ сгенерирован мгновенно без GPU.",
    ]
    
    async def generate(self, request: ChatRequest) -> str:
        """Мгновенный демо-ответ"""
        logger.info("Demo mode: generating fake response")
        await asyncio.sleep(0.5)  # Имитация задержки
        return random.choice(self.DEMO_RESPONSES)
    
    async def generate_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Потоковый демо-ответ (по буквам)"""
        logger.info("Demo mode: streaming fake response")
        response = random.choice(self.DEMO_RESPONSES)
        
        for char in response:
            yield char
            await asyncio.sleep(0.03)  # Имитация задержки между токенами
    
    async def health_check(self) -> bool:
        """Демо-сервис всегда здоров"""
        return True
    
    async def close(self):
        pass