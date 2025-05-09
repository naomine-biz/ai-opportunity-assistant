"""
Slackイベントハンドラーのテスト
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# srcディレクトリをパスに追加
SRC_DIR = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

# flake8の警告を抑制：インポート順序の問題
# isort: skip_file
from slack.handlers import SlackEventHandler, slack_event_handler  # noqa: E402


@pytest.mark.asyncio
async def test_process_message_event():
    """メッセージイベント処理が正しく動作するか確認"""
    # テスト用データ
    user_id = "U123USER"
    text = "A社に訪問しました。進捗を報告します。"
    channel = "D123CHANNEL"
    ts = "1609459200.000100"
    event_data = {"type": "event_callback", "event": {"type": "message"}}
    
    # ロガーをモック
    with patch("slack.handlers.logger") as mock_logger:
        # テスト対象を実行
        await slack_event_handler.process_message_event(
            user_id=user_id,
            text=text,
            channel=channel,
            ts=ts,
            event_data=event_data
        )
        
        # ログが記録されたことを確認
        mock_logger.info.assert_any_call(
            "Processing message event",
            extra={
                "user_id": user_id,
                "channel": channel,
                "ts": ts,
            }
        )


def test_extract_activity_info():
    """テキストから営業活動情報を適切に抽出できることを確認"""
    # ハンドラーインスタンスを作成
    handler = SlackEventHandler()
    
    # 訪問を含むテキスト
    visit_text = "今日はA社に訪問しました。"
    visit_info = handler._extract_activity_info(visit_text)
    
    # 適切な活動タイプが抽出されることを確認
    assert visit_info is not None
    assert visit_info["type"] == "訪問"
    
    # 電話を含むテキスト
    call_text = "B社に電話して見積もりの件を確認しました。"
    call_info = handler._extract_activity_info(call_text)
    
    # 適切な活動タイプが抽出されることを確認
    assert call_info is not None
    assert call_info["type"] == "電話"
    
    # 活動キーワードを含まないテキスト
    other_text = "来週の予定を確認します。"
    other_info = handler._extract_activity_info(other_text)
    
    # 活動情報が抽出されないことを確認
    assert other_info is None