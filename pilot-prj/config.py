from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="allow"
    )
    env_state: Optional[str] = None


class GlobalConfig(BaseConfig):
    MONGO_URL: Optional[str] = None
    MONGO_DB_NAME: Optional[str] = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


@lru_cache()
def get_config(env_state: str) -> GlobalConfig:
    configs = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}
    return configs[env_state]()


config = get_config(BaseConfig().env_state)
