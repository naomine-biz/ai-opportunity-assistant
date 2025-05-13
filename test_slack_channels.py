"""
Slackチャンネルテストスクリプト - generalチャンネルへのメッセージ送信テスト
"""

import asyncio
import os

from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

# 環境変数を読み込む
load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")


async def test_slack_channels():
    """
    通知サービス用のSlackチャンネルテスト
    - generalチャンネルへの投稿
    """
    print(f"設定されているトークン: {SLACK_BOT_TOKEN[:10]}...")

    # APIクライアントの初期化
    client = AsyncWebClient(token=SLACK_BOT_TOKEN)

    try:
        # ボット情報を取得
        auth_result = await client.auth_test()
        if not auth_result.get("ok"):
            print(f"認証失敗: {auth_result}")
            return

        print(f"認証成功: {auth_result['user']} (チーム: {auth_result['team']})")
        print(f"ボットID: {auth_result['user_id']}")
        print(f"チームID: {auth_result['team_id']}")

        # テスト用メッセージ
        message = "これはSlack通知サービスのテストメッセージです。"

        # generalチャンネル送信テスト
        print("\n==== generalチャンネル送信テスト ====")

        try:
            # generalチャンネルのIDを取得（通常は "general" という名前）
            general_channel = None
            channels_result = await client.conversations_list(types="public_channel")

            if not channels_result.get("ok"):
                print(f"チャンネル一覧の取得に失敗: {channels_result.get('error')}")
            else:
                print("チャンネル一覧:")
                for channel in channels_result["channels"]:
                    print(f"- {channel['name']} (ID: {channel['id']})")
                    if channel["name"] == "general":
                        general_channel = channel["id"]

            # generalチャンネルが見つからない場合は最初のチャンネルを使用
            if not general_channel and channels_result.get("channels"):
                general_channel = channels_result["channels"][0]["id"]

            if not general_channel:
                print("generalチャンネルが見つかりませんでした")
                return

            # generalチャンネルにメッセージ送信
            general_result = await client.chat_postMessage(
                channel=general_channel,
                text=message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*チャンネルテスト*\n{message}",
                        },
                    }
                ],
            )

            if general_result.get("ok"):
                print("generalチャンネル送信成功:")
                print(f"- チャンネルID: {general_result['channel']}")
                print(f"- タイムスタンプ: {general_result['ts']}")
            else:
                print(f"generalチャンネル送信失敗: {general_result.get('error')}")

        except SlackApiError as e:
            print(f"generalチャンネル送信エラー: {e}")

    except Exception as e:
        print(f"予期しないエラー: {e}")


if __name__ == "__main__":
    asyncio.run(test_slack_channels())
