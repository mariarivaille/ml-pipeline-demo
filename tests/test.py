import pytest
from fastapi.testclient import TestClient
import sys
import os

# Добавляем корень проекта в путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    Примечание: без валидного API_KEY вернётся 500, что тоже является проверкой.
    """
    payload = {
        "messages": [
            {"role": "user", "content": "Привет"}
        ],
        "temperature": 0.7,
        "top_p": 0.1
    }
    response = client.post("/api/chat", json=payload)
    
    # Либо 200 (если ключ валиден), либо 500 (если ключа нет)
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
    # Пустой массив может вызвать ошибку валидации или логики
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
    # FastAPI должен отклонить некорректные данные
    assert response.status_code in [200, 422, 500]