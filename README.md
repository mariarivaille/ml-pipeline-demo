# LLM ChatBot Demo

Демонстрационный проект для лекции по деплою LLM-моделей.

## 🚀 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)
```bash
# Скачать модель (опционально, ускорит первый запуск)
bash scripts/download_model.sh

# Запустить всё
docker compose up --build

# Проверить
curl http://localhost:8000/health