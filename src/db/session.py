from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from core.config import settings
from core.logger import get_app_logger

logger = get_app_logger()

# データベースエンジンの作成
engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # DEBUGモードの場合はSQL文を表示
    pool_pre_ping=True,  # 接続状態を事前確認
)


def create_db_and_tables() -> None:
    """データベースとテーブルを作成"""
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    データベースセッションを取得するジェネレータ関数

    FastAPIの依存性注入で使用される

    Yields:
        Session: SQLModelのセッション
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(
                f"Database session error: {str(e)}", extra={"exception": str(e)}
            )
            session.rollback()
            raise
        finally:
            session.close()
