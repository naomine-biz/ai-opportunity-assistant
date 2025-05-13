from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """アプリケーション設定"""

    # アプリケーション全般
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_BASE_URL: str = "http://127.0.0.1:8000"  # 内部API呼び出し用ベースURL
    API_TIMEOUT: float = 30.0  # API呼び出しのタイムアウト（秒）

    # データベース
    DATABASE_URL: PostgresDsn

    # Slack
    SLACK_BOT_TOKEN: str
    SLACK_SIGNING_SECRET: str

    # OpenAI
    OPENAI_API_KEY: str

    # スケジューラー
    SCHEDULER_TIMEZONE: str = "Asia/Tokyo"
    SCHEDULER_PROGRESS_CHECK_CRON: str = "0 9 * * *"  # 毎日午前9時に実行
    SCHEDULER_KPI_CHECK_CRON: str = "0 10 * * 1"  # 毎週月曜日の午前10時に実行

    # 通知条件
    NOTIFICATION_INACTIVITY_DAYS: int = 3  # この日数以上アクティビティがない場合に通知
    NOTIFICATION_RETRY_DAYS: int = 2  # 通知後、この日数経過で再通知

    # Slack通知
    SLACK_NOTIFICATION_CHANNEL: str = ""  # 特定のチャンネルに通知する場合（空欄ならDM）
    SLACK_MENTION_ON_CHANNEL: bool = True  # チャンネル通知時にメンションをつけるか

    class Config:
        env_file = ".env"
        case_sensitive = True


# 設定インスタンスを作成
settings = Settings()
