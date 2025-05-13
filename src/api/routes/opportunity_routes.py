"""
オポチュニティ関連APIルート定義

オポチュニティ（営業案件）の作成・更新・検索などのAPIエンドポイントを提供します。
"""

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from src.api.schemas import (
    OpportunityCreate,
    OpportunityResponse,
    OpportunitySearchResponse,
    OpportunityUpdate,
)
from src.core.logger import get_opportunity_logger
from src.services.opportunity_service import (
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
    summary="オポチュニティ詳細取得",
    description="指定されたIDのオポチュニティ詳細情報を取得します。",
    response_description="オポチュニティの詳細情報",
    responses={404: {"description": "指定されたIDのオポチュニティが見つかりません"}},
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="オポチュニティ新規作成",
    description="新規オポチュニティを作成します。顧客ID、案件名、金額、ステージ、予想クロージング日、担当者情報を指定します。",
    response_description="作成されたオポチュニティのID",
    responses={
        201: {
            "description": "オポチュニティが正常に作成されました",
            "content": {
                "application/json": {
                    "example": {"id": "123e4567-e89b-12d3-a456-426614174000"}
                }
            },
        },
        400: {"description": "無効なリクエストデータ"},
        404: {"description": "関連リソース（顧客、ユーザー、ステージなど）が見つかりません"},
    },
)
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
        opportunity_dict = opportunity_data.dict()
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


@router.put(
    "/{opportunity_id}",
    status_code=status.HTTP_200_OK,
    summary="オポチュニティ情報更新",
    description="オポチュニティの情報を更新します。更新したいフィールドのみを指定できます。",
    response_description="更新成功レスポンス",
    responses={
        200: {
            "description": "オポチュニティが正常に更新されました",
            "content": {"application/json": {"example": {"status": "updated"}}},
        },
        400: {"description": "無効な更新データ"},
        404: {"description": "指定されたIDのオポチュニティが見つかりません"},
    },
)
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
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
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


@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="オポチュニティ削除",
    description="指定されたIDのオポチュニティを削除します。",
    response_description="削除成功（コンテンツなし）",
    responses={
        204: {"description": "オポチュニティが正常に削除されました"},
        404: {"description": "指定されたIDのオポチュニティが見つかりません"},
    },
)
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
    "/search/",
    response_model=List[OpportunitySearchResponse],
    status_code=status.HTTP_200_OK,
    summary="オポチュニティ検索",
    description="""
    指定された条件に基づきオポチュニティを検索します。
    複数の検索条件を組み合わせることで、柔軟な検索が可能です。
    すべての検索条件はオプショナルです。
    """,
    response_description="検索条件に合致するオポチュニティのリスト",
    responses={
        200: {
            "description": "検索結果",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "customer": {
                                "id": "123e4567-e89b-12d3-a456-426614174001",
                                "name": "サンプル顧客株式会社",
                            },
                            "title": "システム提案案件",
                            "amount": 1000000,
                            "stage": {"id": 2, "name": "提案中"},
                            "expected_close_date": "2025-06-30",
                        }
                    ]
                }
            },
        },
        500: {"description": "検索処理に失敗しました"},
    },
)
async def search_opportunities_endpoint(
    customer_id: Optional[UUID] = None,
    title: Optional[str] = None,
    stage_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    min_amount: Optional[int] = None,  # 金額下限（任意）
    max_amount: Optional[int] = None,  # 金額上限（任意）
):
    """
    オポチュニティを検索

    Args:
        customer_id: 顧客ID
        title: 案件名（部分一致）
        stage_id: ステージID
        from_date: 予想クロージング日開始
        to_date: 予想クロージング日終了
        min_amount: 金額下限（任意）
        max_amount: 金額上限（任意）

    Returns:
        検索条件に合致するオポチュニティのリスト
    """
    try:
        result = await search_opportunities(
            customer_id, title, stage_id, from_date, to_date, min_amount, max_amount
        )
        logger.info(f"Search opportunities: found {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Error searching opportunities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search opportunities",
        )
