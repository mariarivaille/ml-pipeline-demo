FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

EXPOSE 8000

# Запуск приложения из корня, но с указанием пути к main
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]