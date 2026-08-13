"""Runtime settings with safe local defaults."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FAULTGRAPH_", env_file=".env", extra="ignore")

    database_path: Path = Path("data/faultgraph.db")
    static_directory: Path = Path("static")
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    environment: str = "development"
