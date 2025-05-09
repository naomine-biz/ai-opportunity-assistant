from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """アプリケーション設定"""

    # アプリケーション全般
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # データベース
    DATABASE_URL: PostgresDsn

    # Slack
    SLACK_BOT_TOKEN: str
    SLACK_SIGNING_SECRET: str

    # OpenAI
    OPENAI_API_KEY: str

    # スケジューラー
    SCHEDULER_TIMEZONE: str = "Asia/Tokyo"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 設定インスタンスを作成
settings = Settings()
