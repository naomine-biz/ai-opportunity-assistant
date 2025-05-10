import json
import logging
import sys
import uuid
from typing import Any, Dict, Optional

from core.config import settings


class JsonFormatter(logging.Formatter):
    """JSONフォーマットでログを出力するフォーマッタ"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # request_idがある場合は追加
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # user_idがある場合は追加
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # 操作種別と対象リソースがある場合は追加（監査ログ用）
        if hasattr(record, "operation_type"):
            log_data["operation_type"] = record.operation_type

        if hasattr(record, "resource_type"):
            log_data["resource_type"] = record.resource_type

        if hasattr(record, "resource_id"):
            log_data["resource_id"] = record.resource_id

        # 例外情報がある場合は追加
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ContextAdapter(logging.LoggerAdapter):
    """コンテキスト情報（request_id等）をログに追加するアダプタ"""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        # extra情報が存在しない場合は初期化
        kwargs["extra"] = kwargs.get("extra", {})

        # コンテキスト情報をextraに追加
        for key, value in self.extra.items():
            if key not in kwargs["extra"]:
                kwargs["extra"][key] = value

        return msg, kwargs


def get_logger(name: str, request_id: Optional[str] = None) -> logging.LoggerAdapter:
    """
    指定した名前のロガーを取得する

    Args:
        name: ロガー名（例: app.access, app.slack）
        request_id: リクエストID（None の場合は新規生成）

    Returns:
        ロガーアダプタ
    """
    logger = logging.getLogger(name)

    # request_idがない場合は新規生成
    if request_id is None:
        request_id = str(uuid.uuid4())

    # コンテキスト情報を設定
    context = {"request_id": request_id}

    return ContextAdapter(logger, context)


def setup_logging() -> None:
    """アプリケーション全体のログ設定を初期化"""
    # ルートロガーの設定
    root_logger = logging.getLogger()

    # 環境変数からログレベルを設定
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # 標準出力へのハンドラを設定
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)

    # 主要ロガーの設定
    logger_names = [
        "app.access",
        "app.slack",
        "app.audit",
        "app.app",
        "app.opportunity",
        "app.activity",
        "app.notification",
    ]
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)


# アプリケーション起動時にログ設定を初期化
setup_logging()


# 主要ロガー取得用関数
def get_access_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.access", request_id)


def get_slack_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.slack", request_id)


def get_audit_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.audit", request_id)


def get_app_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.app", request_id)


def get_opportunity_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.opportunity", request_id)


def get_activity_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.activity", request_id)


def get_notification_logger(request_id: Optional[str] = None) -> logging.LoggerAdapter:
    return get_logger("app.notification", request_id)
