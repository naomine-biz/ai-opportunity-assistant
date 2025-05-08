# システムパターン

## システムアーキテクチャ

### 全体構成
```
[Slack] <---> [FastAPI] <---> [Database]
   ^             |
   |             v
   +-------> [Scheduler]
```

- **Slackインターフェース**: ユーザーとの対話窓口
- **FastAPI**: バックエンドAPIサーバー
- **Database**: PostgreSQLによるデータ永続化
- **Scheduler**: 定期実行処理（通知など）

### レイヤー構造
```
┌─────────────────────────────────────┐
│ インターフェース層                  │
│ (slack/, api/)                      │
├─────────────────────────────────────┤
│ ビジネスロジック層                  │
│ (services/, scheduler/)             │
├─────────────────────────────────────┤
│ データアクセス層                    │
│ (db/)                               │
├─────────────────────────────────────┤
│ AI処理層                            │
│ (agents/)                           │
└─────────────────────────────────────┘
```

## 主要技術決定

### 依存関係ルール
- **上位レイヤーから下位レイヤーのみ依存可**
- **下位レイヤーから上位レイヤーへの依存禁止**
- **横の依存も禁止（同レイヤー間の直接依存なし）**

| Source（呼び出し元） | Allowed Target（依存可能先） | Forbidden Target（依存禁止先）              |
| -------------------- | ---------------------------- | ------------------------------------------- |
| `slack/`             | `api/`                       | `services/`, `db/`, `agents/`, `scheduler/` |
| `api/`               | `services/`                  | `db/`, `agents/`, `scheduler/`              |
| `services/`          | `db/`, `agents/`             | `api/`, `slack/`, `scheduler/`              |
| `scheduler/`         | `services/`                  | `api/`, `slack/`, `db/`, `agents/`          |
| `db/`                | （なし）                     | 全て                                        |
| `agents/`            | （なし）                     | 全て                                        |

### データフロー
1. **Slack入力フロー**
   ```
   Slack入力 -> slack/handlers.py -> api/slack_routes.py -> services/opportunity_service.py -> agents/parser.py -> db/repository.py -> DB保存
   ```

2. **スケジューラー通知フロー**
   ```
   APScheduler -> scheduler/task_runner.py -> services/opportunity_service.py -> db/repository.py -> データ取得 -> slack/bot.py -> Slack通知
   ```

3. **API操作フロー**
   ```
   API呼出 -> api/api_routes.py -> services/opportunity_service.py -> db/repository.py -> DB操作
   ```

## 重要実装パス

### 自然言語処理パス
```
1. Slackからのメッセージ受信
2. agents/parser.pyでテキスト解析
3. オポチュニティID、アクティビティタイプ、日付などを抽出
4. 構造化データに変換
5. DBに保存
```

### 通知生成パス
```
1. スケジューラーがタスク実行
2. 未更新オポチュニティの検索
3. 通知条件の評価
4. 通知メッセージ生成
5. Slack APIで送信
```

## コンポーネント関係

### モジュール間の関係
- **slack/**: Slack Event API受信、メッセージ送信
- **api/**: REST APIエンドポイント定義、リクエスト処理
- **services/**: ビジネスロジック、トランザクション管理
- **db/**: データアクセス、リポジトリパターン
- **agents/**: AI処理、自然言語解析
- **scheduler/**: 定期実行処理
- **core/**: 共通設定、ユーティリティ
- **models/**: データモデル定義

### データモデル関係
```
customer ────< opportunity >────< opportunity_user >──── user
                        │
                        └───< activity_log >──── user
                                     │
                                     └── activity_type
```

## 設計パターン

### リポジトリパターン
- データアクセスをリポジトリクラスに集約
- SQLModelを使用したORMアプローチ
- サービス層はリポジトリを介してのみDBアクセス

### 依存性注入
- FastAPIの依存性注入を活用
- DBセッション、設定などをDIで提供
- テスト容易性の向上

### サービスレイヤー
- ビジネスロジックをサービスクラスに集約
- トランザクション境界の管理
- 複数リポジトリの連携

### イベント駆動
- Slack Eventをトリガーとした処理
- スケジューラーによる定期イベント
