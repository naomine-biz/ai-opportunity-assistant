import json
from typing import Any, Dict, Optional

from src.core.logger import get_slack_logger

logger = get_slack_logger()


class SlackEventHandler:
    """
    Slack Event APIからのイベントを処理するハンドラクラス
    """

    def __init__(self):
        """SlackEventHandlerの初期化"""
        logger.info("Initializing SlackEventHandler")

    async def process_message_event(
        self, user_id: str, text: str, channel: str, ts: str, event_data: Dict[str, Any]
    ) -> None:
        """
        メッセージイベントを処理する

        Args:
            user_id: Slack ユーザーID
            text: メッセージテキスト
            channel: チャンネルID
            ts: メッセージタイムスタンプ
            event_data: Slackイベント全体のデータ
        """
        logger.info(
            "Processing message event",
            extra={
                "user_id": user_id,
                "channel": channel,
                "ts": ts,
            },
        )

        # TODO: この部分に自然言語処理やデータベース保存ロジックを実装
        # 現時点ではログ出力のみ

        # メッセージを解析して営業活動情報を抽出（将来実装）
        activity_info = self._extract_activity_info(text)

        if activity_info:
            logger.info(
                "Extracted activity information",
                extra={"activity_info": json.dumps(activity_info)},
            )
        else:
            logger.info("No activity information extracted from message")

    def _extract_activity_info(self, text: str) -> Optional[Dict[str, Any]]:
        """
        テキストから営業活動情報を抽出する（モック実装）

        Args:
            text: メッセージテキスト

        Returns:
            抽出された活動情報の辞書。見つからない場合はNone
        """
        # 現時点ではモック実装
        # 実際の実装では自然言語処理モジュールを使用して情報を抽出

        # 「訪問」という単語があれば訪問イベントと判断（単純なモック）
        if "訪問" in text:
            return {
                "type": "訪問",
                "customer": None,  # 顧客名の抽出はまだ実装なし
                "date": None,  # 日付の抽出はまだ実装なし
            }
        # 「電話」という単語があれば電話イベントと判断
        elif "電話" in text:
            return {
                "type": "電話",
                "customer": None,
                "date": None,
            }
        # それ以外はNone
        return None


# シングルトンインスタンス
slack_event_handler = SlackEventHandler()
