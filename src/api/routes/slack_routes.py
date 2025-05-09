from fastapi import APIRouter, Request, Response, Depends, HTTPException
from slack_sdk.signature import SignatureVerifier

from core.config import settings
from core.logger import get_slack_logger
from slack.handlers import slack_event_handler
from slack.models import EventType

router = APIRouter()
logger = get_slack_logger()

# Slack署名検証用のVerifier
signature_verifier = SignatureVerifier(settings.SLACK_SIGNING_SECRET)


# 署名検証用の依存関数
async def verify_slack_signature(request: Request):
    """
    Slackからのリクエストの署名を検証する

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        検証成功時には何も返さない

    Raises:
        HTTPException: 署名検証失敗時に403を返す
    """
    # リクエストボディを読み込む
    body = await request.body()

    # X-Slack-Signatureヘッダーを取得
    signature = request.headers.get("X-Slack-Signature")

    # X-Slack-Request-Timestampヘッダーを取得
    timestamp = request.headers.get("X-Slack-Request-Timestamp")

    # 署名を検証
    if not signature_verifier.is_valid(
        body=body,
        timestamp=timestamp,
        signature=signature
    ):
        logger.warning(
            "Invalid Slack signature",
            extra={"signature": signature, "timestamp": timestamp}
        )
        raise HTTPException(status_code=403, detail="Invalid Slack signature")


@router.post("/events", dependencies=[Depends(verify_slack_signature)])
async def slack_events(request: Request):
    """
    Slack Event APIエンドポイント

    - URL検証チャレンジに応答
    - Slackイベントを受信して処理
    """
    # リクエストボディをJSONとして解析
    event_data = await request.json()

    # Slackイベントタイプの確認
    event_type = event_data.get("type")

    # URLの検証チャレンジに対応
    if event_type == EventType.URL_VERIFICATION:
        logger.info("Received Slack URL verification challenge")
        challenge = event_data.get("challenge")
        return {"challenge": challenge}

    # イベントコールバックの処理
    if event_type == EventType.EVENT_CALLBACK:
        event = event_data.get("event", {})
        inner_event_type = event.get("type")

        # チャネルメッセージイベントの処理
        if inner_event_type == EventType.MESSAGE:
            user_id = event.get("user")
            text = event.get("text")
            channel = event.get("channel")
            ts = event.get("ts")

            if not user_id or not text:
                logger.warning("Received message event without user or text")
                return Response(status_code=204)  # 処理対象外

            logger.info(
                "Received message from user",
                extra={
                    "user_id": user_id,
                    "channel": channel,
                    "ts": ts,
                    "text_length": len(text) if text else 0
                }
            )

            # バックグラウンドでメッセージ処理
            await slack_event_handler.process_message_event(
                user_id=user_id,
                text=text,
                channel=channel,
                ts=ts,
                event_data=event_data
            )

    # 202 Acceptedを返す（非同期処理を示す）
    return Response(status_code=202)