"""
データベースセッション提供サービス
"""

from sqlmodel import Session

from db.session import get_session


def get_db_session() -> Session:
    """
    データベースセッションを取得する

    このサービスは、APIエンドポイントでセッションを依存性として使用するための共通関数を提供します。
    これにより、APIレイヤーからDBレイヤーへの直接の依存を避けられます。

    Returns:
        Session: SQLModelセッション
    """
    return get_session()
