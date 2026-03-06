#!/bin/bash
# Скрипт для скачивания модели локально (для разработки)

set -e

MODEL_DIR="./models"
MODEL_FILE="qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/${MODEL_FILE}"

echo "📥 Скачивание модели Qwen2.5-0.5B..."

mkdir -p ${MODEL_DIR}

if [ -f "${MODEL_DIR}/${MODEL_FILE}" ]; then
    echo "✅ Модель уже существует"
else
    echo "⏳ Загрузка может занять 5-10 минут..."
    curl -L -o "${MODEL_DIR}/${MODEL_FILE}" "${MODEL_URL}"
    echo "✅ Модель скачана: $(ls -lh ${MODEL_DIR}/${MODEL_FILE})"
fi

echo "📊 Размер: $(du -h ${MODEL_DIR}/${MODEL_FILE} | cut -f1)"