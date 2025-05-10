"""
アクティビティログAPIルートのテスト
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

# モックデータ
SAMPLE_ACTIVITY_ID = uuid.uuid4()
OPPORTUNITY_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
ACTIVITY_TYPE_ID = 1


@pytest.fixture
def activity_log_create_data():
    """アクティビティログ作成リクエストのモックデータ"""
    return {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        "activity_type_id": ACTIVITY_TYPE_ID,
        "action_date": "2024-04-24",
        "comment": "A社訪問済み",
    }


@pytest.mark.asyncio
@patch("api.routes.activity_routes.create_activity_log")
async def test_create_activity_log_success(
    mock_create_activity_log, client, activity_log_create_data
):
    """正常系: アクティビティログ作成テスト"""
    # モックの設定
    mock_create = AsyncMock()
    mock_create.return_value = SAMPLE_ACTIVITY_ID
    mock_create_activity_log.side_effect = mock_create

    # APIリクエスト実行
    response = client.post("/api/v1/activity_log", json=activity_log_create_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert uuid.UUID(data["id"])  # UUIDとして解析できることを確認


@pytest.mark.asyncio
@patch("api.routes.activity_routes.create_activity_log")
async def test_create_activity_log_invalid_data(mock_create_activity_log, client):
    """異常系: 不正なリクエストデータでアクティビティログ作成テスト"""
    # 不完全なデータ（必須フィールド不足）
    invalid_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        # activity_type_id が欠けている
        "action_date": "2024-04-24",
    }

    # APIリクエスト実行
    response = client.post("/api/v1/activity_log", json=invalid_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@patch("api.routes.activity_routes.create_activity_log")
async def test_create_activity_log_opportunity_not_found(
    mock_create_activity_log, client, activity_log_create_data
):
    """異常系: 存在しないオポチュニティに対するアクティビティログ作成テスト"""
    # モックの設定
    mock_create = AsyncMock()
    mock_create.side_effect = ValueError("Opportunity not found")
    mock_create_activity_log.side_effect = mock_create

    # APIリクエスト実行
    response = client.post("/api/v1/activity_log", json=activity_log_create_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("api.routes.activity_routes.create_activity_log")
async def test_create_activity_log_user_not_found(
    mock_create_activity_log, client, activity_log_create_data
):
    """異常系: 存在しないユーザーに対するアクティビティログ作成テスト"""
    # モックの設定
    mock_create = AsyncMock()
    mock_create.side_effect = ValueError("User not found")
    mock_create_activity_log.side_effect = mock_create

    # APIリクエスト実行
    response = client.post("/api/v1/activity_log", json=activity_log_create_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("api.routes.activity_routes.create_activity_log")
async def test_create_activity_log_activity_type_not_found(
    mock_create_activity_log, client, activity_log_create_data
):
    """異常系: 存在しないアクティビティタイプに対するアクティビティログ作成テスト"""
    # モックの設定
    mock_create = AsyncMock()
    mock_create.side_effect = ValueError("Activity type not found")
    mock_create_activity_log.side_effect = mock_create

    # APIリクエスト実行
    response = client.post("/api/v1/activity_log", json=activity_log_create_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("api.routes.activity_routes.create_activity_log")
async def test_create_activity_log_invalid_date(mock_create_activity_log, client):
    """異常系: 不正な日付形式でアクティビティログ作成テスト"""
    # 不正な日付形式のデータ
    invalid_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        "activity_type_id": ACTIVITY_TYPE_ID,
        "action_date": "2024/04/24",  # 不正な日付形式
        "comment": "A社訪問済み",
    }

    # APIリクエスト実行
    response = client.post("/api/v1/activity_log", json=invalid_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
