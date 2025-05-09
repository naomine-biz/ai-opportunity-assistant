"""
アクティビティログ関連APIルート定義
"""

from fastapi import APIRouter, HTTPException, status

from api.schemas import ActivityLogCreate, ActivityLogResponse
from core.logger import get_activity_logger
from services.activity_service import create_activity_log

router = APIRouter()
logger = get_activity_logger()


@router.post(
    "", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED
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
        activity_dict = activity_data.model_dump()
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
