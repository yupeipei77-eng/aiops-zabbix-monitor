from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "aiops-zabbix-monitor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://aiops:aiops@localhost:5432/aiops"
    REDIS_URL: str = "redis://localhost:6379/0"

    WEBHOOK_API_KEY: str = "changeme-webhook-api-key"

    DEFAULT_LLM_PROVIDER: str = "mock"
    ADVANCED_LLM_PROVIDER: str = "mock"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: Optional[str] = None

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: Optional[str] = None

    KIMI_API_KEY: Optional[str] = None
    KIMI_MODEL: str = "moonshot-v1-8k"
    KIMI_BASE_URL: Optional[str] = None

    MIMO_API_KEY: Optional[str] = None
    MIMO_MODEL: str = "mimo"
    MIMO_BASE_URL: Optional[str] = None

    GATEWAY_API_KEY: Optional[str] = None
    GATEWAY_BASE_URL: Optional[str] = None
    GATEWAY_DEFAULT_MODEL: str = "deepseek-v4-flash"
    GATEWAY_PROVIDER_NAME: str = "gateway"

    LLM_POLICY_LOW_PROVIDER: str = "mock"
    LLM_POLICY_LOW_MODEL: str = "mock"
    LLM_POLICY_MEDIUM_PROVIDER: str = "mock"
    LLM_POLICY_MEDIUM_MODEL: str = "mock"
    LLM_POLICY_HIGH_PROVIDER: str = "mock"
    LLM_POLICY_HIGH_MODEL: str = "mock"
    LLM_POLICY_CRITICAL_PROVIDER: str = "mock"
    LLM_POLICY_CRITICAL_MODEL: str = "mock"

    DEDUP_WINDOW_SECONDS: int = 300
    STORM_WINDOW_SECONDS: int = 600
    STORM_THRESHOLD: int = 50

    ZABBIX_URL: Optional[str] = None
    ZABBIX_API_TOKEN: Optional[str] = None

    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
