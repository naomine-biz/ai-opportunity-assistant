from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """タイムスタンプ項目を提供するMixin"""

    created_at: datetime = Field(default_factory=datetime.utcnow)


class UUIDMixin(SQLModel):
    """UUID主キーを提供するMixin"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
