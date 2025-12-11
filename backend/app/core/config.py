from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database Configuration
    DATABASE_URL: str = "postgresql://ai_user:password@localhost/ai_therapy"

    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "AI Therapy Backend"

    # ===== AI & Agno Configuration =====
    OPENAI_API_KEY: str = ""

    # Agno Database (默认使用主数据库)
    AGNO_DB_URL: Optional[str] = None

    # Therapist Agent 配置
    THERAPIST_MODEL: str = "gpt-4o"
    THERAPIST_HISTORY_RUNS: int = 100
    THERAPIST_ENABLE_MEMORY: bool = True
    THERAPIST_MARKDOWN: bool = False
    THERAPIST_TEMPERATURE: float = 0.7

    # Clerk Agent 配置
    CLERK_MODEL: str = "gpt-4o-mini"
    CLERK_TEMPERATURE: float = 0.0

    # Onboarding Agent 配置
    ONBOARDING_MODEL: str = "gpt-4o-mini"

    # Agno 性能配置
    AGNO_AUTO_CREATE_TABLES: bool = True
    AGNO_TABLE_PREFIX: str = "agno_"

    # Session 时间和轮数控制
    SESSION_SUGGESTED_DURATION_MINUTES: int = 30  # 建议咨询时长（分钟）
    SESSION_SUGGESTED_TURNS: int = 30  # 建议对话轮数
    SESSION_REMINDER_INTERVAL: int = 3  # 超时后每N轮提示一次

    @property
    def agno_database_url(self) -> str:
        """获取 Agno 数据库 URL"""
        return self.AGNO_DB_URL or self.DATABASE_URL

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
