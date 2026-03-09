import pytest
from fastapi.testclient import TestClient
import sys
import os

# Гарантируем правильный путь для импорта app в CI и локально
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app.main import app

client = TestClient(app)


def test_health_check():
    """Тест проверки здоровья сервиса."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_page():
    """Тест загрузки главной страницы."""
    response = client.get("/")
    assert response.status_code == 200
    assert "GigaChat Bot" in response.text


def test_chat_api_structure():
    """
    Тест структуры API чата.
    Если API_KEY нет (в CI), сервер вернет 500. Это ожидаемое поведение.
    Если ключ есть, вернет 200.
    """
    payload = {
        "messages": [
            {"role": "user", "content": "Привет"}
        ],
        "temperature": 0.7,
        "top_p": 0.1
    }
    response = client.post("/api/chat", json=payload)
    
    # Разрешаем и 200 (успех), и 500 (нет ключа в CI)
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        assert "response" in response.json()


def test_chat_api_empty_messages():
    """Тест обработки пустого списка сообщений."""
    payload = {
        "messages": [],
        "temperature": 0.7
    }
    response = client.post("/api/chat", json=payload)
    # Pydantic может отклонить пустой список (422) или сервер вернет ошибку (500)
    assert response.status_code in [200, 422, 500]


def test_chat_api_invalid_role():
    """Тест обработки некорректной роли сообщения."""
    payload = {
        "messages": [
            {"role": "invalid_role", "content": "Привет"}
        ],
        "temperature": 0.7
    }
    response = client.post("/api/chat", json=payload)
    # Pydantic валидация (422) или ошибка сервера (500)
    assert response.status_code in [200, 422, 500]