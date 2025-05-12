"""
スケジューラータスクランナー - 定期実行処理を定義するモジュール
"""

from datetime import date, datetime
from typing import Dict, List, Optional

import httpx

from core.config import settings
from core.logger import get_notification_logger

logger = get_notification_logger()

# 内部API接続情報
BASE_URL = "http://127.0.0.1:8000"  # settings.API_BASE_URLがあれば使用する
API_TIMEOUT = 30.0  # 秒

# 設定がある場合はそちらを優先
if hasattr(settings, "API_BASE_URL") and settings.API_BASE_URL:
    BASE_URL = settings.API_BASE_URL


async def run_progress_notification_check() -> int:
    """
    進捗確認通知処理を実行する（内部APIを呼び出す）

    Returns:
        送信された通知の数
    """
    logger.info("Starting progress notification check task")
    try:
        today = date.today()

        # 内部APIを呼び出す
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/notification/progress",
                json={"target_date": today.isoformat()},
            )

            if response.status_code != 200:
                logger.error(
                    "Failed to call progress notification API",
                    extra={
                        "status_code": response.status_code,
                        "response_text": response.text,
                    },
                )
                return 0

            result = response.json()
            notifications_sent = result.get("notifications_sent", 0)

        logger.info(
            "Progress notification check completed",
            extra={
                "date": today.isoformat(),
                "notifications_sent": notifications_sent,
            },
        )
        return notifications_sent
    except Exception as e:
        logger.error(f"Error in progress notification check task: {str(e)}")
        return 0


async def run_kpi_action_notification(target_users: Optional[List[Dict]] = None) -> int:
    """
    KPI達成促進の通知処理を実行する（内部APIを呼び出す）

    Args:
        target_users: 対象ユーザーリスト（省略時は全ユーザー）

    Returns:
        送信された通知の数
    """
    logger.info("Starting KPI action notification task")
    try:
        # デモ用のターゲットユーザー（実際の実装では動的に決定）
        if target_users is None:
            target_users = [
                {
                    "slack_id": "U12345678",
                    "kpi_status": "at_risk",
                    "message": "今週の会議数KPIが未達成です。あと2件の会議を設定しましょう。",
                }
            ]

        sent_count = 0
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            for user in target_users:
                slack_id = user.get("slack_id")
                message = user.get("message")

                if not slack_id or not message:
                    continue

                # 内部APIを呼び出す - パスはルーターのプレフィックスによって異なる可能性がある
                response = await client.post(
                    f"{BASE_URL}/api/notification/kpi",
                    json={
                        "user_slack_id": slack_id,
                        "message": message,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success", False):
                        sent_count += 1
                else:
                    logger.error(
                        "Failed to call KPI notification API",
                        extra={
                            "user_slack_id": slack_id,
                            "status_code": response.status_code,
                            "response_text": response.text,
                        },
                    )

        logger.info(
            "KPI action notification completed",
            extra={
                "date": datetime.now().isoformat(),
                "target_users": len(target_users) if target_users else 0,
                "notifications_sent": sent_count,
            },
        )
        return sent_count
    except Exception as e:
        logger.error(f"Error in KPI action notification task: {str(e)}")
        return 0


# スケジューラーに登録する関数のマッピング
scheduler_tasks = {
    "progress_notification_check": run_progress_notification_check,
    "kpi_action_notification": run_kpi_action_notification,
}
