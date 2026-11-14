
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: str = "dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: str | None = None
    DB_FORCE_ROLL_BACK: bool = False
    MAILGUN_DOMAIN: str | None = None
    MAILGUN_API_KEY: str | None = None
    LOGTAIL_API_KEY: str | None = None
    B2_KEY_ID: str | None = None
    B2_APPLICATION_KEY: str | None = None
    B2_BUCKET_NAME: str | None = None
    DEEPAI_API_KEY: str | None = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DEV_",
        extra="ignore"
    )


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PROD_",
        extra="ignore"
    )


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TEST_",
        extra="ignore"
    )


@lru_cache()
def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig,
    }
    if env_state not in configs:
        raise ValueError(f"Unknown environment: {env_state}")
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)