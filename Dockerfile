FROM python:3.9-slim

# 1. Объявляем аргумент сборки (не попадает в финальный образ при правильной настройке)
ARG HF_TOKEN
# 2. Передаем его в переменную окружения только на время сборки
ENV HF_TOKEN=${HF_TOKEN}

WORKDIR /app

# 3. Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем код приложения
COPY . .

# 5. Создаем папку для модели
# RUN mkdir -p /models

# 6. Скачиваем модель ТОЛЬКО если передан токен
# Используем --progress=off для чистоты логов
RUN if [ -n "$HF_TOKEN" ]; then \
      curl -L -H "Authorization: Bearer $HF_TOKEN" \
      "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q5_k_m.gguf" \
      -o /models/qwen2.5-0.5b-instruct-q5_k_m.gguf; \
    fi

# 7. Очищаем переменную (безопасность)
ENV HF_TOKEN=

EXPOSE 8000
CMD ["python", "app/main.py"]