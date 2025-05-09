from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Slackイベントタイプ"""

    URL_VERIFICATION = "url_verification"
    EVENT_CALLBACK = "event_callback"
    APP_MENTION = "app_mention"
    MESSAGE = "message"


class SlackUser(BaseModel):
    """Slackユーザー情報"""

    id: str
    name: Optional[str] = None
    real_name: Optional[str] = None


class SlackMessageEvent(BaseModel):
    """Slackメッセージイベント"""

    type: str
    user: str
    text: str
    channel: str
    ts: str
    event_ts: Optional[str] = None
    channel_type: Optional[str] = None


class SlackEventPayload(BaseModel):
    """Slack Event API からのペイロード基本構造"""

    type: EventType
    token: Optional[str] = None
    challenge: Optional[str] = None
    team_id: Optional[str] = None
    api_app_id: Optional[str] = None
    event: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    event_time: Optional[int] = None

    class Config:
        use_enum_values = True


class SlackVerificationSchema(BaseModel):
    """URL検証チャレンジスキーマ"""

    type: str = Field(..., const=True, pattern="^url_verification$")
    challenge: str
    token: str
