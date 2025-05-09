"""
オポチュニティ関連APIルート定義
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from api.schemas import (
    OpportunityCreate,
    OpportunityResponse,
    OpportunitySearchResponse,
    OpportunityUpdate,
)
from core.logger import get_opportunity_logger
from services.opportunity_service import (
    create_opportunity,
    delete_opportunity,
    get_opportunity_by_id,
    search_opportunities,
    update_opportunity,
)

router = APIRouter()
logger = get_opportunity_logger()


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
    status_code=status.HTTP_200_OK,
)
async def get_opportunity(opportunity_id: UUID):
    """
    指定されたIDのオポチュニティ詳細を取得

    Args:
        opportunity_id: 取得するオポチュニティのID

    Returns:
        オポチュニティ詳細情報
    """
    try:
        response = await get_opportunity_by_id(opportunity_id)
        logger.info(f"Retrieved opportunity: {opportunity_id}")
        return response
    except ValueError as e:
        logger.warning(f"Error retrieving opportunity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_opportunity_endpoint(opportunity_data: OpportunityCreate):
    """
    新規オポチュニティを作成

    Args:
        opportunity_data: オポチュニティ作成データ

    Returns:
        作成されたオポチュニティのID
    """
    try:
        # Convert Pydantic model to dictionary
        opportunity_dict = opportunity_data.model_dump()
        new_opportunity_id = await create_opportunity(opportunity_dict)
        logger.info(f"Created opportunity: {new_opportunity_id}")
        return {"id": str(new_opportunity_id)}
    except ValueError as e:
        detail = str(e)
        if "not found" in detail:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        logger.warning(f"Error creating opportunity: {detail}")
        raise HTTPException(status_code=status_code, detail=detail)


@router.put("/{opportunity_id}", status_code=status.HTTP_200_OK)
async def update_opportunity_endpoint(
    opportunity_id: UUID,
    update_data: OpportunityUpdate,
):
    """
    オポチュニティ情報を更新

    Args:
        opportunity_id: 更新するオポチュニティのID
        update_data: 更新するフィールドと値

    Returns:
        更新成功レスポンス
    """
    try:
        # Convert Pydantic model to dictionary, excluding None values
        update_dict = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }
        await update_opportunity(opportunity_id, update_dict)
        logger.info(f"Updated opportunity: {opportunity_id}")
        return {"status": "updated"}
    except ValueError as e:
        detail = str(e)
        if "not found" in detail:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        logger.warning(f"Error updating opportunity: {detail}")
        raise HTTPException(status_code=status_code, detail=detail)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity_endpoint(opportunity_id: UUID):
    """
    オポチュニティを削除

    Args:
        opportunity_id: 削除するオポチュニティのID

    Returns:
        削除成功レスポンス
    """
    try:
        await delete_opportunity(opportunity_id)
        logger.info(f"Deleted opportunity: {opportunity_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        logger.warning(f"Error deleting opportunity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )


@router.get(
    "/search",
    response_model=List[OpportunitySearchResponse],
    status_code=status.HTTP_200_OK,
)
async def search_opportunities_endpoint(
    customer_id: Optional[UUID] = None,
    title: Optional[str] = None,
    stage_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    """
    オポチュニティを検索

    Args:
        customer_id: 顧客ID
        title: 案件名（部分一致）
        stage_id: ステージID
        from_date: 予想クロージング日開始
        to_date: 予想クロージング日終了

    Returns:
        検索条件に合致するオポチュニティのリスト
    """
    try:
        result = await search_opportunities(
            customer_id, title, stage_id, from_date, to_date
        )
        logger.info(f"Search opportunities: found {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Error searching opportunities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search opportunities",
        )
