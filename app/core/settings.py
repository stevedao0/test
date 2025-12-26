from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    supabase_url: str = os.getenv("VITE_SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY", "")

    project_root: Path = Path(__file__).resolve().parents[2]

    session_secret_key: str = os.getenv("SESSION_SECRET_KEY", "contract-management-secret-key-change-in-production")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
