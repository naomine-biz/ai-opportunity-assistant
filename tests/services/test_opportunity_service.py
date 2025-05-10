"""
オポチュニティサービスのテスト
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from models.entity import Customer, Opportunity, User
from models.master import Stage
from services.opportunity_service import (
    create_opportunity,
    delete_opportunity,
    get_opportunity_by_id,
    search_opportunities,
    update_opportunity,
)

# モックデータ
SAMPLE_OPPORTUNITY_ID = uuid.uuid4()
CUSTOMER_ID = uuid.uuid4()
STAGE_ID = 2
USER_ID_1 = uuid.uuid4()
USER_ID_2 = uuid.uuid4()


@pytest.fixture
def mock_opportunity():
    """オポチュニティモック"""
    opportunity = MagicMock()
    opportunity.id = SAMPLE_OPPORTUNITY_ID
    opportunity.customer_id = CUSTOMER_ID
    opportunity.title = "Webシステム導入"
    opportunity.amount = 5000000
    opportunity.stage_id = STAGE_ID
    opportunity.expected_close_date = date(2024, 6, 1)
    opportunity.created_at = datetime.utcnow()
    opportunity.updated_at = datetime.utcnow()
    return opportunity


@pytest.fixture
def mock_customer():
    """顧客モック"""
    customer = MagicMock()
    customer.id = CUSTOMER_ID
    customer.name = "株式会社ABC"
    return customer


@pytest.fixture
def mock_stage():
    """ステージモック"""
    stage = MagicMock()
    stage.id = STAGE_ID
    stage.name = "提案"
    return stage


@pytest.fixture
def mock_users():
    """ユーザーモック"""
    owner = MagicMock()
    owner.id = USER_ID_1
    owner.name = "田中太郎"

    collaborator = MagicMock()
    collaborator.id = USER_ID_2
    collaborator.name = "佐藤花子"

    return {USER_ID_1: owner, USER_ID_2: collaborator}


@pytest.fixture
def mock_opportunity_users():
    """オポチュニティユーザー関連モック"""
    owner_rel = MagicMock()
    owner_rel.opportunity_id = SAMPLE_OPPORTUNITY_ID
    owner_rel.user_id = USER_ID_1
    owner_rel.role = "owner"

    collaborator_rel = MagicMock()
    collaborator_rel.opportunity_id = SAMPLE_OPPORTUNITY_ID
    collaborator_rel.user_id = USER_ID_2
    collaborator_rel.role = "collaborator"

    return [owner_rel, collaborator_rel]


@pytest.fixture
def mock_session(
    mock_opportunity, mock_customer, mock_stage, mock_users, mock_opportunity_users
):
    """セッションモック"""
    session = MagicMock(spec=Session)

    # get メソッドのモック
    def mock_get(model_cls, id_value):
        if model_cls == Opportunity and id_value == SAMPLE_OPPORTUNITY_ID:
            return mock_opportunity
        elif model_cls == Customer and id_value == CUSTOMER_ID:
            return mock_customer
        elif model_cls == Stage and id_value == STAGE_ID:
            return mock_stage
        elif model_cls == User:
            return mock_users.get(id_value)
        return None

    session.get.side_effect = mock_get

    # exec メソッドのモック
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = mock_opportunity_users

    session.exec.return_value = mock_exec_result

    return session


@pytest.mark.asyncio
async def test_get_opportunity_by_id(mock_session):
    """get_opportunity_by_id のテスト"""
    # 関数の実行
    result = await get_opportunity_by_id(SAMPLE_OPPORTUNITY_ID, mock_session)

    # 結果の検証
    assert result["id"] == SAMPLE_OPPORTUNITY_ID
    assert result["title"] == "Webシステム導入"
    assert result["amount"] == 5000000
    assert result["stage"]["id"] == STAGE_ID
    assert result["customer"]["name"] == "株式会社ABC"
    assert len(result["owners"]) == 1
    assert len(result["collaborators"]) == 1
    assert result["owners"][0]["name"] == "田中太郎"


@pytest.mark.asyncio
async def test_get_opportunity_by_id_not_found(mock_session):
    """存在しないオポチュニティの get_opportunity_by_id のテスト"""
    # get メソッドの戻り値を None に変更
    mock_session.get.return_value = None

    # エラーが発生することを検証
    with pytest.raises(ValueError, match="Opportunity not found"):
        await get_opportunity_by_id(uuid.uuid4(), mock_session)


@pytest.mark.asyncio
async def test_create_opportunity(mock_session):
    """create_opportunity のテスト"""
    # 新しく作成するオポチュニティのデータ
    opportunity_data = {
        "customer_id": CUSTOMER_ID,
        "title": "新システム導入",
        "amount": 4000000,
        "stage_id": STAGE_ID,
        "expected_close_date": "2024-07-01",
        "owners": [USER_ID_1],
        "collaborators": [USER_ID_2],
    }

    # モックオポチュニティの設定
    new_opportunity = MagicMock()
    new_opportunity.id = SAMPLE_OPPORTUNITY_ID
    mock_session.add.return_value = None
    mock_session.refresh.side_effect = lambda obj: setattr(
        obj, "id", SAMPLE_OPPORTUNITY_ID
    )

    # 関数の実行（モックパッチを使用して Opportunity クラスをオーバーライド）
    with patch(
        "services.opportunity_service.Opportunity", return_value=new_opportunity
    ):
        result = await create_opportunity(opportunity_data, mock_session)

    # 結果の検証
    assert result == SAMPLE_OPPORTUNITY_ID
    assert (
        mock_session.add.call_count == 3
    )  # オポチュニティ + オーナー + コラボレーター
    assert mock_session.commit.call_count == 2  # add後 + リレーション作成後


@pytest.mark.asyncio
async def test_create_opportunity_missing_required_field(mock_session):
    """必須フィールドが欠けている場合の create_opportunity のテスト"""
    # 不完全なデータ（title が欠けている）
    incomplete_data = {
        "customer_id": CUSTOMER_ID,
        "amount": 4000000,
        "stage_id": STAGE_ID,
        "expected_close_date": "2024-07-01",
        "owners": [USER_ID_1],
    }

    # エラーが発生することを検証
    with pytest.raises(ValueError, match="Missing required field"):
        await create_opportunity(incomplete_data, mock_session)


@pytest.mark.asyncio
async def test_update_opportunity(mock_session, mock_opportunity):
    """update_opportunity のテスト"""
    # 更新データ
    update_data = {"amount": 5500000, "stage_id": 3}

    # 新しいステージモック
    new_stage = MagicMock()
    new_stage.id = 3
    new_stage.name = "商談"

    # get メソッドのモックを更新
    original_side_effect = mock_session.get.side_effect

    def updated_get(model_cls, id_value):
        if model_cls == Stage and id_value == 3:
            return new_stage
        return original_side_effect(model_cls, id_value)

    mock_session.get.side_effect = updated_get

    # 関数の実行
    result = await update_opportunity(SAMPLE_OPPORTUNITY_ID, update_data, mock_session)

    # 結果の検証
    assert result is True
    assert mock_opportunity.amount == 5500000
    assert mock_opportunity.stage_id == 3
    assert mock_session.commit.called


@pytest.mark.asyncio
async def test_delete_opportunity(mock_session, mock_opportunity_users):
    """delete_opportunity のテスト"""
    # 関数の実行
    result = await delete_opportunity(SAMPLE_OPPORTUNITY_ID, mock_session)

    # 結果の検証
    assert result is True
    assert (
        mock_session.delete.call_count == 3
    )  # オポチュニティ + オーナー + コラボレーター
    assert mock_session.commit.called


@pytest.mark.asyncio
async def test_search_opportunities(mock_session):
    """search_opportunities のテスト"""
    # 検索結果のモック
    mock_opportunity1 = MagicMock()
    mock_opportunity1.id = SAMPLE_OPPORTUNITY_ID
    mock_opportunity1.customer_id = CUSTOMER_ID
    mock_opportunity1.title = "Webシステム導入"
    mock_opportunity1.amount = 5000000
    mock_opportunity1.stage_id = STAGE_ID
    mock_opportunity1.expected_close_date = date(2024, 6, 1)

    mock_opportunity2 = MagicMock()
    mock_opportunity2.id = uuid.uuid4()
    mock_opportunity2.customer_id = CUSTOMER_ID
    mock_opportunity2.title = "クラウド移行"
    mock_opportunity2.amount = 8000000
    mock_opportunity2.stage_id = 1
    mock_opportunity2.expected_close_date = date(2024, 7, 10)

    # exec メソッドの戻り値を変更
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = [mock_opportunity1, mock_opportunity2]
    mock_session.exec.return_value = mock_exec_result

    # get メソッドのモックを更新
    original_side_effect = mock_session.get.side_effect

    mock_stage1 = MagicMock()
    mock_stage1.id = 1
    mock_stage1.name = "見込み"

    def updated_get(model_cls, id_value):
        if model_cls == Stage and id_value == 1:
            return mock_stage1
        return original_side_effect(model_cls, id_value)

    mock_session.get.side_effect = updated_get

    # 関数の実行
    result = await search_opportunities(
        customer_id=CUSTOMER_ID,
        title=None,
        stage_id=None,
        from_date=None,
        to_date=None,
        session=mock_session,
    )

    # 結果の検証
    assert len(result) == 2
    assert result[0]["title"] == "Webシステム導入"
    assert result[1]["title"] == "クラウド移行"
    assert result[0]["stage"]["name"] == "提案"
    assert result[1]["stage"]["name"] == "見込み"
