import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@postgres:5432/linguafuse"

    # Redis/Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "./storage"

    # AI Providers
    TTS_PROVIDER: str = "coqui"
    ELEVENLABS_API_KEY: str = ""
    TRANSLATION_PROVIDER: str = "seamlessm4t"
    GOOGLE_TRANSLATE_API_KEY: str = ""

    # Wav2Lip
    WAV2LIP_CHECKPOINT_PATH: str = "./models/checkpoints/wav2lip_gan.pth"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# BCP-47 Language Map
LANGUAGE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Odia": "or",
    "Assamese": "as",
    "Urdu": "ur",
    "Sanskrit": "sa",
    "Konkani": "kok",
    "Manipuri": "mni",
    "Nepali": "ne",
    "Kashmiri": "ks",
    "Sindhi": "sd",
    "Bodo": "brx",
    "Dogri": "doi",
    "Maithili": "mai",
    "Santali": "sat",
}
