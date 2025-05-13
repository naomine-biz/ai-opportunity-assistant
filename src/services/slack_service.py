"""
Slackサービスモジュール - API層とSlack処理モジュールの橋渡し
"""

from typing import Any, Dict

from src.core.logger import get_slack_logger
from src.slack.handlers import slack_event_handler

logger = get_slack_logger()


# イベントタイプ定数
class EventType:
    URL_VERIFICATION = "url_verification"
    EVENT_CALLBACK = "event_callback"
    MESSAGE = "message"


async def handle_slack_verification_challenge(
    event_data: Dict[str, Any],
) -> Dict[str, str]:
    """
    Slack URL検証チャレンジを処理する

    Args:
        event_data: チャレンジデータを含むイベントデータ

    Returns:
        チャレンジトークンを含むレスポンス
    """
    logger.info("Handling Slack URL verification challenge")
    challenge = event_data.get("challenge")
    return {"challenge": challenge}


async def process_slack_event(event_data: Dict[str, Any]) -> bool:
    """
    Slackイベントを処理する

    Args:
        event_data: Slackから受信したイベントデータ

    Returns:
        処理が成功したかどうか
    """
    event = event_data.get("event", {})
    event_type = event.get("type")

    # メッセージイベントの処理
    if event_type == EventType.MESSAGE:
        user_id = event.get("user")
        text = event.get("text")
        channel = event.get("channel")
        ts = event.get("ts")

        if not user_id or not text:
            logger.warning("Received message event without user or text")
            return False

        logger.info(
            "Processing message through service layer",
            extra={
                "user_id": user_id,
                "channel": channel,
                "ts": ts,
                "text_length": len(text) if text else 0,
            },
        )

        # Slackハンドラにイベント処理を委譲
        await slack_event_handler.process_message_event(
            user_id=user_id, text=text, channel=channel, ts=ts, event_data=event_data
        )
        return True

    # 未対応のイベントタイプ
    logger.info(f"Unsupported inner event type: {event_type}")
    return False
