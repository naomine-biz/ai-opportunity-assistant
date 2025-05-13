"""
アクティビティログ関連APIルート定義

営業活動の記録を管理するためのエンドポイントを提供します。
営業担当者による顧客訪問、電話、メール等の活動履歴を記録します。
"""

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import ActivityLogCreate, ActivityLogResponse
from src.core.logger import get_activity_logger
from src.services.activity_service import create_activity_log

router = APIRouter()
logger = get_activity_logger()


@router.post(
    "",
    response_model=ActivityLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="アクティビティログ新規作成",
    description="営業活動の記録を新規に作成します。オポチュニティID、ユーザーID、活動種別、実施日などを指定します。",
    response_description="作成されたアクティビティログのID",
    responses={
        201: {
            "description": "アクティビティログが正常に作成されました",
            "content": {
                "application/json": {
                    "example": {"id": "123e4567-e89b-12d3-a456-426614174000"}
                }
            },
        },
        400: {"description": "無効なリクエストデータ"},
        404: {"description": "関連リソース（オポチュニティ、ユーザー、活動種別など）が見つかりません"},
    },
)
async def create_activity_log_endpoint(activity_data: ActivityLogCreate):
    """
    アクティビティログを記録

    Args:
        activity_data: アクティビティログデータ

    Returns:
        作成されたアクティビティログのID
    """
    try:
        # Convert Pydantic model to dictionary
        activity_dict = activity_data.dict()
        new_activity_id = await create_activity_log(activity_dict)

        logger.info(
            f"Created activity log: {new_activity_id}",
            extra={
                "opportunity_id": str(activity_data.opportunity_id),
                "user_id": str(activity_data.user_id),
                "activity_type_id": activity_data.activity_type_id,
            },
        )

        return {"id": new_activity_id}
    except ValueError as e:
        detail = str(e)
        if "not found" in detail:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        logger.warning(f"Error creating activity log: {detail}")
        raise HTTPException(status_code=status_code, detail=detail)
