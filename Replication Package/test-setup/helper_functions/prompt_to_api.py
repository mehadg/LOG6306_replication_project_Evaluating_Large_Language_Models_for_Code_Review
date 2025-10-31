import requests
import time

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

MODEL_MAP = {
    "mistral": "mistral:7b-instruct",
    "llama": "llama3:latest",
}

def _ollama_generate(model_tag: str, prompt: str, timeout=180) -> str:
    for _ in range(3):
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": model_tag,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=timeout,
            )
            r.raise_for_status()
            return r.json().get("response", "")
        except Exception as e:
            print(f"Ollama error: {e}")
            time.sleep(2)
    raise RuntimeError("Ollama call failed repeatedly")

def get_response(user_prompt: str, model_key: str) -> str:
    return _ollama_generate(MODEL_MAP.get(model_key, model_key), user_prompt)
