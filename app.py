from fastapi import FastAPI
import pickle
from pydantic import BaseModel

app = FastAPI()

# Загружаем модель при старте
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

class InputData(BaseModel):
    value: int

@app.get("/")
def root():
    return {"message": "ML Service is running!"}

@app.post("/predict")
def predict( InputData):
    prediction = model.predict([[data.value]])[0]
    return {"prediction": int(prediction)}