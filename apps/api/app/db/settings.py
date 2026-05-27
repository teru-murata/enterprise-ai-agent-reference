from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    database_url: str


def get_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "enterprise_ai_agent")
    user = os.getenv("POSTGRES_USER", "app")
    password = os.getenv("POSTGRES_PASSWORD", "app")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings(database_url=get_database_url())
