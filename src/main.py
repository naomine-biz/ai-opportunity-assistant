import uvicorn
from fastapi import FastAPI

from src.api.api import api_router
from src.core.config import settings
from src.core.logger import get_app_logger
from src.db.session import create_db_and_tables

logger = get_app_logger()

# APIタグの説明
tags_metadata = [
    {
        "name": "opportunity",
        "description": "オポチュニティ（営業案件）に関するエンドポイント。案件の作成、更新、検索などの操作が含まれます。",
    },
    {
        "name": "activity",
        "description": "アクティビティログ（営業活動記録）に関するエンドポイント。営業活動の記録管理を行います。",
    },
    {
        "name": "notification",
        "description": "通知機能に関するエンドポイント。期限や活動状況に基づくアラート通知を管理します。",
    },
    {
        "name": "slack",
        "description": "Slack連携に関するエンドポイント。Slackイベントの受信や通知送信を処理します。",
    },
]

# FastAPIアプリケーションの作成
app = FastAPI(
    title="営業オポチュニティマネジメント AIアシスタント",
    description="""
    営業活動の記録と分析を支援するAIアシスタントシステム。

    ## 主な機能
    
    * **オポチュニティ管理**: 案件情報の追加・更新・検索
    * **アクティビティログ**: 営業活動の記録と履歴管理
    * **通知**: 期限切れや活動不足に関するアラート
    * **Slack連携**: SlackボットとのUI連携
    
    ## 利用シナリオ
    
    営業担当者はSlackを通じて自然言語でアクティビティを記録し、
    AIがそれを構造化データとして保存します。
    システムは期限や進捗状況に基づき、適切なアクションを提案します。
    """,
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,  # 本番環境ではSwagger UIを無効化
    redoc_url="/redoc" if settings.DEBUG else None,  # 本番環境ではRedocを無効化
    openapi_tags=tags_metadata,
    contact={
        "name": "開発チーム",
        "email": "dev-team@example.com",
    },
    license_info={
        "name": "社内利用限定",
    },
)


@app.on_event("startup")
def startup_event() -> None:
    """アプリケーション起動時の初期化処理"""
    logger.info("Application startup")
    create_db_and_tables()


@app.on_event("shutdown")
def shutdown_event() -> None:
    """アプリケーション終了時の処理"""
    logger.info("Application shutdown")


@app.get("/")
def read_root() -> dict:
    """ルートエンドポイント"""
    return {"message": "AI Opportunity Assistant API"}


# APIルーターを登録
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
