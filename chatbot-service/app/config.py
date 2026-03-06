from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # === Режимы работы ===
    DEMO_MODE: bool = False  # True = заглушка, False = реальная модель
    USE_LLMAMA_CPP: bool = True  # Использовать llama.cpp
    
    # === Настройки модели ===
    MODEL_NAME: str = "Qwen/Qwen2.5-0.5B-Instruct"
    MODEL_PATH: str = "./models/qwen2.5-0.5b-instruct-q4_k_m.gguf"
    MAX_TOKENS: int = 256
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # === Настройки llama.cpp сервера ===
    LLAMA_CPP_URL: str = "http://llama-cpp:8001"
    LLAMA_CPP_TIMEOUT: int = 60  # секунд
    
    # === Настройки API ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "LLM ChatBot Demo"
    API_VERSION: str = "1.0.0"
    
    # === Логирование ===
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # === Rate Limiting ===
    RATE_LIMIT_PER_MINUTE: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()