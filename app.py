from fastapi import FastAPI
import pickle
import pandas as pd
from pydantic import BaseModel, Field

app = FastAPI()

# Загружаем модель при старте
with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)

# Описание входных данных (признаки Титаника)
class InputData(BaseModel):
    pclass: int = Field(
        ..., 
        ge=1, 
        le=3, 
        description="Класс билета (1, 2 или 3)",
        example=3
    )
    sex: str = Field(
        ..., 
        pattern="^(male|female)$", 
        description="Пол пассажира",
        example="male"
    )
    age: float = Field(
        ..., 
        ge=0, 
        le=120, 
        description="Возраст пассажира",
        example=22.0
    )
    sibsp: int = Field(
        ..., 
        ge=0, 
        le=10, 
        description="Количество братьев/сестер на борту",
        example=1
    )
    parch: int = Field(
        ..., 
        ge=0, 
        le=10, 
        description="Количество родителей/детей на борту",
        example=0
    )
    fare: float = Field(
        ..., 
        ge=0, 
        description="Стоимость билета",
        example=7.25
    )
    embarked: str = Field(
        ..., 
        pattern="^(C|Q|S)$", 
        description="Порт посадки (C=Cherbourg, Q=Queenstown, S=Southampton)",
        example="S"
    )

@app.get("/")
def root():
    return {"message": "ML Service is running!"}

@app.post("/predict")
def predict(data: InputData):
    # Преобразуем данные Pydantic в словарь
    input_dict = data.dict()
    
    # Создаем DataFrame (1 строка), чтобы модель поняла имена колонок
    # Это важно, так как в Pipeline мы использовали имена колонок
    input_df = pd.DataFrame([input_dict])
    
    # Делаем предсказание
    prediction = model.predict(input_df)[0]
    
    # Возвращаем результат (0 - погиб, 1 - выжил)
    return {"prediction": int(prediction), "survived": bool(prediction), "survived_text": "Выжил" if bool(prediction) else "Погиб"}