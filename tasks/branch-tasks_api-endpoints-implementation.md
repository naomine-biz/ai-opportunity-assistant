# feature/api-endpoints-implementation ブランチのタスクリスト

## 1. APIエンドポイント定義の完成

- [x] **オポチュニティ管理APIの実装**
  - [x] GET `/opportunity/search/` - オポチュニティ検索（一覧取得）
  - [x] GET `/opportunity/{opportunity_id}` - 個別オポチュニティ取得
  - [x] POST `/opportunity` - オポチュニティ作成
  - [x] PUT `/opportunity/{opportunity_id}` - オポチュニティ更新
  - [x] DELETE `/opportunity/{opportunity_id}` - オポチュニティ削除
  - [x] エラーハンドリングの実装

- [x] **アクティビティログAPIの実装**
  - [x] POST `/activity_log` - アクティビティログ登録
  - [x] エラーハンドリングの実装

- [x] **Slackイベント受信APIの実装**
  - [x] POST `/slack/events` - Slackイベント受信エンドポイント
  - [x] Slack署名検証実装
  - [x] イベントタイプ別ハンドリング
  - [x] エラーハンドリングの実装

- [ ] **通知APIの完成**
  - [x] POST `/notify/progress` - 進捗通知処理（基本実装済み）
  - [ ] 通知サービス呼び出しの実装完了（TODOの対応）

## 2. スキーマ定義とバリデーションの実装

- [x] **リクエスト/レスポンススキーマの定義**
  - [x] オポチュニティ関連スキーマ（OpportunityCreate, OpportunityUpdate, OpportunityResponse, OpportunitySearchResponse）
  - [x] アクティビティログ関連スキーマ（ActivityLogCreate, ActivityLogResponse）
  - [x] ユーザー関連スキーマ（UserBase）
  - [x] 顧客関連スキーマ（CustomerBase）
  - [x] 通知関連スキーマ（NotificationRequest, NotificationResponse, NotificationRecipient）

- [x] **バリデーションルールの実装**
  - [x] 必須項目の検証（Pydanticモデルによる自動検証）
  - [x] フォーマット検証（日付、UUID等の型チェック）
  - [x] 基本的なビジネスルール（例：金額は0より大きい）

## 3. サービス層の実装

- [x] **オポチュニティサービスの実装**
  - [x] CRUD操作の実装（create_opportunity、get_opportunity_by_id、update_opportunity、delete_opportunity）
  - [x] オポチュニティ検索・フィルタリング機能（search_opportunities）
  - [x] ユーザー関連付け機能の実装（owner、collaborator関係）

- [x] **アクティビティサービスの実装**
  - [x] アクティビティ記録機能（create_activity_log）

- [ ] **通知サービスの完成**
  - [x] 進捗確認通知ロジックの実装（基本実装済み）
  - [ ] 実際の通知実行部分の実装

- [ ] **Slackサービスの基本実装**
  - [x] イベント処理機能（process_slack_event）- handlers.pyで実装
  - [x] URL検証チャレンジ処理（handle_slack_verification_challenge）- handlers.pyで実装
  - [ ] メッセージ送信機能 - bot.pyで実装予定
  - [ ] ユーザー情報取得機能 - bot.pyで実装予定

### Slack関連ファイルの責務分担
- `slack/handlers.py` - Slackからの**受信**処理（イベント処理、コマンド解析）
- `slack/bot.py` - Slackへの**送信**処理（メッセージ送信、ユーザー情報取得）※現在未実装
- `slack/models.py` - Slackデータ構造の定義

## 4. モックベースのテスト実装（基本レベル）

- [x] **APIルートのテスト**
  - [x] 通知ルートのテスト（基本実装済み）
  - [x] オポチュニティルートのテスト（GET, POST, PUT, DELETE, search全て実装済み）
  - [x] アクティビティルートのテスト（POST実装済み）
  - [x] Slackイベントルートのテスト（URL検証チャレンジ、メッセージイベント、署名検証の全てのテスト実装済み）

- [x] **サービス層のテスト**
  - [x] 通知サービスのテスト（基本実装済み）
  - [x] オポチュニティサービスのテスト
  - [x] アクティビティサービスのテスト
  - [x] Slackサービスのテスト（test_slack_handlers.pyで実装済み）

## 5. API仕様ドキュメント

- [ ] **FastAPI自動ドキュメント設定**
  - [ ] OpenAPI仕様の整備
  - [ ] エンドポイント説明の追加
  - [ ] リクエスト/レスポンス例の追加

- [ ] **エラーケースの文書化**
  - [ ] 各APIのエラーレスポンス定義
  - [ ] エラーコード一覧の整備

## 6. リファクタリングと最適化

- [x] **共通パターンの標準化**
  - [x] UUIDの直接使用によるID管理（実装済み）
  - [x] UTC日時の使用（実装済み）
  - [x] クエリ型の明示的指定（SelectOfScalarに変更済み）

- [ ] **コード品質向上**
  - [ ] linter警告の解消
  - [ ] 重複コードの排除
  - [ ] 命名規則の統一
