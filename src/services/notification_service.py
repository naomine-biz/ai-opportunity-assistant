"""
通知関連サービス
"""
import uuid
from datetime import date, timedelta
from typing import Dict, List, Optional

from sqlmodel import Session, select

from core.logger import get_notification_logger
from db.session import get_session
from models.entity import ActivityLog, Opportunity, OpportunityUser, User
from slack.bot import slack_bot

logger = get_notification_logger()


async def check_progress_notifications(
    target_date: date, session: Session = None
) -> List[Dict]:
    """
    進捗確認が必要なオポチュニティを特定し通知対象リストを作成

    Args:
        target_date: 基準日
        session: データベースセッション (省略可能)

    Returns:
        通知対象リスト
    """
    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()
    # 進捗確認が必要なオポチュニティを特定
    # 設定から非アクティブ日数を取得
    from core.config import settings

    inactivity_days = settings.NOTIFICATION_INACTIVITY_DAYS
    cutoff_date = target_date - timedelta(days=inactivity_days)

    # 全オポチュニティを取得
    opportunities = session.exec(select(Opportunity)).all()
    notifications_to_send = []

    for opp in opportunities:
        # 最新のアクティビティログを取得
        latest_activity = session.exec(
            select(ActivityLog)
            .where(ActivityLog.opportunity_id == opp.id)
            .order_by(ActivityLog.action_date.desc())
        ).first()

        # アクティビティがない、または最新のアクティビティが古い場合
        if not latest_activity or latest_activity.action_date < cutoff_date:
            # オーナーを取得
            owners = session.exec(
                select(OpportunityUser).where(
                    OpportunityUser.opportunity_id == opp.id,
                    OpportunityUser.role == "owner",
                )
            ).all()

            for owner_relation in owners:
                owner = session.get(User, owner_relation.user_id)

                notifications_to_send.append(
                    {
                        "user_id": owner.id,
                        "slack_id": owner.slack_id,
                        "opportunity_id": opp.id,
                        "opportunity_title": opp.title,
                        "last_activity_date": latest_activity.action_date.isoformat()
                        if latest_activity
                        else "なし",
                    }
                )

    logger.info(
        "Progress notification check completed",
        extra={
            "target_date": target_date.isoformat(),
            "notifications_count": len(notifications_to_send),
        },
    )

    return notifications_to_send


async def send_progress_notifications(notifications: List[Dict]) -> int:
    """
    進捗確認通知をSlackに送信する

    Args:
        notifications: 通知対象リスト（check_progress_notifications関数の戻り値）

    Returns:
        送信成功した通知の数
    """
    success_count = 0

    for notification in notifications:
        user_slack_id = notification.get("slack_id")
        if not user_slack_id:
            logger.warning(
                "Notification skipped: No Slack ID",
                extra={"user_id": str(notification.get("user_id"))},
            )
            continue

        # 通知メッセージを構築
        from core.config import settings

        opportunity_title = notification.get("opportunity_title", "不明な案件")
        inactivity_days = settings.NOTIFICATION_INACTIVITY_DAYS
        message = (
            f"案件「{opportunity_title}」の進捗状況を更新してください。最終活動日から{inactivity_days}日以上経過しています。"
        )

        try:
            # Slack通知を送信
            await slack_bot.send_notification(
                user_slack_id=user_slack_id,
                message=message,
                opportunity_data=notification,
            )
            success_count += 1
            logger.info(
                "Progress notification sent successfully",
                extra={
                    "user_slack_id": user_slack_id,
                    "opportunity_id": str(notification.get("opportunity_id")),
                },
            )
        except Exception as e:
            logger.error(
                "Failed to send progress notification",
                extra={
                    "user_slack_id": user_slack_id,
                    "opportunity_id": str(notification.get("opportunity_id")),
                    "error": str(e),
                },
            )

    return success_count


async def send_kpi_notification(
    user_slack_id: str,
    message: str,
    opportunity_id: Optional[uuid.UUID] = None,
    opportunity_title: Optional[str] = None,
) -> bool:
    """
    KPI達成のためのアクション促進通知を送信する

    Args:
        user_slack_id: 通知先ユーザーのSlack ID
        message: 通知メッセージ
        opportunity_id: 関連する案件ID（オプション）
        opportunity_title: 関連する案件名（オプション）

    Returns:
        送信成功したかどうか
    """
    opportunity_data = None
    if opportunity_id:
        opportunity_data = {
            "opportunity_id": opportunity_id,
            "opportunity_title": opportunity_title or "不明な案件",
        }

    try:
        # Slack通知を送信
        await slack_bot.send_notification(
            user_slack_id=user_slack_id,
            message=message,
            opportunity_data=opportunity_data,
        )
        logger.info(
            "KPI notification sent successfully",
            extra={
                "user_slack_id": user_slack_id,
                "opportunity_id": str(opportunity_id) if opportunity_id else None,
            },
        )
        return True
    except Exception as e:
        logger.error(
            "Failed to send KPI notification",
            extra={
                "user_slack_id": user_slack_id,
                "opportunity_id": str(opportunity_id) if opportunity_id else None,
                "error": str(e),
            },
        )
        return False
