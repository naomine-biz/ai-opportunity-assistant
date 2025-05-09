"""
通知関連APIルート定義
"""

from fastapi import APIRouter, HTTPException, status

from api.schemas import NotificationRequest, NotificationResponse
from core.logger import get_notification_logger
from services.notification_service import check_progress_notifications

router = APIRouter()
logger = get_notification_logger()


@router.post(
    "/progress", response_model=NotificationResponse, status_code=status.HTTP_200_OK
)
async def trigger_progress_notification(notification_data: NotificationRequest):
    """
    スケジューラーからの進捗通知処理をトリガする内部API

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

        # 実際の通知処理は別のサービスに委譲（このAPIでは通知対象の特定のみを行う）
        # TODO: 通知サービスを呼び出す実装を追加

        logger.info(
            "Progress notification check completed",
            extra={
                "target_date": notification_data.target_date.isoformat(),
                "notifications_count": len(notifications_to_send),
            },
        )

        return {
            "status": "completed",
            "target_date": notification_data.target_date,
            "notifications_count": len(notifications_to_send),
            "notifications": notifications_to_send,
        }
    except Exception as e:
        logger.error(f"Error checking progress notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking progress notifications: {str(e)}",
        )
