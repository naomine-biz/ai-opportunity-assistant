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


@pytest.mark.asyncio
@patch("api.routes.notification_routes.check_progress_notifications")
async def test_trigger_progress_notification_success(
    mock_check_progress_notifications,
    client,
    notification_request_data,
    notification_response_data,
):
    """正常系: 進捗通知トリガーテスト"""
    # モックの設定
    mock_check = AsyncMock()
    mock_check.return_value = notification_response_data
    mock_check_progress_notifications.side_effect = mock_check

    # APIリクエスト実行
    response = client.post("/api/v1/notify/progress", json=notification_request_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "completed"
    assert data["target_date"] == notification_request_data["target_date"]
    assert data["notifications_count"] == len(notification_response_data)
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["opportunity_title"] == "Webシステム導入"


@pytest.mark.asyncio
async def test_trigger_progress_notification_invalid_date(client):
    """異常系: 不正な日付形式で進捗通知トリガーテスト"""
    # 不正な日付形式のデータ
    invalid_data = {"target_date": "2024/04/24"}  # 不正な日付形式

    # APIリクエスト実行
    response = client.post("/api/v1/notify/progress", json=invalid_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@patch("api.routes.notification_routes.check_progress_notifications")
async def test_trigger_progress_notification_service_error(
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
