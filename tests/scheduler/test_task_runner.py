"""
スケジューラタスクランナーのテスト
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Response

from scheduler.task_runner import (
    run_kpi_action_notification,
    run_progress_notification_check,
)


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_progress_notification_check_success(mock_client):
    """正常系：進捗通知チェックタスクのテスト"""
    # モックレスポンスの設定
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "completed",
        "notifications_count": 5,
        "notifications_sent": 3,
    }

    # AsyncClientのモック設定
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # 関数実行
    result = await run_progress_notification_check()

    # 検証
    assert result == 3  # notifications_sentの値が返される

    # APIの呼び出し確認
    mock_client_instance.post.assert_called_once()
    call_args = mock_client_instance.post.call_args[0]

    # URLパスの検証
    assert "/api/notification/progress" in call_args[0]

    # 日付パラメータの検証
    today = date.today().isoformat()
    assert {"target_date": today} == mock_client_instance.post.call_args[1]["json"]


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_progress_notification_check_error(mock_client):
    """異常系：APIエラー時の進捗通知チェックタスクのテスト"""
    # モックレスポンスの設定
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    # AsyncClientのモック設定
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # 関数実行
    result = await run_progress_notification_check()

    # 検証
    assert result == 0  # エラー時は0を返す

    # APIの呼び出し確認
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_progress_notification_check_exception(mock_client):
    """異常系：例外発生時の進捗通知チェックタスクのテスト"""
    # 例外を発生させる
    mock_client.return_value.__aenter__.side_effect = Exception("Test exception")

    # 関数実行 - 例外をキャッチして0を返すはず
    result = await run_progress_notification_check()

    # 検証
    assert result == 0  # 例外発生時は0を返す


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_kpi_action_notification_success(mock_client):
    """正常系：KPI通知タスクのテスト"""
    # モックレスポンスの設定
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "completed",
        "success": True,
        "user_slack_id": "U12345678",
    }

    # AsyncClientのモック設定
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # テスト用ユーザーデータ
    test_users = [
        {
            "slack_id": "U12345678",
            "kpi_status": "at_risk",
            "message": "テスト通知",
        }
    ]

    # 関数実行
    result = await run_kpi_action_notification(test_users)

    # 検証
    assert result == 1  # 1件成功

    # APIの呼び出し確認
    mock_client_instance.post.assert_called_once()
    call_args = mock_client_instance.post.call_args[0]

    # URLパスの検証
    assert "/api/notification/kpi" in call_args[0]

    # パラメータの検証
    assert "user_slack_id" in mock_client_instance.post.call_args[1]["json"]
    assert "message" in mock_client_instance.post.call_args[1]["json"]


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_kpi_action_notification_multiple_users(mock_client):
    """複数ユーザー向けKPI通知タスクのテスト"""
    # モックレスポンスの設定
    mock_response_success = MagicMock(spec=Response)
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"success": True}

    mock_response_error = MagicMock(spec=Response)
    mock_response_error.status_code = 500
    mock_response_error.text = "Error"

    # AsyncClientのモック設定
    mock_client_instance = AsyncMock()
    # 1回目は成功、2回目は失敗
    mock_client_instance.post.side_effect = [mock_response_success, mock_response_error]
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # テスト用ユーザーデータ
    test_users = [
        {
            "slack_id": "U12345678",
            "message": "テスト通知1",
        },
        {
            "slack_id": "U87654321",
            "message": "テスト通知2",
        },
    ]

    # 関数実行
    result = await run_kpi_action_notification(test_users)

    # 検証
    assert result == 1  # 2件中1件成功
    assert mock_client_instance.post.call_count == 2  # 2回呼び出し


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_kpi_action_notification_default_users(mock_client):
    """デフォルトユーザー向けKPI通知タスクのテスト"""
    # モックレスポンスの設定
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    # AsyncClientのモック設定
    mock_client_instance = AsyncMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # デフォルト値を使用（ユーザーリスト指定なし）
    result = await run_kpi_action_notification()

    # 検証
    assert result == 1  # 1件成功（デフォルトユーザー）
    mock_client_instance.post.assert_called_once()  # 1回呼び出し


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_kpi_action_notification_invalid_user(mock_client):
    """無効なユーザーデータのKPI通知タスクのテスト"""
    # AsyncClientのモック設定
    mock_client_instance = AsyncMock()
    mock_client.return_value.__aenter__.return_value = mock_client_instance

    # 無効なユーザーデータ
    test_users = [
        {
            # slack_idなし
            "message": "テスト通知1",
        },
        {
            "slack_id": "U87654321",
            # messageなし
        },
    ]

    # 関数実行
    result = await run_kpi_action_notification(test_users)

    # 検証
    assert result == 0  # 0件成功
    assert not mock_client_instance.post.called  # 呼び出しなし


@pytest.mark.asyncio
@patch("scheduler.task_runner.httpx.AsyncClient")
async def test_run_kpi_action_notification_exception(mock_client):
    """例外発生時のKPI通知タスクのテスト"""
    # 例外を発生させる
    mock_client.return_value.__aenter__.side_effect = Exception("Test exception")

    # 関数実行 - 例外をキャッチして0を返すはず
    result = await run_kpi_action_notification()

    # 検証
    assert result == 0  # 例外発生時は0を返す
