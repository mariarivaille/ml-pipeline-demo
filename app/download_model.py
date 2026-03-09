import os
import requests

MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q5_k_m.gguf"
MODEL_PATH = os.getenv("MODEL_PATH", "models/qwen2.5-0.5b-instruct-q5_k_m.gguf")

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"✅ Модель уже существует: {MODEL_PATH}")
        return
    
    print(f"📥 Скачивание модели из {MODEL_URL}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    try:
        with requests.get(MODEL_URL, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(MODEL_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = (downloaded / total) * 100
                        print(f"\r⬇️  Загружено: {percent:.1f}%", end="")
            print("\n✅ Модель успешно загружена!")
            
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        raise

if __name__ == "__main__":
    download_model()