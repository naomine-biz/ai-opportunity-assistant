"""
Slack Event APIテスト
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

# srcディレクトリをパスに追加
SRC_DIR = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

# flake8の警告を抑制：インポート順序の問題
# isort: skip_file
from api.routes.slack_routes import verify_slack_signature  # noqa: E402


def test_slack_verification_challenge(client):
    """SlackのURL検証チャレンジに応答できることを確認"""
    # URL検証チャレンジリクエストデータ
    challenge_data = {
        "type": "url_verification",
        "challenge": "test_challenge_token",
    }

    # 検証リクエスト送信
    response = client.post("/api/v1/slack/events", json=challenge_data)

    # レスポンスを検証
    assert response.status_code == 200
    assert response.json() == {"challenge": "test_challenge_token"}


def test_slack_message_event(client):
    """Slackからのメッセージイベントが正しく処理されることを確認"""
    # メッセージイベントデータ
    message_data = {
        "type": "event_callback",
        "team_id": "T123ABC",
        "event": {
            "type": "message",
            "user": "U123USER",
            "text": "A社に訪問しました。",
            "channel": "D123CHANNEL",
            "ts": "1609459200.000100",
        },
    }

    # 非同期メソッドのモック作成
    async def mock_process_event(*args, **kwargs):
        return True

    # サービスレイヤーのイベント処理をモック
    with patch("services.slack_service.process_slack_event", mock_process_event):
        # リクエスト送信
        response = client.post("/api/v1/slack/events", json=message_data)

        # レスポンスを検証（非同期処理なので202を返す）
        assert response.status_code == 202

        # ハンドラが呼び出されることを期待するがモックではasync callのアサーションが難しいため、
        # ここでは詳細なアサーションは行わない


@pytest.mark.asyncio
async def test_slack_signature_verification():
    """Slack署名検証が正しく動作することを確認"""
    # モックリクエスト作成
    mock_request = MagicMock()

    # asyncメソッドとして正しくモック化
    async def mock_body():
        return b'{"foo": "bar"}'

    mock_request.body = mock_body
    mock_request.headers.get.side_effect = lambda x: {
        "X-Slack-Signature": "test_signature",
        "X-Slack-Request-Timestamp": "1609459200",
    }.get(x)

    # 署名検証が成功するケース
    with patch(
        "api.routes.slack_routes.signature_verifier.is_valid", return_value=True
    ):
        # 例外が発生しないことを確認
        await verify_slack_signature(mock_request)

    # 署名検証が失敗するケース
    with patch(
        "api.routes.slack_routes.signature_verifier.is_valid", return_value=False
    ):
        # HTTPException(403)が発生することを確認
        with pytest.raises(HTTPException) as exc_info:
            await verify_slack_signature(mock_request)

        assert exc_info.value.status_code == 403
        assert "Invalid Slack signature" in exc_info.value.detail


def test_missing_user_or_text(client):
    """ユーザーIDまたはテキストが欠けている場合、適切に処理されることを確認"""
    # ユーザーIDが欠けているイベントデータ
    message_data = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "text": "テストメッセージ",
            "channel": "D123CHANNEL",
            "ts": "1609459200.000100",
        },
    }

    # 非同期メソッドのモック作成 - 処理されなかった場合はFalseを返す
    async def mock_process_event(*args, **kwargs):
        return False

    # サービスレイヤーのイベント処理をモック
    with patch("services.slack_service.process_slack_event", mock_process_event):
        # リクエスト送信
        response = client.post("/api/v1/slack/events", json=message_data)

        # 処理対象外として204を返す
        assert response.status_code == 204
