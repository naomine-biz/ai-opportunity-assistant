"""
通知関連APIルート定義
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from api.schemas import NotificationRequest, NotificationResponse
from core.logger import get_notification_logger
from services.notification_service import (
    check_progress_notifications,
    send_kpi_notification,
    send_progress_notifications,
)

router = APIRouter()
logger = get_notification_logger()


@router.post(
    "/progress", response_model=NotificationResponse, status_code=status.HTTP_200_OK
)
async def send_progress_notification(notification_data: NotificationRequest):
    """
    進捗確認の通知を送信する内部API

    Args:
        notification_data: 通知データ（対象日など）

    Returns:
        通知処理結果の要約
    """
    try:
        # サービスレイヤーに処理を委譲
        notifications_to_send = await check_progress_notifications(
            notification_data.target_date
        )

        # 実際の通知処理をサービスに委譲
        success_count = await send_progress_notifications(notifications_to_send)

        logger.info(
            "Progress notification process completed",
            extra={
                "target_date": notification_data.target_date.isoformat(),
                "notifications_count": len(notifications_to_send),
                "success_count": success_count,
            },
        )

        return {
            "status": "completed",
            "target_date": notification_data.target_date,
            "notifications_count": len(notifications_to_send),
            "notifications_sent": success_count,
            "notifications": notifications_to_send,
        }
    except Exception as e:
        logger.error(f"Error checking progress notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking progress notifications: {str(e)}",
        )


class KpiNotificationRequest(BaseModel):
    """KPI通知リクエストスキーマ"""

    user_slack_id: str
    message: str
    opportunity_id: Optional[uuid.UUID] = None
    opportunity_title: Optional[str] = None


class KpiNotificationResponse(BaseModel):
    """KPI通知レスポンススキーマ"""

    status: str
    success: bool
    user_slack_id: str


@router.post(
    "/kpi", response_model=KpiNotificationResponse, status_code=status.HTTP_200_OK
)
async def send_kpi_action_notification(notification_data: KpiNotificationRequest):
    """
    KPI達成を促す通知を特定ユーザーに送信する内部API

    Args:
        notification_data: 通知データ（ユーザー、メッセージなど）

    Returns:
        通知処理結果の要約
    """
    try:
        # サービスレイヤーに処理を委譲
        success = await send_kpi_notification(
            user_slack_id=notification_data.user_slack_id,
            message=notification_data.message,
            opportunity_id=notification_data.opportunity_id,
            opportunity_title=notification_data.opportunity_title,
        )

        logger.info(
            "KPI notification process completed",
            extra={
                "user_slack_id": notification_data.user_slack_id,
                "success": success,
            },
        )

        return {
            "status": "completed" if success else "failed",
            "success": success,
            "user_slack_id": notification_data.user_slack_id,
        }
    except Exception as e:
        logger.error(f"Error sending KPI notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending KPI notification: {str(e)}",
        )
