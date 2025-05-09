from fastapi import APIRouter

from api.routes import slack_routes

# メインAPIルーター
api_router = APIRouter()

# Slackイベント関連のルートを登録
api_router.include_router(slack_routes.router, prefix="/slack", tags=["slack"])

# TODO: 他のルーターを追加する
# api_router.include_router(opportunity_routes.router, prefix="/opportunity", tags=["opportunity"])
# api_router.include_router(activity_routes.router, prefix="/activity_log", tags=["activity"])
# api_router.include_router(notification_routes.router, prefix="/notify", tags=["notification"])