"""
オポチュニティAPIルートのテスト
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

# モックデータ
SAMPLE_OPPORTUNITY_ID = uuid.uuid4()
CUSTOMER_ID = uuid.uuid4()
STAGE_ID = 2
USER_ID_1 = uuid.uuid4()
USER_ID_2 = uuid.uuid4()


@pytest.fixture
def opportunity_response():
    """オポチュニティ詳細レスポンスのモックデータ"""
    return {
        "id": str(SAMPLE_OPPORTUNITY_ID),
        "customer": {"id": str(CUSTOMER_ID), "name": "株式会社ABC"},
        "title": "Webシステム導入",
        "amount": 5000000,
        "stage": {"id": STAGE_ID, "name": "提案"},
        "expected_close_date": "2024-06-01",
        "owners": [{"id": str(USER_ID_1), "name": "田中太郎"}],
        "collaborators": [{"id": str(USER_ID_2), "name": "佐藤花子"}],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def opportunity_create_data():
    """オポチュニティ作成リクエストのモックデータ"""
    return {
        "customer_id": str(CUSTOMER_ID),
        "title": "新システム導入",
        "amount": 4000000,
        "stage_id": 1,
        "expected_close_date": "2024-07-01",
        "owners": [str(USER_ID_1)],
        "collaborators": [str(USER_ID_2)],
    }


@pytest.fixture
def opportunity_update_data():
    """オポチュニティ更新リクエストのモックデータ"""
    return {"stage_id": 2, "amount": 4500000}


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.get_opportunity_by_id")
async def test_get_opportunity_success(
    mock_get_opportunity, client, opportunity_response
):
    """正常系: オポチュニティ詳細取得テスト"""
    # モックの設定
    mock_get = AsyncMock()
    mock_get.return_value = opportunity_response
    mock_get_opportunity.side_effect = mock_get

    # APIリクエスト実行
    response = client.get(f"/api/v1/opportunity/{SAMPLE_OPPORTUNITY_ID}")

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(SAMPLE_OPPORTUNITY_ID)
    assert data["title"] == "Webシステム導入"
    assert data["amount"] == 5000000
    assert data["stage"]["id"] == STAGE_ID


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.get_opportunity_by_id")
async def test_get_opportunity_not_found(mock_get_opportunity, client):
    """異常系: 存在しないオポチュニティ詳細取得テスト"""
    # モックの設定
    mock_get = AsyncMock()
    mock_get.side_effect = ValueError("Opportunity not found")
    mock_get_opportunity.side_effect = mock_get

    # APIリクエスト実行
    response = client.get(f"/api/v1/opportunity/{SAMPLE_OPPORTUNITY_ID}")

    # レスポンスの検証
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.create_opportunity")
async def test_create_opportunity_success(
    mock_create_opportunity, client, opportunity_create_data
):
    """正常系: オポチュニティ作成テスト"""
    # モックの設定
    mock_create = AsyncMock()
    mock_create.return_value = SAMPLE_OPPORTUNITY_ID
    mock_create_opportunity.side_effect = mock_create

    # APIリクエスト実行
    response = client.post("/api/v1/opportunity", json=opportunity_create_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == str(SAMPLE_OPPORTUNITY_ID)


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.create_opportunity")
async def test_create_opportunity_invalid_data(mock_create_opportunity, client):
    """異常系: 不正なリクエストデータでオポチュニティ作成テスト"""
    # 不完全なデータ（金額が負の値）
    invalid_data = {
        "customer_id": str(CUSTOMER_ID),
        "title": "新システム導入",
        "amount": -100,  # 負の値
        "stage_id": 1,
        "expected_close_date": "2024-07-01",
        "owners": [str(USER_ID_1)],
    }

    # APIリクエスト実行
    response = client.post("/api/v1/opportunity", json=invalid_data)

    # レスポンスの検証
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.update_opportunity")
async def test_update_opportunity_success(
    mock_update_opportunity, client, opportunity_update_data
):
    """正常系: オポチュニティ更新テスト"""
    # モックの設定
    mock_update = AsyncMock()
    mock_update.return_value = True
    mock_update_opportunity.side_effect = mock_update

    # APIリクエスト実行
    response = client.put(
        f"/api/v1/opportunity/{SAMPLE_OPPORTUNITY_ID}", json=opportunity_update_data
    )

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "updated"


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.delete_opportunity")
async def test_delete_opportunity_success(mock_delete_opportunity, client):
    """正常系: オポチュニティ削除テスト"""
    # モックの設定
    mock_delete = AsyncMock()
    mock_delete.return_value = True
    mock_delete_opportunity.side_effect = mock_delete

    # APIリクエスト実行
    response = client.delete(f"/api/v1/opportunity/{SAMPLE_OPPORTUNITY_ID}")

    # レスポンスの検証
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
@patch("api.routes.opportunity_routes.search_opportunities")
async def test_search_opportunities_success(mock_search_opportunities, client):
    """正常系: オポチュニティ検索テスト"""
    # 検索結果のモックデータ
    search_results = [
        {
            "id": str(SAMPLE_OPPORTUNITY_ID),
            "customer": {"id": str(CUSTOMER_ID), "name": "株式会社ABC"},
            "title": "Webシステム導入",
            "amount": 5000000,
            "stage": {"id": STAGE_ID, "name": "提案"},
            "expected_close_date": "2024-06-01",
        },
        {
            "id": str(uuid.uuid4()),
            "customer": {"id": str(CUSTOMER_ID), "name": "株式会社ABC"},
            "title": "クラウド移行",
            "amount": 8000000,
            "stage": {"id": 1, "name": "見込み"},
            "expected_close_date": "2024-07-10",
        },
    ]

    # モックの設定
    mock_search = AsyncMock()
    mock_search.return_value = search_results
    mock_search_opportunities.side_effect = mock_search

    # APIリクエスト実行
    # 検索テスト時はクエリパラメーターなしで呼び出す
    response = client.get("/api/v1/opportunity/search")

    # レスポンスの検証
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Webシステム導入"
    assert data[1]["title"] == "クラウド移行"
