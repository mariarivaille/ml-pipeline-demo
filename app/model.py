import os
from llama_cpp import Llama

MODEL_PATH = os.getenv("MODEL_PATH", "models/qwen2.5-0.5b-instruct-q5_k_m.gguf")

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._model = None
        self._initialized = True
    
    def load(self):
        if self._model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Модель не найдена: {MODEL_PATH}")
            
            print(f"🧠 Загрузка модели: {MODEL_PATH}")
            self._model = Llama(
                model_path=MODEL_PATH,
                n_ctx=2048,
                n_threads=4,
                verbose=False
            )
            print("✅ Модель загружена в память")
        return self._model
    
    def get(self):
        if self._model is None:
            self.load()
        return self._model

model_manager = ModelManager()