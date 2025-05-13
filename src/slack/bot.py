"""
Slack Bot モジュール - Slackへのメッセージ送信と情報取得を担当
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from core.config import settings
from core.logger import get_slack_logger

logger = get_slack_logger()


class SlackBot:
    """
    Slackへのメッセージ送信と情報取得を担当するクラス
    """

    def __init__(self):
        """SlackBotの初期化"""
        self.bot_token = settings.SLACK_BOT_TOKEN
        self.client = AsyncWebClient(token=self.bot_token)
        self.rate_limit_delay = 1.0  # APIレート制限時のデフォルト遅延(秒)
        self.max_retries = 3  # API呼び出し失敗時の最大リトライ回数
        logger.info("Initializing SlackBot")

        # 本番実装
        self.use_mock = False

    async def send_message(
        self, channel_id: str, text: str, blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Slackにメッセージを送信する

        Args:
            channel_id: 送信先チャンネルまたはDM ID
            text: 送信するテキストメッセージ
            blocks: Block Kit形式のメッセージ構造（オプション）

        Returns:
            Slack APIレスポンス
        """
        if self.use_mock:
            logger.info(
                "MOCK: Sending message to Slack",
                extra={
                    "channel_id": channel_id,
                    "text": text,
                    "has_blocks": blocks is not None,
                },
            )
            # モックレスポンスを返す
            return {
                "ok": True,
                "channel": channel_id,
                "ts": f"{uuid.uuid4().hex[:8]}.{uuid.uuid4().hex[:6]}",  # モックのタイムスタンプ
                "message": {
                    "text": text,
                    "blocks": blocks,
                },
            }
        else:
            # 実際のSlack APIを呼び出す実装
            return await self._call_slack_api(
                method="chat_postMessage",
                channel=channel_id,
                text=text,
                blocks=blocks,
            )

    async def send_notification(
        self,
        user_slack_id: str,
        message: str,
        opportunity_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        ユーザーに通知を送信する

        Args:
            user_slack_id: 通知先ユーザーのSlack ID
            message: 通知メッセージ
            opportunity_data: 案件関連データ（オプション）

        Returns:
            送信結果
        """
        # ブロックの構築
        blocks = self._build_notification_blocks(message, opportunity_data)

        # DMにメッセージ送信
        return await self.send_message(
            channel_id=user_slack_id,  # DMの場合はユーザーIDを直接指定
            text=message,  # フォールバック用テキスト
            blocks=blocks,  # リッチなメッセージ表示用ブロック
        )

    def _build_notification_blocks(
        self, message: str, opportunity_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        通知用のBlock Kitブロックを構築する

        Args:
            message: 通知メッセージ
            opportunity_data: 案件関連データ（オプション）

        Returns:
            Block Kit形式のブロックリスト
        """
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*通知*\n{message}"}}
        ]

        # 案件データがある場合は追加情報を表示
        if opportunity_data:
            blocks.append({"type": "divider"})

            fields = []
            if opportunity_data.get("opportunity_title"):
                title = opportunity_data.get("opportunity_title")
                fields.append(
                    {
                        "type": "mrkdwn",
                        "text": f"*【案件名】*\n{title}",
                    }
                )

            if opportunity_data.get("last_activity_date"):
                last_date = opportunity_data.get("last_activity_date")
                fields.append(
                    {
                        "type": "mrkdwn",
                        "text": f"*【最終活動日】*\n{last_date}",
                    }
                )

            blocks.append({"type": "section", "fields": fields})

            # アクションボタン（将来的に機能を追加予定）
            opp_id = opportunity_data.get("opportunity_id")
            blocks.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "案件を表示",
                                "emoji": True,
                            },
                            "value": f"view_opportunity_{opp_id}",
                            "action_id": "view_opportunity",
                        }
                    ],
                }
            )

        return blocks

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        ユーザー情報を取得する

        Args:
            user_id: Slack ユーザーID

        Returns:
            ユーザー情報。取得できなかった場合はNone
        """
        if self.use_mock:
            logger.info(
                "MOCK: Getting user info from Slack",
                extra={"user_id": user_id},
            )
            # モックのユーザー情報を返す
            return {
                "ok": True,
                "user": {
                    "id": user_id,
                    "team_id": "T12345678",
                    "name": f"mock_user_{user_id[-4:]}",
                    "real_name": f"Mock User {user_id[-4:]}",
                    "is_admin": False,
                    "is_bot": False,
                },
            }
        else:
            # 実際のSlack APIを呼び出す実装
            return await self._call_slack_api(method="users_info", user=user_id)

    async def _call_slack_api(
        self, method: str, retry_count: int = 0, **kwargs
    ) -> Dict[str, Any]:
        """
        Slack APIを呼び出すためのヘルパーメソッド (レート制限とエラー処理を含む)

        Args:
            method: 呼び出すAPIメソッド名
            retry_count: 現在のリトライ回数
            **kwargs: APIに渡す引数

        Returns:
            APIレスポンス
        """
        try:
            # APIメソッドの動的呼び出し
            api_method = getattr(self.client, method)
            response = await api_method(**kwargs)
            return response
        except SlackApiError as e:
            error = e.response["error"]

            # レート制限エラーの処理
            if error == "ratelimited":
                retry_after = int(
                    e.response.headers.get("Retry-After", self.rate_limit_delay)
                )
                logger.warning(
                    f"Slack API rate limit reached. {retry_after}秒後にリトライ",
                    extra={"method": method, "retry_after": retry_after},
                )

                # 適切な時間待機後、リトライ
                await asyncio.sleep(retry_after)
                return await self._call_slack_api(method, retry_count, **kwargs)

            # その他のエラーの処理
            elif retry_count < self.max_retries:
                # バックオフ戦略でリトライ (指数関数的に待機時間を増やす)
                wait_time = (2**retry_count) * self.rate_limit_delay
                logger.warning(
                    f"Slack API error: {error}. {wait_time: .1f} 秒後にリトライします",
                    extra={
                        "method": method,
                        "error": error,
                        "retry_count": retry_count + 1,
                    },
                )

                await asyncio.sleep(wait_time)
                return await self._call_slack_api(method, retry_count + 1, **kwargs)
            else:
                # 最大リトライ回数を超えた場合
                logger.error(
                    "Slack API呼び出しが最大リトライ回数に達しました",
                    extra={
                        "method": method,
                        "error": error,
                        "max_retries": self.max_retries,
                    },
                )
                # エラー情報を含むレスポンスを返す
                return {
                    "ok": False,
                    "error": error,
                    "response_metadata": {
                        "messages": [f"{self.max_retries}回のリトライ後に失敗"]
                    },
                }


# シングルトンインスタンス
slack_bot = SlackBot()
