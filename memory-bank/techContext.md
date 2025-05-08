# 技術コンテキスト

## 使用技術

### バックエンド API
- **FastAPI (Python)**
  - 軽量で非同期処理に対応
  - 自動APIドキュメント生成（OpenAPI/Swagger）
  - 型アノテーションによる堅牢性
  - AI/MLライブラリとの親和性が高い

### エージェントモジュール（自然言語処理・ルールロジック）
- **Python**
  - `openai` ライブラリ（OpenAI API利用時）
  - `transformers`（NER等を用いる場合）
  - `spaCy`（軽量なエンティティ抽出）

- 初期はAPI直接呼び出しのみで構成
- LLMとの対話ミドルウェア（LangChain等）は導入しない
- 複雑な連携・エージェント制御が必要になった場合に後からリファクタリングで導入可能性

### データベース
- **PostgreSQL**
  - 標準SQL
  - JSONB対応による柔軟な構造管理
  - 拡張性・実績

### Python用DBライブラリ
- **SQLModel**
  - FastAPIとの親和性（同じ作者によるライブラリ）
  - SQLAlchemyベースで拡張性高い
  - Pydantic型と連携し、APIスキーマとの一貫性

### Slack連携
- **slack_sdk (Python)**
  - Slack Bot開発公式SDK
  - Slack Events API, Web API 対応
  - Pythonエコシステムに統合可能

### スケジューラー
- **APScheduler (Python)**
  - Python内でスケジュール管理
  - タスク実行間隔やcron指定が可能
  - FastAPIと同一プロセス内に統合可能
  - Celeryほどの分散・外部Brokerは不要

## 開発セットアップ

### 環境構築
- **Python 3.9+**
- **Poetry** または **pip + requirements.txt** による依存管理
- **.env** ファイルによる環境変数管理

### 開発ツール
- **black**: 自動フォーマット
- **isort**: import順自動整列
- **flake8**: 静的解析
- **pytest**: テスト実行

### 開発ワークフロー
- **GitHub** でのソース管理
- **GitHub Actions** による自動テスト
- **Conventional Commit** 準拠のコミットメッセージ（推奨）

## 技術的制約

### スケーラビリティ
- 初期段階では単一サーバー構成
- 水平スケーリングは考慮しない（将来的な課題）
- APSchedulerは分散環境では考慮が必要

### パフォーマンス
- 自然言語処理はAPIコール待ち時間が発生
- 非同期処理で応答性を確保
- 大量データ処理は想定しない（100名規模）

### セキュリティ
- Slack署名検証による認証
- 内部APIは認証なし（初期段階）
- 環境変数による秘密情報管理

## 依存関係

### 主要パッケージ
```
fastapi==0.95.0
uvicorn==0.21.1
sqlmodel==0.0.8
psycopg2-binary==2.9.6
slack-sdk==3.20.2
apscheduler==3.10.1
python-dotenv==1.0.0
openai==0.27.4
```

### 開発用パッケージ
```
pytest==7.3.1
black==23.3.0
isort==5.12.0
flake8==6.0.0
```

## ツール使用パターン

### 設定管理
- `.env` ファイルに環境変数形式で設定値を管理
- `config.py` にて `.env` から設定値を読み込み、アプリケーションで利用
- `.env.example` をリポジトリに含め、設定項目の仕様書とする

### ログ管理
- JSON形式の構造化ログ
- ログ種別：アクセスログ、Slackイベントログ、操作ログ、アプリケーションログ
- 初期構成: stdout出力（コンテナ/アプリ標準出力）

### テスト戦略
- ユニットテスト：サービス層の関数単位テスト
- APIテスト：FastAPIエンドポイントの統合テスト
- シナリオテスト：Slackイベント処理、スケジューラーのE2Eテスト
- pytest + unittest.mock を使用
