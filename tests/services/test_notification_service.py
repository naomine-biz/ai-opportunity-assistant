"""
通知サービスのテスト
"""

import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from sqlmodel.sql.expression import SelectOfScalar

from models.entity import User
from services.notification_service import check_progress_notifications

# モックデータ
OPPORTUNITY_ID_1 = uuid.uuid4()
OPPORTUNITY_ID_2 = uuid.uuid4()
USER_ID_1 = uuid.uuid4()
USER_ID_2 = uuid.uuid4()
TODAY = date.today()
OLD_DATE = TODAY - timedelta(days=10)
RECENT_DATE = TODAY - timedelta(days=3)


@pytest.fixture
def mock_opportunities():
    """オポチュニティのモックリスト"""
    opportunity1 = MagicMock()
    opportunity1.id = OPPORTUNITY_ID_1
    opportunity1.title = "古いアクティビティのオポチュニティ"

    opportunity2 = MagicMock()
    opportunity2.id = OPPORTUNITY_ID_2
    opportunity2.title = "最近のアクティビティのオポチュニティ"

    return [opportunity1, opportunity2]


@pytest.fixture
def mock_activities():
    """アクティビティログのモックリスト"""
    # オポチュニティ1の古いアクティビティ
    activity1 = MagicMock()
    activity1.opportunity_id = OPPORTUNITY_ID_1
    activity1.action_date = OLD_DATE  # 7日以上前

    # オポチュニティ2の最近のアクティビティ
    activity2 = MagicMock()
    activity2.opportunity_id = OPPORTUNITY_ID_2
    activity2.action_date = RECENT_DATE  # 7日以内

    return {OPPORTUNITY_ID_1: activity1, OPPORTUNITY_ID_2: activity2}


@pytest.fixture
def mock_owner_relations():
    """オーナー関係のモックリスト"""
    # オポチュニティ1のオーナー関係
    owner_rel1 = MagicMock()
    owner_rel1.opportunity_id = OPPORTUNITY_ID_1
    owner_rel1.user_id = USER_ID_1
    owner_rel1.role = "owner"

    # オポチュニティ2のオーナー関係
    owner_rel2 = MagicMock()
    owner_rel2.opportunity_id = OPPORTUNITY_ID_2
    owner_rel2.user_id = USER_ID_2
    owner_rel2.role = "owner"

    return {OPPORTUNITY_ID_1: owner_rel1, OPPORTUNITY_ID_2: owner_rel2}


@pytest.fixture
def mock_users():
    """ユーザーモック"""
    user1 = MagicMock()
    user1.id = USER_ID_1
    user1.name = "田中太郎"
    user1.slack_id = "U12345678"

    user2 = MagicMock()
    user2.id = USER_ID_2
    user2.name = "佐藤花子"
    user2.slack_id = "U87654321"

    return {USER_ID_1: user1, USER_ID_2: user2}


@pytest.fixture
def mock_session(mock_opportunities, mock_activities, mock_owner_relations, mock_users):
    """セッションモック"""
    session = MagicMock()

    # get メソッドのモック
    def mock_get(model_cls, id_value):
        if model_cls == User:
            return mock_users.get(id_value)
        return None

    session.get.side_effect = mock_get

    # exec メソッドのモック
    def mock_exec(query):
        if isinstance(query, SelectOfScalar):
            # オーナー関係を取得するクエリ
            if str(query).find("FROM opportunity_user") > -1:
                params = query.compile().params
                if OPPORTUNITY_ID_1 == params.get("opportunity_id_1", ""):
                    return MagicMock(
                        all=lambda: [mock_owner_relations.get(OPPORTUNITY_ID_1)]
                    )
                elif OPPORTUNITY_ID_2 == params.get("opportunity_id_1", ""):
                    return MagicMock(
                        all=lambda: [mock_owner_relations.get(OPPORTUNITY_ID_2)]
                    )
                return MagicMock(all=lambda: [])

            # オポチュニティを取得するクエリ
            if str(query).find("FROM opportunity") > -1:
                return MagicMock(all=lambda: mock_opportunities)

            # アクティビティログを取得するクエリ
            if str(query).find("FROM activity_log") > -1:
                # クエリに含まれるオポチュニティIDを取得
                params = query.compile().params
                if OPPORTUNITY_ID_1 == params.get("opportunity_id_1", ""):
                    return MagicMock(
                        first=lambda: mock_activities.get(OPPORTUNITY_ID_1)
                    )
                elif OPPORTUNITY_ID_2 == params.get("opportunity_id_1", ""):
                    return MagicMock(
                        first=lambda: mock_activities.get(OPPORTUNITY_ID_2)
                    )
                return MagicMock(first=lambda: None)

        return MagicMock(all=lambda: [], first=lambda: None)

    session.exec.side_effect = mock_exec

    return session


@pytest.mark.asyncio
async def test_check_progress_notifications(mock_session):
    """check_progress_notifications のテスト"""
    # 関数の実行
    result = await check_progress_notifications(TODAY, mock_session)

    # 結果の検証
    assert len(result) == 1  # 古いアクティビティのオポチュニティのみが通知対象
    assert result[0]["opportunity_id"] == OPPORTUNITY_ID_1
    assert result[0]["slack_id"] == "U12345678"
    assert result[0]["last_activity_date"] == OLD_DATE.isoformat()


@pytest.mark.asyncio
async def test_check_progress_notifications_no_activities(
    mock_session, mock_opportunities
):
    """アクティビティのないオポチュニティの check_progress_notifications のテスト"""
    # exec メソッドのモックを変更して、すべてのオポチュニティでアクティビティがないケース
    original_side_effect = mock_session.exec.side_effect

    def updated_exec(query):
        if (
            isinstance(query, SelectOfScalar)
            and str(query).find("FROM activity_log") > -1
        ):
            return MagicMock(first=lambda: None)  # アクティビティなし
        return original_side_effect(query)

    mock_session.exec.side_effect = updated_exec

    # 関数の実行
    result = await check_progress_notifications(TODAY, mock_session)

    # 結果の検証
    assert len(result) == 2  # アクティビティがないため両方のオポチュニティが通知対象
    assert result[0]["last_activity_date"] == "なし"
    assert result[1]["last_activity_date"] == "なし"


@pytest.mark.asyncio
async def test_check_progress_notifications_no_owners(mock_session):
    """オーナーのないオポチュニティの check_progress_notifications のテスト"""
    # exec メソッドのモックを変更して、オーナーがいないケース
    original_side_effect = mock_session.exec.side_effect

    def updated_exec(query):
        if (
            isinstance(query, SelectOfScalar)
            and str(query).find("FROM opportunity_user") > -1
        ):
            return MagicMock(all=lambda: [])  # オーナーなし
        return original_side_effect(query)

    mock_session.exec.side_effect = updated_exec

    # 関数の実行
    result = await check_progress_notifications(TODAY, mock_session)

    # 結果の検証
    assert len(result) == 0  # オーナーがいないため通知なし
