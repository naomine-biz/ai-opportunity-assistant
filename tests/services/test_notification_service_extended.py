"""
通知サービス拡張機能のテスト
"""

import uuid
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from services.notification_service import (
    send_kpi_notification,
    send_progress_notifications,
)


@pytest.mark.asyncio
@patch("services.notification_service.slack_bot")
async def test_send_progress_notifications(mock_slack_bot):
    """send_progress_notifications のテスト"""
    # SlackBotのsend_notificationメソッドをモック
    mock_slack_bot.send_notification = AsyncMock()
    mock_slack_bot.send_notification.return_value = {
        "ok": True,
        "channel": "U12345678",
        "ts": "12345.67890",
    }

    # テスト用の通知データ
    user_id = uuid.uuid4()
    opportunity_id = uuid.uuid4()
    notifications = [
        {
            "user_id": user_id,
            "slack_id": "U12345678",
            "opportunity_id": opportunity_id,
            "opportunity_title": "テスト案件1",
            "last_activity_date": date.today().isoformat(),
        },
        {
            "user_id": user_id,
            "slack_id": "U87654321",
            "opportunity_id": uuid.uuid4(),
            "opportunity_title": "テスト案件2",
            "last_activity_date": date.today().isoformat(),
        },
        {
            # Slack IDなし - スキップされるはず
            "user_id": uuid.uuid4(),
            "opportunity_id": uuid.uuid4(),
            "opportunity_title": "スキップされる案件",
            "last_activity_date": date.today().isoformat(),
        },
    ]

    # 関数を実行
    result = await send_progress_notifications(notifications)

    # 結果の検証
    assert result == 2  # Slack IDがある2件だけ成功するはず
    assert mock_slack_bot.send_notification.call_count == 2  # 2回呼ばれるはず

    # 最初の呼び出しパラメータを検証
    first_call_args = mock_slack_bot.send_notification.call_args_list[0][1]
    assert first_call_args["user_slack_id"] == "U12345678"
    assert "テスト案件1" in first_call_args["message"]
    assert first_call_args["opportunity_data"] == notifications[0]


@pytest.mark.asyncio
@patch("services.notification_service.slack_bot")
async def test_send_progress_notifications_exception(mock_slack_bot):
    """例外発生時の send_progress_notifications のテスト"""
    # SlackBotのsend_notificationメソッドを例外を投げるようにモック
    mock_slack_bot.send_notification = AsyncMock()
    mock_slack_bot.send_notification.side_effect = Exception("テスト例外")

    # テスト用の通知データ
    notifications = [
        {
            "user_id": uuid.uuid4(),
            "slack_id": "U12345678",
            "opportunity_id": uuid.uuid4(),
            "opportunity_title": "テスト案件",
            "last_activity_date": date.today().isoformat(),
        }
    ]

    # 関数を実行 - 例外はキャッチされるはず
    result = await send_progress_notifications(notifications)

    # 結果の検証
    assert result == 0  # 例外によりカウントされないはず
    assert mock_slack_bot.send_notification.called  # メソッドは呼ばれたはず


@pytest.mark.asyncio
@patch("services.notification_service.slack_bot")
async def test_send_kpi_notification(mock_slack_bot):
    """send_kpi_notification のテスト"""
    # SlackBotのsend_notificationメソッドをモック
    mock_slack_bot.send_notification = AsyncMock()
    mock_slack_bot.send_notification.return_value = {
        "ok": True,
        "channel": "U12345678",
        "ts": "12345.67890",
    }

    # テストパラメータ
    user_slack_id = "U12345678"
    message = "KPIを達成するために新たなアクションが必要です"
    opportunity_id = uuid.uuid4()
    opportunity_title = "重要案件A"

    # 関数を実行
    result = await send_kpi_notification(
        user_slack_id=user_slack_id,
        message=message,
        opportunity_id=opportunity_id,
        opportunity_title=opportunity_title,
    )

    # 結果の検証
    assert result is True  # 成功するはず
    mock_slack_bot.send_notification.assert_called_once()  # 1回だけ呼ばれるはず

    # 呼び出しパラメータを検証
    call_args = mock_slack_bot.send_notification.call_args[1]
    assert call_args["user_slack_id"] == user_slack_id
    assert call_args["message"] == message
    assert call_args["opportunity_data"]["opportunity_id"] == opportunity_id
    assert call_args["opportunity_data"]["opportunity_title"] == opportunity_title


@pytest.mark.asyncio
@patch("services.notification_service.slack_bot")
async def test_send_kpi_notification_without_opportunity(mock_slack_bot):
    """案件情報なしでのsend_kpi_notification のテスト"""
    # SlackBotのsend_notificationメソッドをモック
    mock_slack_bot.send_notification = AsyncMock()
    mock_slack_bot.send_notification.return_value = {
        "ok": True,
        "channel": "U12345678",
        "ts": "12345.67890",
    }

    # テストパラメータ
    user_slack_id = "U12345678"
    message = "今週のKPI目標を達成していません"

    # 関数を実行（opportunity_id指定なし）
    result = await send_kpi_notification(user_slack_id=user_slack_id, message=message)

    # 結果の検証
    assert result is True  # 成功するはず
    mock_slack_bot.send_notification.assert_called_once()  # 1回だけ呼ばれるはず

    # 呼び出しパラメータを検証
    call_args = mock_slack_bot.send_notification.call_args[1]
    assert call_args["user_slack_id"] == user_slack_id
    assert call_args["message"] == message
    assert call_args["opportunity_data"] is None  # 案件データなし


@pytest.mark.asyncio
@patch("services.notification_service.slack_bot")
async def test_send_kpi_notification_exception(mock_slack_bot):
    """例外発生時のsend_kpi_notification のテスト"""
    # SlackBotのsend_notificationメソッドを例外を投げるようにモック
    mock_slack_bot.send_notification = AsyncMock()
    mock_slack_bot.send_notification.side_effect = Exception("テスト例外")

    # テストパラメータ
    user_slack_id = "U12345678"
    message = "例外テスト用メッセージ"

    # 関数を実行
    result = await send_kpi_notification(user_slack_id=user_slack_id, message=message)

    # 結果の検証
    assert result is False  # 例外によりFalseが返されるはず
    assert mock_slack_bot.send_notification.called  # メソッドは呼ばれたはず
