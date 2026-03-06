import logging
import sys
from app.config import settings

def setup_logger(name: str) -> logging.Logger:
    """Настройка логгера для всего приложения"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Консольный обработчик
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

logger = setup_logger(__name__)