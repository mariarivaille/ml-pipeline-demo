from fastapi import FastAPI
import pickle
import pandas as pd
from pydantic import BaseModel, Field

app = FastAPI(
    title="Titanic Survival Predictor",
    description="ML-сервис для предсказания выживания пассажиров Титаника на основе логистической регрессии",
    version="1.0.0"
)

# Загружаем модель при старте
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Описание входных данных с полной валидацией и документацией
class InputData(BaseModel):
    pclass: int = Field(
        ..., 
        ge=1, 
        le=3, 
        title="Класс билета",
        description="Класс каюты пассажира: 1 = первый класс, 2 = второй класс, 3 = третий класс",
        examples=[1, 2, 3]
    )
    sex: str = Field(
        ..., 
        pattern="^(male|female)$", 
        title="Пол",
        description="Пол пассажира. Допустимые значения: 'male' или 'female'",
        examples=["female", "male"]
    )
    age: float = Field(
        ..., 
        ge=0, 
        le=120, 
        title="Возраст",
        description="Возраст пассажира в годах. Допустимый диапазон: 0-120",
        example=22.0
    )
    sibsp: int = Field(
        ..., 
        ge=0, 
        le=10, 
        title="Братья/Сёстры",
        description="Количество братьев или сестёр пассажира на борту. Максимум 10",
        examples=range(11)
    )
    parch: int = Field(
        ..., 
        ge=0, 
        le=10, 
        title="Родители/Дети",
        description="Количество родителей или детей пассажира на борту. Максимум 10",
        examples=range(11)
    )
    fare: float = Field(
        ..., 
        ge=0, 
        title="Стоимость билета",
        description="Цена билета в фунтах стерлингов. Должна быть неотрицательным числом",
        example=7.25
    )
    embarked: str = Field(
        ..., 
        pattern="^(C|Q|S)$", 
        title="Порт посадки",
        description="Порт, где пассажир сел на корабль: C = Cherbourg, Q = Queenstown, S = Southampton",
        examples=["C", "Q", "S"]
    )

# Модель ответа для документации
class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="0 = погиб, 1 = выжил")
    survived: bool = Field(..., description="True если пассажир выжил, иначе False")
    survived_text: bool = Field(..., description="Выжил/Погиб")
    input_data: dict = Field(..., description="Входные данные, использованные для предсказания")

@app.get("/", tags=["Главная страница"])
def root():
    """
    Главная страница сервиса.
    
    Возвращает статус работы ML-сервиса.
    """
    return {"message": "ML Service is running!"}

@app.post("/predict", response_model=PredictionResponse, tags=["Предсказание судьбы для пассажира"])
def predict(
    data: InputData
):
    """
    Предсказание выживания пассажира Титаника.
    
    **Как это работает:**
    - Модель анализирует данные пассажира
    - Возвращает вероятность выживания (0 или 1)
    
    **Примеры успешных запросов:**
    - Женщина, 1 класс, 25 лет → высокий шанс выживания
    - Мужчина, 3 класс, 40 лет → низкий шанс выживания
    
    **Валидация:**
    - Все поля обязательны
    - Значения должны соответствовать указанным ограничениям
    """
    # Преобразуем данные Pydantic в словарь
    input_dict = data.dict()
    
    # Создаем DataFrame (1 строка), чтобы модель поняла имена колонок
    input_df = pd.DataFrame([input_dict])
    
    # Делаем предсказание
    prediction = model.predict(input_df)[0]
    
    # Возвращаем результат
    return {
        "prediction": int(prediction), 
        "survived": bool(prediction),
        "survived_text": "Выжил" if bool(prediction) else "Погиб",
        "input_data": input_dict
    }

@app.get("/health", tags=["Проверка доступности сервиса"])
def health_check():
    """
    Проверка здоровья сервиса.
    
    Используется для мониторинга доступности сервиса.
    """
    return {"status": "healthy"}