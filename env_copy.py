import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv(".env")


class Env(BaseModel):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    OPENAI_API_KEY: str
    FPTSHOP_BASE_URL: str
    LITERAL_API_KEY: str
    GEMINI_API_KEY: str
    CHAINLIT_AUTH_SECRET: str
    CHAINLIT_HOST: str
    CHAINLIT_PORT: int
    SENDER_EMAIL: str
    RECEIVER_EMAIL: str
    CLIENT_ID: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Open Source Model Configuration
    OPEN_SOURCE_MODEL_URL: str = ""  # URL của API model open source
    OPEN_SOURCE_MODEL_NAME: str = ""  # Tên model open source
    OPEN_SOURCE_API_KEY: Optional[str] = None  # API key cho model open source (nếu cần)


env = Env.model_validate(os.environ)
