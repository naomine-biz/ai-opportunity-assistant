"""
アクティビティサービスのテスト
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from models.entity import Opportunity, User
from models.master import ActivityType
from services.activity_service import create_activity_log

# モックデータ
SAMPLE_ACTIVITY_ID = uuid.uuid4()
OPPORTUNITY_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
ACTIVITY_TYPE_ID = 1


@pytest.fixture
def mock_opportunity():
    """オポチュニティモック"""
    opportunity = MagicMock()
    opportunity.id = OPPORTUNITY_ID
    return opportunity


@pytest.fixture
def mock_user():
    """ユーザーモック"""
    user = MagicMock()
    user.id = USER_ID
    user.name = "田中太郎"
    return user


@pytest.fixture
def mock_activity_type():
    """アクティビティタイプモック"""
    activity_type = MagicMock()
    activity_type.id = ACTIVITY_TYPE_ID
    activity_type.name = "顧客訪問"
    return activity_type


@pytest.fixture
def mock_session(mock_opportunity, mock_user, mock_activity_type):
    """セッションモック"""
    session = MagicMock(spec=Session)

    # get メソッドのモック
    def mock_get(model_cls, id_value):
        if model_cls == Opportunity and id_value == OPPORTUNITY_ID:
            return mock_opportunity
        elif model_cls == User and id_value == USER_ID:
            return mock_user
        elif model_cls == ActivityType and id_value == ACTIVITY_TYPE_ID:
            return mock_activity_type
        return None

    session.get.side_effect = mock_get
    return session


@pytest.mark.asyncio
async def test_create_activity_log(mock_session):
    """create_activity_log のテスト"""
    # アクティビティログデータ
    activity_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        "activity_type_id": ACTIVITY_TYPE_ID,
        "action_date": "2024-04-24",
        "comment": "A社訪問済み",
    }

    # モックアクティビティログの設定
    new_activity_log = MagicMock()
    new_activity_log.id = SAMPLE_ACTIVITY_ID
    mock_session.add.return_value = None
    mock_session.refresh.side_effect = lambda obj: setattr(
        obj, "id", SAMPLE_ACTIVITY_ID
    )

    # 関数の実行
    with patch("services.activity_service.ActivityLog", return_value=new_activity_log):
        result = await create_activity_log(activity_data, mock_session)

    # 結果の検証
    assert result == SAMPLE_ACTIVITY_ID
    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called


@pytest.mark.asyncio
async def test_create_activity_log_missing_required_field(mock_session):
    """必須フィールドが欠けている場合の create_activity_log のテスト"""
    # 不完全なデータ（action_date が欠けている）
    incomplete_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        "activity_type_id": ACTIVITY_TYPE_ID,
        # "action_date" が欠けている
        "comment": "A社訪問済み",
    }

    # エラーが発生することを検証
    with pytest.raises(ValueError, match="Missing required field"):
        await create_activity_log(incomplete_data, mock_session)


@pytest.mark.asyncio
async def test_create_activity_log_opportunity_not_found(mock_session):
    """存在しないオポチュニティに対する create_activity_log のテスト"""
    # アクティビティログデータ
    activity_data = {
        "opportunity_id": str(uuid.uuid4()),  # 存在しないオポチュニティID
        "user_id": str(USER_ID),
        "activity_type_id": ACTIVITY_TYPE_ID,
        "action_date": "2024-04-24",
        "comment": "A社訪問済み",
    }

    # get メソッドの戻り値を変更
    original_side_effect = mock_session.get.side_effect

    def updated_get(model_cls, id_value):
        if model_cls == Opportunity:
            return None  # オポチュニティが見つからない
        return original_side_effect(model_cls, id_value)

    mock_session.get.side_effect = updated_get

    # エラーが発生することを検証
    with pytest.raises(ValueError, match="Opportunity not found"):
        await create_activity_log(activity_data, mock_session)


@pytest.mark.asyncio
async def test_create_activity_log_user_not_found(mock_session):
    """存在しないユーザーに対する create_activity_log のテスト"""
    # アクティビティログデータ
    activity_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(uuid.uuid4()),  # 存在しないユーザーID
        "activity_type_id": ACTIVITY_TYPE_ID,
        "action_date": "2024-04-24",
        "comment": "A社訪問済み",
    }

    # get メソッドの戻り値を変更
    original_side_effect = mock_session.get.side_effect

    def updated_get(model_cls, id_value):
        if model_cls == User:
            return None  # ユーザーが見つからない
        return original_side_effect(model_cls, id_value)

    mock_session.get.side_effect = updated_get

    # エラーが発生することを検証
    with pytest.raises(ValueError, match="User not found"):
        await create_activity_log(activity_data, mock_session)


@pytest.mark.asyncio
async def test_create_activity_log_activity_type_not_found(mock_session):
    """存在しないアクティビティタイプに対する create_activity_log のテスト"""
    # アクティビティログデータ
    activity_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        "activity_type_id": 999,  # 存在しないアクティビティタイプID
        "action_date": "2024-04-24",
        "comment": "A社訪問済み",
    }

    # get メソッドの戻り値を変更
    original_side_effect = mock_session.get.side_effect

    def updated_get(model_cls, id_value):
        if model_cls == ActivityType:
            return None  # アクティビティタイプが見つからない
        return original_side_effect(model_cls, id_value)

    mock_session.get.side_effect = updated_get

    # エラーが発生することを検証
    with pytest.raises(ValueError, match="Activity type not found"):
        await create_activity_log(activity_data, mock_session)


@pytest.mark.asyncio
async def test_create_activity_log_optional_comment(mock_session):
    """コメント（任意項目）がない場合の create_activity_log のテスト"""
    # コメントがないアクティビティログデータ
    activity_data = {
        "opportunity_id": str(OPPORTUNITY_ID),
        "user_id": str(USER_ID),
        "activity_type_id": ACTIVITY_TYPE_ID,
        "action_date": "2024-04-24",
        # "comment" は省略
    }

    # モックアクティビティログの設定
    new_activity_log = MagicMock()
    new_activity_log.id = SAMPLE_ACTIVITY_ID
    mock_session.add.return_value = None
    mock_session.refresh.side_effect = lambda obj: setattr(
        obj, "id", SAMPLE_ACTIVITY_ID
    )

    # 関数の実行
    with patch("services.activity_service.ActivityLog", return_value=new_activity_log):
        result = await create_activity_log(activity_data, mock_session)

    # 結果の検証
    assert result == SAMPLE_ACTIVITY_ID
    assert mock_session.add.called
    assert mock_session.commit.called
