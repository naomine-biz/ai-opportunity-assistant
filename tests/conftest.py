"""
テストフィクスチャ定義
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# テスト用環境変数を設定
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
os.environ["SLACK_SIGNING_SECRET"] = "test-signing-secret"
os.environ["OPENAI_API_KEY"] = "sk-test-key"

# srcディレクトリをパスに追加
SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

# データベース接続モック
mock_engine = MagicMock()
mock_session = MagicMock()


@pytest.fixture(autouse=True)
def mock_db_session():
    """データベースセッションをモック"""
    with patch("sqlmodel.create_engine", return_value=mock_engine), \
         patch("db.session.engine", mock_engine), \
         patch("db.session.create_db_and_tables") as mock_create:
        yield mock_session


@pytest.fixture(scope="function")
async def mock_verify_slack_signature():
    """署名検証をバイパスするための非同期モック関数"""
    return None

@pytest.fixture(scope="function")
def client(mock_verify_slack_signature):
    """テスト用クライアントを作成"""
    # 設定とセッション取得
    from core.config import settings
    from db.session import get_session
    from main import app
    from api.routes.slack_routes import verify_slack_signature

    # テスト用セッションをDI
    def override_get_session():
        session = MagicMock()
        yield session

    # 署名検証をバイパスするための依存関係オーバーライド
    async def mock_verify():
        return None

    # テスト用セッションと署名検証バイパスを設定
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[verify_slack_signature] = mock_verify

    # テストクライアントを作成して返す
    with TestClient(app) as test_client:
        yield test_client

    # テスト後に依存関係をリセット
    app.dependency_overrides.clear()


@pytest.fixture(name="mock_slack_settings")
def mock_slack_settings_fixture():
    """Slack設定モック"""
    from core.config import settings
    return settings