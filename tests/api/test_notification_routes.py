"""
通知APIルートのテスト
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

# モックデータ
OPPORTUNITY_ID = uuid.uuid4()
USER_ID = uuid.uuid4()


@pytest.fixture
def notification_request_data():
    """通知リクエストのモックデータ"""
    return {"target_date": "2024-04-24"}


@pytest.fixture
def notification_response_data():
    """通知レスポンスのモックデータ"""
    return [
        {
            "user_id": str(USER_ID),
            "slack_id": "U12345678",
            "opportunity_id": str(OPPORTUNITY_ID),
            "opportunity_title": "Webシステム導入",
            "last_activity_date": "2024-04-10",
        }
    ]


@pytest.fixture
def kpi_notification_request_data():
    """KPI通知リクエストのモックデータ"""
    return {
        "user_slack_id": "U12345678",
        "message": "KPIテスト通知",
        "opportunity_id": str(OPPORTUNITY_ID),
        "opportunity_title": "Webシステム導入",
    }


@pytest.mark.asyncio
@patch("api.routes.notification_routes.check_progress_notifications")
@patch("api.routes.notification_routes.send_progress_notifications")
async def test_send_progress_notification_success(
    mock_send_progress_notifications,
    mock_check_progress_notifications,
    client,
    notification_request_data,
    notification_response_data,
):
    """正常系: 進捗通知送信テスト"""
    # モックの設定
    mock_check = AsyncMock()
    mock_check.return_value = notification_response_data
    mock_check_progress_notifications.side_effect = mock_check

    mock_send = AsyncMock()
    mock_send.return_value = 1  # 1件送信成功
    mock_send_progress_notifications.side_effect = mock_send

    # APIリクエスト実行
    response = client.post("/api/v1/notify/progress", json=notification_request_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "completed"
    assert data["target_date"] == notification_request_data["target_date"]
    assert data["notifications_count"] == len(notification_response_data)
    assert data["notifications_sent"] == 1
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["opportunity_title"] == "Webシステム導入"

    # モックの呼び出しを検証
    mock_check_progress_notifications.assert_called_once()
    mock_send_progress_notifications.assert_called_once_with(notification_response_data)


@pytest.mark.asyncio
async def test_send_progress_notification_invalid_date(client):
    """異常系: 不正な日付形式で進捗通知送信テスト"""
    # 不正な日付形式のデータ
    invalid_data = {"target_date": "2024/04/24"}  # 不正な日付形式

    # APIリクエスト実行
    response = client.post("/api/v1/notify/progress", json=invalid_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@patch("api.routes.notification_routes.check_progress_notifications")
async def test_send_progress_notification_service_error(
    mock_check_progress_notifications, client, notification_request_data
):
    """異常系: サービス層でエラー発生時のテスト"""
    # モックの設定
    mock_check = AsyncMock()
    mock_check.side_effect = Exception("Database connection error")
    mock_check_progress_notifications.side_effect = mock_check

    # APIリクエスト実行
    response = client.post("/api/v1/notify/progress", json=notification_request_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "error" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("api.routes.notification_routes.send_kpi_notification")
async def test_send_kpi_action_notification_success(
    mock_send_kpi_notification, client, kpi_notification_request_data
):
    """正常系: KPI通知送信テスト"""
    # モックの設定
    mock_send = AsyncMock()
    mock_send.return_value = True  # 送信成功
    mock_send_kpi_notification.side_effect = mock_send

    # APIリクエスト実行
    response = client.post("/api/v1/notify/kpi", json=kpi_notification_request_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "completed"
    assert data["success"] is True
    assert data["user_slack_id"] == kpi_notification_request_data["user_slack_id"]

    # モックの呼び出しを検証
    mock_send_kpi_notification.assert_called_once()
    args = mock_send_kpi_notification.call_args[1]
    assert args["user_slack_id"] == kpi_notification_request_data["user_slack_id"]
    assert args["message"] == kpi_notification_request_data["message"]
    assert (
        str(args["opportunity_id"]) == kpi_notification_request_data["opportunity_id"]
    )
    assert (
        args["opportunity_title"] == kpi_notification_request_data["opportunity_title"]
    )


@pytest.mark.asyncio
@patch("api.routes.notification_routes.send_kpi_notification")
async def test_send_kpi_action_notification_failure(
    mock_send_kpi_notification, client, kpi_notification_request_data
):
    """異常系: KPI通知送信失敗テスト"""
    # モックの設定
    mock_send = AsyncMock()
    mock_send.return_value = False  # 送信失敗
    mock_send_kpi_notification.side_effect = mock_send

    # APIリクエスト実行
    response = client.post("/api/v1/notify/kpi", json=kpi_notification_request_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "failed"
    assert data["success"] is False


@pytest.mark.asyncio
async def test_send_kpi_action_notification_invalid_input(client):
    """異常系: 不正なリクエストデータでKPI通知送信テスト"""
    # 必須パラメータを欠くデータ
    invalid_data = {
        # user_slack_idが欠けている
        "message": "テストメッセージ"
    }

    # APIリクエスト実行
    response = client.post("/api/v1/notify/kpi", json=invalid_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@patch("api.routes.notification_routes.send_kpi_notification")
async def test_send_kpi_action_notification_service_error(
    mock_send_kpi_notification, client, kpi_notification_request_data
):
    """異常系: サービス層でエラー発生時のテスト"""
    # モックの設定
    mock_send = AsyncMock()
    mock_send.side_effect = Exception("Slack API error")
    mock_send_kpi_notification.side_effect = mock_send

    # APIリクエスト実行
    response = client.post("/api/v1/notify/kpi", json=kpi_notification_request_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "error" in response.json()["detail"].lower()
