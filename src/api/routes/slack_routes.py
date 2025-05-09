from fastapi import APIRouter, Request, Response, Depends, HTTPException
from slack_sdk.signature import SignatureVerifier

from core.config import settings
from core.logger import get_slack_logger
from services.slack_service import handle_slack_verification_challenge, process_slack_event

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
    if event_type == "url_verification":
        logger.info("Received Slack URL verification challenge")
        return await handle_slack_verification_challenge(event_data)

    # イベントコールバックの処理
    if event_type == "event_callback":
        # サービスレイヤーにイベント処理を委譲
        processed = await process_slack_event(event_data)

        # 処理されなかった場合は204
        if not processed:
            return Response(status_code=204)

        # 処理が完了した場合は202（非同期処理）
        return Response(status_code=202)

    # その他のイベントタイプ
    logger.info(f"Unsupported Slack event type: {event_type}")
    return Response(status_code=204)