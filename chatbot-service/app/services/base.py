from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.schemas import ChatRequest

class BaseModelService(ABC):
    """Базовый класс для всех сервисов генерации"""
    
    @abstractmethod
    async def generate(self, request: ChatRequest) -> str:
        """Синхронная генерация ответа"""
        pass
    
    @abstractmethod
    async def generate_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Потоковая генерация ответа"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Проверка работоспособности сервиса"""
        pass