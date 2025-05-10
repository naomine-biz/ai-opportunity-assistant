"""
アクティビティログ関連サービス
"""

from datetime import date
from uuid import UUID

from sqlmodel import Session

from core.logger import get_activity_logger
from db.session import get_session
from models.entity import ActivityLog, Opportunity, User
from models.master import ActivityType

logger = get_activity_logger()


async def create_activity_log(activity_data: dict, session: Session = None) -> UUID:
    """
    アクティビティログを記録

    Args:
        activity_data: アクティビティログデータ
        session: データベースセッション (省略可能)

    Returns:
        作成されたアクティビティログのID

    Raises:
        ValueError: 必須フィールドがない、または参照先が存在しない場合
    """
    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()
    # 必須フィールドを確認
    required_fields = [
        "opportunity_id",
        "user_id",
        "activity_type_id",
        "action_date",
    ]
    for field in required_fields:
        if field not in activity_data:
            logger.warning(f"Missing required field: {field}")
            raise ValueError(f"Missing required field: {field}")

    # オポチュニティが存在するか確認
    opportunity_id = UUID(activity_data["opportunity_id"]) if isinstance(activity_data["opportunity_id"], str) else activity_data["opportunity_id"]
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        logger.warning(f"Opportunity not found: {activity_data['opportunity_id']}")
        raise ValueError(f"Opportunity not found: {activity_data['opportunity_id']}")

    # ユーザーが存在するか確認
    user_id = UUID(activity_data["user_id"]) if isinstance(activity_data["user_id"], str) else activity_data["user_id"]
    user = session.get(User, user_id)
    if not user:
        logger.warning(f"User not found: {activity_data['user_id']}")
        raise ValueError(f"User not found: {activity_data['user_id']}")

    # アクティビティタイプが存在するか確認
    activity_type = session.get(ActivityType, activity_data["activity_type_id"])
    if not activity_type:
        logger.warning(f"Activity type not found: {activity_data['activity_type_id']}")
        raise ValueError(
            f"Activity type not found: {activity_data['activity_type_id']}"
        )

    # アクティビティログを作成
    new_activity = ActivityLog(
        opportunity_id=opportunity_id,  # 既に変換済みの値を使用
        user_id=user_id,  # 既に変換済みの値を使用
        activity_type_id=activity_data["activity_type_id"],
        action_date=date.fromisoformat(activity_data["action_date"]),
        comment=activity_data.get("comment", ""),  # コメントはオプション
    )

    session.add(new_activity)
    session.commit()
    session.refresh(new_activity)

    logger.info(
        f"Created activity log: {new_activity.id}",
        extra={
            "opportunity_id": str(new_activity.opportunity_id),
            "user_id": str(new_activity.user_id),
            "activity_type_id": new_activity.activity_type_id,
        },
    )

    return new_activity.id
