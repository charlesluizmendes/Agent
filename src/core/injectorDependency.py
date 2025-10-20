import os
from dotenv import load_dotenv
from functools import lru_cache

from src.core.services.newsService import NewsService

load_dotenv(".env", override=False)
load_dotenv(".env.local", override=True)


OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_KEY = os.getenv("OPENAI_KEY")
OPENAI_TEMPERATURE = os.getenv("OPENAI_TEMPERATURE")

@lru_cache()
def get_news_service() -> NewsService:
    return NewsService(
        model=OPENAI_MODEL,
        api_key=OPENAI_KEY,
        temperature=OPENAI_TEMPERATURE
    )