from __future__ import annotations

from functools import lru_cache
from supabase import create_client, Client

from app.core.settings import get_settings


@lru_cache
def get_supabase_client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase() -> Client:
    return get_supabase_client()
