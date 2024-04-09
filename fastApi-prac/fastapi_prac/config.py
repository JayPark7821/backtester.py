from functools import lru_cache
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings, extra="allow"):
    ENV_STATE: Optional[str] = None
    model_config = ConfigDict(env_file=".env")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None


class DevConfig(GlobalConfig):
    model_config = ConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = ConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    DB_FORCE_ROLL_BACK: bool = True
    model_config = ConfigDict(env_prefix="TEST_")


@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
