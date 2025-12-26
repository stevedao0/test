from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parents[2]
load_dotenv(_project_root / ".env")


class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "") or os.getenv("VITE_SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("VITE_SUPABASE_ANON_KEY", "")

    project_root: Path = _project_root

    session_secret_key: str = os.getenv("SESSION_SECRET_KEY", "contract-management-secret-key-change-in-production")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
