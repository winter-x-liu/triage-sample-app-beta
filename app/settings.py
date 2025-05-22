"""Settings, from the environment where the deployment differs."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    state_name: str = "State Beta"
    app_version: str = "4.3"
    database_url: str = os.environ.get("DATABASE_URL", "postgresql://localhost/mockapp")
    schema: str = os.environ.get("APP_SCHEMA", "app_beta")


settings = Settings()
