from typing import Optional

from sqlmodel import Field, SQLModel

from src.models.base import TimestampMixin


class Stage(TimestampMixin, SQLModel, table=True):
    """案件ステージマスタ"""

    __tablename__ = "stage"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    order_no: int
    is_active: bool = Field(default=True)


class ActivityType(TimestampMixin, SQLModel, table=True):
    """アクティビティ種別マスタ"""

    __tablename__ = "activity_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    is_active: bool = Field(default=True)
