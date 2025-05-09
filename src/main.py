import uvicorn
from fastapi import FastAPI

from core.config import settings
from core.logger import get_app_logger
from db.session import create_db_and_tables

logger = get_app_logger()

# FastAPIアプリケーションの作成
app = FastAPI(
    title="営業オポチュニティマネジメント AIアシスタント",
    description="営業活動の記録と分析を支援するAIアシスタントシステム",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,  # 本番環境ではSwagger UIを無効化
    redoc_url="/redoc" if settings.DEBUG else None,  # 本番環境ではRedocを無効化
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
