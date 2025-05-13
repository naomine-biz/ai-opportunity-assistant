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
# 自動テスト実行（モックテスト）
poetry run pytest

# Slack通知テストスクリプト
# 実際のSlack APIを使用して通知機能をテストする
poetry run python test_slack_channels.py
```

### Slack連携テスト

プロジェクトには以下のSlack連携テストスクリプトが含まれています：

- `test_slack_channels.py`: generalチャンネルへのメッセージ送信をテストします。

これらのスクリプトは自動テスト（pytest）とは別に、実際のSlack APIとの連携確認のために使用します。
テストを実行する前に、`.env`ファイルにSlack API認証情報を設定してください。

```
# Slack連携設定
SLACK_BOT_TOKEN=xoxb-XXXXXXXX     # SlackボットトークンID
SLACK_SIGNING_SECRET=XXXXXXXX      # Slack署名シークレット
```

### リント実行

```bash
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
poetry run python -m scripts.check_dependencies
```

### プルリクエスト作成ルール

プルリクエストを作成する際は、以下のルールに従ってください：

1. **ブランチ命名規則**
   - 機能追加: `feature/機能名`
   - バグ修正: `fix/バグ内容`
   - リファクタリング: `refactor/内容`
   - ドキュメント: `docs/内容`

2. **コード品質**
   - PRを作成する前に必ず以下のコマンドを実行し、コードフォーマットとリントを行う
     ```bash
     poetry run black src tests
     poetry run isort src tests
     poetry run flake8 src tests
     poetry run python -m scripts.check_dependencies
     ```
   - 不要なimportや使われていない変数は削除する
   - すべてのテストが通過していることを確認する

3. **依存関係ルール**
   - モジュール間の依存関係ルールを守ること
   - apiからslackへの直接依存など、禁止されている依存関係を作らない
   - 疑わしい場合は`poetry run python -m scripts.check_dependencies`で検証する

4. **PR説明**
   - 概要: 変更の概要を簡潔に記述
   - 背景: なぜこの変更が必要か
   - 変更内容: 主な変更点をリストアップ
   - テスト: どのようにテストしたか

5. **レビュー前チェックリスト**
   - [ ] コードフォーマット・リントを適用済み
   - [ ] テストがすべて通過
   - [ ] 依存関係ルールを遵守
   - [ ] ドキュメントを更新（必要な場合）
