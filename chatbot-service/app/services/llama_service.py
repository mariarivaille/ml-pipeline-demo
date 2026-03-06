import httpx
import asyncio
from typing import AsyncGenerator
from app.config import settings
from app.schemas import ChatRequest
from app.services.base import BaseModelService
from app.utils.logger import logger

class LlamaCppService(BaseModelService):
    """Сервис для работы с llama.cpp сервером"""
    
    def __init__(self):
        self.base_url = settings.LLAMA_CPP_URL
        self.timeout = settings.LLAMA_CPP_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout)
        logger.info(f"LlamaCppService initialized with URL: {self.base_url}")
    
    def _format_prompt(self, messages: list) -> str:
        """Форматирование истории сообщений в промпт для Qwen"""
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"].strip()
            if role == "system":
                prompt += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"
        return prompt
    
    async def generate(self, request: ChatRequest) -> str:
        """Синхронная генерация через llama.cpp API"""
        try:
            prompt = self._format_prompt([m.model_dump() for m in request.messages])
            
            payload = {
                "prompt": prompt,
                "n_predict": request.max_tokens or settings.MAX_TOKENS,
                "temperature": request.temperature or settings.TEMPERATURE,
                "top_p": settings.TOP_P,
                "stream": False,
                "stop": ["<|im_end|>", "<|endoftext|>"]
            }
            
            response = await self.client.post(
                f"{self.base_url}/completion",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("content", "").strip()
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during generation: {e}")
            raise Exception(f"Model service error: {str(e)}")
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    async def generate_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Потоковая генерация через llama.cpp SSE API"""
        try:
            prompt = self._format_prompt([m.model_dump() for m in request.messages])
            
            payload = {
                "prompt": prompt,
                "n_predict": request.max_tokens or settings.MAX_TOKENS,
                "temperature": request.temperature or settings.TEMPERATURE,
                "top_p": settings.TOP_P,
                "stream": True,
                "stop": ["<|im_end|>", "<|endoftext|>"]
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/completion",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Убираем "data: "
                        if data.strip() == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            content = chunk.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка доступности llama.cpp сервера"""
        try:
            response = await self.client.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()