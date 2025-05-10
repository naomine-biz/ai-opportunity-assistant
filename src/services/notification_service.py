"""
通知関連サービス
"""
from datetime import date, timedelta
from typing import Dict, List

from sqlmodel import Session, select

from core.logger import get_notification_logger
from db.session import get_session
from models.entity import ActivityLog, Opportunity, OpportunityUser, User

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
    # 例：最終アクティビティが7日以上前のオポチュニティ
    cutoff_date = target_date - timedelta(days=7)

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
