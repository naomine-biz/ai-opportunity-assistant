# 営業オポチュニティマネジメント AIアシスタント

営業活動の記録と分析を支援するAIアシスタントシステム

## 環境構築

### 必要条件

- Python 3.9以上
- PostgreSQL
- Poetry

### インストール

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/ai-opportunity-assistant.git
cd ai-opportunity-assistant
```

2. Poetryで依存関係をインストール

```bash
poetry install
```

3. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な環境変数を設定してください。

```bash
cp .env.example .env
# .envファイルを編集して必要な値を設定
```

### 実行方法

```bash
# 開発サーバー起動
poetry run python src/main.py
```

## プロジェクト構造

```
ai-opportunity-assistant/
├── docs/          # プロジェクト設計文書
├── memory-bank/   # プロジェクト概要情報
├── seeds/         # 初期データ
├── src/           # ソースコード
│   ├── agents/    # AIエージェント関連
│   ├── api/       # APIエンドポイント
│   ├── core/      # 設定、ロギング等の中核機能
│   ├── db/        # データベース関連
│   ├── models/    # データモデル
│   ├── scheduler/ # スケジューリング処理
│   ├── services/  # ビジネスロジック
│   ├── slack/     # Slack連携
│   └── main.py    # アプリケーションエントリーポイント
├── pyproject.toml # Poetryプロジェクト設定
└── README.md
```

## 開発

### テスト実行

```bash
poetry run pytest
```

### リント実行

```bash
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
```