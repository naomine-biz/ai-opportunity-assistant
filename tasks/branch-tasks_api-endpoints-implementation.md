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

- [x] **通知APIの完成**
  - [x] POST `/notify/progress` - 進捗通知処理の実装
  - [x] POST `/notify/kpi` - KPI達成促進通知の実装
  - [x] 通知サービス呼び出しの実装完了

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

- [x] **通知サービスのモック実装**
  - [x] 進捗確認通知ロジックの実装
  - [x] 通知実行部分のモック実装
  - [x] KPI達成促進通知のモック実装

- [x] **Slackサービスの基本モック実装**
  - [x] イベント処理機能（process_slack_event）- handlers.pyで実装
  - [x] URL検証チャレンジ処理（handle_slack_verification_challenge）- handlers.pyで実装
  - [x] メッセージ送信機能のモック - bot.pyで実装（`use_mock = True`）
  - [x] ユーザー情報取得機能のモック - bot.pyで実装（`use_mock = True`）

### Slack関連ファイルの責務分担
- `slack/handlers.py` - Slackからの**受信**処理（イベント処理、コマンド解析）
- `slack/bot.py` - Slackへの**送信**処理（メッセージ送信、ユーザー情報取得）
- `slack/models.py` - Slackデータ構造の定義

## 4. モックベースのテスト実装（基本レベル）

- [x] **APIルートのテスト**
  - [x] 通知ルートのテスト
  - [x] オポチュニティルートのテスト（GET, POST, PUT, DELETE, search全て実装済み）
  - [x] アクティビティルートのテスト（POST実装済み）
  - [x] Slackイベントルートのテスト（URL検証チャレンジ、メッセージイベント、署名検証の全てのテスト実装済み）

- [x] **サービス層のテスト**
  - [x] 通知サービスのテスト
  - [x] オポチュニティサービスのテスト
  - [x] アクティビティサービスのテスト
  - [x] Slackサービスのテスト（test_slack_handlers.pyとtest_slack_bot.pyで実装済み）

## 5. API仕様ドキュメント

- [x] **API仕様書の更新**
  - [x] 通知APIのパス修正（`/api/v1/notify/*`）
  - [x] レスポンススキーマの更新（`notifications_sent`フィールド追加）
  - [x] 設定パラメータの追加

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

- [x] **コード品質向上**
  - [x] linter警告の解消（実行済み）
  - [x] APIパス形式の統一
  - [x] スキーマ定義の整合性確保

## 7. 残課題

- [ ] **Slack通知サービスの本実装**
  - [ ] モック実装から実際のSlack Web API呼び出しへの移行（`use_mock = False`）
  - [ ] APIレート制限への対応
  - [ ] エラーハンドリングとリトライロジックの強化

- [ ] **通知機能の強化**
  - [ ] より柔軟な通知条件の実装（ユーザー設定に基づく頻度調整など）
  - [ ] マルチチャンネル通知（SlackとEmail）
  - [ ] 通知テンプレートの拡充

- [ ] **Slack Bot機能の拡張**
  - [ ] インタラクティブコンポーネント対応（ボタン、選択メニュー）
  - [ ] リッチメッセージフォーマット（カードUI）
  - [ ] Slack Web APIを使った高度な機能
