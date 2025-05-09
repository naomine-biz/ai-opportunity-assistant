"""
テストファイル用の特殊モジュール
このファイルはpytestが最初に読み込み、データベース接続と関連モジュールをモックします。
"""
import os
from unittest.mock import MagicMock, patch

# テスト環境変数を設定
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
os.environ["SLACK_SIGNING_SECRET"] = "test-signing-secret"
os.environ["OPENAI_API_KEY"] = "sk-test-key"

# データベースエンジン作成をモック
mock_engine = MagicMock()
mock_session = MagicMock()

# セッションファクトリをモック
mock_session_factory = MagicMock()
mock_session_factory.return_value.__enter__.return_value = mock_session
mock_session_factory.return_value.__exit__.return_value = None

# 必要なモックパッチを適用
patch("sqlmodel.create_engine", return_value=mock_engine).start()


# エンジン設定を確認
def create_mock_db():
    pass


# 実モジュールのインポートの前にパッチを適用
patch("db.session.create_db_and_tables", create_mock_db).start()
