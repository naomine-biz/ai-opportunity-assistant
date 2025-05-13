from fastapi import APIRouter

from src.api.routes import (
    activity_routes,
    notification_routes,
    opportunity_routes,
    slack_routes,
)

# メインAPIルーター
api_router = APIRouter()


# Slackイベント関連のルートを登録
api_router.include_router(slack_routes.router, prefix="/slack", tags=["slack"])

# オポチュニティ関連のルート登録
api_router.include_router(
    opportunity_routes.router, prefix="/opportunity", tags=["opportunity"]
)

# アクティビティログ関連のルート登録
api_router.include_router(
    activity_routes.router, prefix="/activity_log", tags=["activity"]
)

# 通知関連のルート登録
api_router.include_router(
    notification_routes.router, prefix="/notify", tags=["notification"]
)
