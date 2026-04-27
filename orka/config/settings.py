import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    base_url: str = os.getenv("BASE_URL", "https://api.groq.com/openai/v1")


settings = Settings()
