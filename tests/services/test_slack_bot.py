"""
SlackBotのテスト
"""

import uuid
from unittest.mock import patch

import pytest

from slack.bot import SlackBot


@pytest.fixture
def slack_bot():
    """SlackBotのインスタンスを返す"""
    bot = SlackBot()
    bot.use_mock = True  # モックモードを有効化
    return bot


@pytest.mark.asyncio
async def test_send_message(slack_bot):
    """send_message のテスト"""
    # 送信パラメータ
    channel_id = "D12345678"
    text = "テストメッセージ"
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "テスト"}}]

    # メッセージ送信
    result = await slack_bot.send_message(
        channel_id=channel_id, text=text, blocks=blocks
    )

    # 結果の検証
    assert result["ok"] is True
    assert result["channel"] == channel_id
    assert result["message"]["text"] == text
    assert result["message"]["blocks"] == blocks


@pytest.mark.asyncio
async def test_send_notification(slack_bot):
    """send_notification のテスト"""
    # 送信パラメータ
    user_slack_id = "U12345678"
    message = "テスト通知"
    opportunity_data = {
        "opportunity_id": uuid.uuid4(),
        "opportunity_title": "テスト案件",
        "last_activity_date": "2025-01-01",
    }

    # スパイとしてsend_messageをモック化
    with patch.object(slack_bot, "send_message", autospec=True) as mock_send_message:
        mock_send_message.return_value = {
            "ok": True,
            "channel": user_slack_id,
            "ts": "12345.67890",
        }

        # 通知送信
        result = await slack_bot.send_notification(
            user_slack_id=user_slack_id,
            message=message,
            opportunity_data=opportunity_data,
        )

        # send_messageが呼ばれたことを確認
        mock_send_message.assert_called_once()
        # channel_idの確認
        assert mock_send_message.call_args[1]["channel_id"] == user_slack_id
        # textの確認
        assert mock_send_message.call_args[1]["text"] == message
        # blocksが含まれていることを確認
        assert "blocks" in mock_send_message.call_args[1]
        assert mock_send_message.call_args[1]["blocks"] is not None

        # 結果の検証
        assert result["ok"] is True
        assert result["channel"] == user_slack_id


@pytest.mark.asyncio
async def test_get_user_info(slack_bot):
    """get_user_info のテスト"""
    # ユーザーID
    user_id = "U12345678"

    # ユーザー情報取得
    result = await slack_bot.get_user_info(user_id)

    # 結果の検証
    assert result["ok"] is True
    assert result["user"]["id"] == user_id
    assert "name" in result["user"]
    assert "real_name" in result["user"]


@pytest.mark.asyncio
async def test_build_notification_blocks(slack_bot):
    """_build_notification_blocks のテスト"""
    # パラメータ
    message = "テスト通知"
    opportunity_data = {
        "opportunity_id": uuid.uuid4(),
        "opportunity_title": "テスト案件",
        "last_activity_date": "2025-01-01",
    }

    # ブロック構築
    blocks = slack_bot._build_notification_blocks(message, opportunity_data)

    # 結果の検証
    assert len(blocks) > 0
    # 通知メッセージのブロックを確認
    assert blocks[0]["type"] == "section"
    assert message in blocks[0]["text"]["text"]

    # opportunity_dataがある場合の追加ブロックを確認
    assert len(blocks) > 3  # 複数のブロックが存在
    assert blocks[1]["type"] == "divider"  # 区切り線
    assert blocks[2]["type"] == "section"  # セクション（フィールド）
    assert len(blocks[2]["fields"]) == 2  # フィールド数
    assert blocks[3]["type"] == "actions"  # アクションボタン

    # アクションボタンのテキストを確認
    assert blocks[3]["elements"][0]["text"]["text"] == "案件を表示"
    # アクションボタンのvalueにオポチュニティIDが含まれていることを確認
    assert str(opportunity_data["opportunity_id"]) in blocks[3]["elements"][0]["value"]
