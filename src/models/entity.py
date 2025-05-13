from datetime import date, datetime
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.models.base import TimestampMixin, UUIDMixin
from src.models.master import ActivityType, Stage


class User(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """営業担当者"""

    __tablename__ = "user"

    name: str
    email: str = Field(unique=True)
    slack_id: str = Field(unique=True)

    # リレーションシップ
    opportunities: list["OpportunityUser"] = Relationship(back_populates="user")
    activities: list["ActivityLog"] = Relationship(back_populates="user")


class Customer(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """顧客マスタ"""

    __tablename__ = "customer"

    name: str = Field(index=True)
    industry: str

    # リレーションシップ
    opportunities: list["Opportunity"] = Relationship(back_populates="customer")


class Opportunity(UUIDMixin, SQLModel, table=True):
    """オポチュニティ（案件）"""

    __tablename__ = "opportunity"

    customer_id: UUID = Field(foreign_key="customer.id")
    title: str
    amount: float
    stage_id: int = Field(foreign_key="stage.id")
    expected_close_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # リレーションシップ
    customer: Customer = Relationship(back_populates="opportunities")
    stage: Stage = Relationship()
    users: list["OpportunityUser"] = Relationship(back_populates="opportunity")
    activity_logs: list["ActivityLog"] = Relationship(back_populates="opportunity")


class OpportunityUser(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """オポチュニティ担当者（中間テーブル）"""

    __tablename__ = "opportunity_user"

    opportunity_id: UUID = Field(foreign_key="opportunity.id")
    user_id: UUID = Field(foreign_key="user.id")
    role: str  # "owner" or "collaborator"

    # リレーションシップ
    opportunity: Opportunity = Relationship(back_populates="users")
    user: User = Relationship(back_populates="opportunities")


class ActivityLog(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """アクティビティログ"""

    __tablename__ = "activity_log"

    opportunity_id: UUID = Field(foreign_key="opportunity.id")
    user_id: UUID = Field(foreign_key="user.id")
    activity_type_id: int = Field(foreign_key="activity_type.id")
    action_date: date
    comment: str

    # リレーションシップ
    opportunity: Opportunity = Relationship(back_populates="activity_logs")
    user: User = Relationship(back_populates="activities")
    activity_type: ActivityType = Relationship()
