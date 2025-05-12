"""
APIスキーマ定義
リクエスト/レスポンスの検証と型定義
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    """顧客の基本情報"""

    id: UUID
    name: str


class UserBase(BaseModel):
    """ユーザーの基本情報"""

    id: UUID
    name: str


class StageBase(BaseModel):
    """ステージの基本情報"""

    id: int
    name: str


class OpportunityCreate(BaseModel):
    """オポチュニティ作成リクエスト"""

    customer_id: UUID
    title: str
    amount: float = Field(gt=0)
    stage_id: int
    expected_close_date: date
    owners: List[UUID]
    collaborators: Optional[List[UUID]] = []


class OpportunityUpdate(BaseModel):
    """オポチュニティ更新リクエスト"""

    title: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    stage_id: Optional[int] = None
    expected_close_date: Optional[date] = None


class OpportunityResponse(BaseModel):
    """オポチュニティ詳細レスポンス"""

    id: UUID
    customer: CustomerBase
    title: str
    amount: float
    stage: StageBase
    expected_close_date: date
    owners: List[UserBase]
    collaborators: List[UserBase]
    created_at: datetime
    updated_at: datetime


class OpportunitySearchResponse(BaseModel):
    """オポチュニティ検索結果レスポンス"""

    id: UUID
    customer: CustomerBase
    title: str
    amount: float
    stage: StageBase
    expected_close_date: date


class ActivityLogCreate(BaseModel):
    """アクティビティログ作成リクエスト"""

    opportunity_id: UUID
    user_id: UUID
    activity_type_id: int
    action_date: date
    comment: Optional[str] = ""


class ActivityLogResponse(BaseModel):
    """アクティビティログ作成レスポンス"""

    id: UUID


class NotificationRequest(BaseModel):
    """通知リクエスト"""

    target_date: date


class NotificationRecipient(BaseModel):
    """通知対象者情報"""

    user_id: UUID
    slack_id: str
    opportunity_id: UUID
    opportunity_title: str
    last_activity_date: str


class NotificationResponse(BaseModel):
    """通知処理結果レスポンス"""

    status: str
    target_date: date
    notifications_count: int
    notifications_sent: int
    notifications: List[NotificationRecipient]
