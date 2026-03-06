FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для компиляции llama-cpp-python
RUN apt-get update && apt-get install -y \
    curl \
    git \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем llama-cpp-python с флагами для CPU
RUN CMAKE_ARGS="-DLLAMA_BLAS=OFF" pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY app/ ./app/

# === Скачиваем модель при сборке ===
ARG HF_TOKEN
ARG MODEL_URL=https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf
ARG MODEL_PATH=/app/models/model.gguf

RUN mkdir -p /app/models && \
    curl -L -H "Authorization: Bearer ${HF_TOKEN}" -o ${MODEL_PATH} ${MODEL_URL} && \
    ls -lh ${MODEL_PATH}

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]