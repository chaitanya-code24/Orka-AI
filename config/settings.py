from pydantic import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "llama-3.3-70b-versatile"
    base_url: str = "https://api.groq.com/openai/v1"

    class Config:
        env_file = ".env"

settings = Settings()
