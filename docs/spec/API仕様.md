
# API仕様

本ドキュメントは、営業オポチュニティマネジメント AIアシスタントシステムのAPI仕様を示す。

対象API:
- Slack Botからの入力受付
- オポチュニティ情報の取得・管理
- アクティビティログの記録
- 内部通知（スケジューラー用）

---

## 🎯 API一覧

| メソッド | パス                | 説明                           |
| -------- | ------------------- | ------------------------------ |
| POST     | /slack/events       | Slack Event APIエンドポイント  |
| GET      | /opportunity/{id}   | オポチュニティ詳細取得         |
| POST     | /opportunity        | オポチュニティ新規作成         |
| PUT      | /opportunity/{id}   | オポチュニティ更新             |
| DELETE   | /opportunity/{id}   | オポチュニティ削除             |
| GET      | /opportunity/search | オポチュニティ検索             |
| POST     | /activity_log       | アクティビティログ記録         |
| POST     | /notify/progress    | 進捗確認の通知送信（内部API）  |
| POST     | /notify/kpi         | KPI達成促進通知送信（内部API） |

---

## ✅ POST /slack/events

### 説明
Slack Event APIからのイベントを受信する。

⚠️ verification challenge対応必須：初回リクエストで `{"type": "url_verification", "challenge": "xxxx"}` が届くため、`challenge` の値をそのままレスポンスする。

### リクエストパラメータ
Slack Event APIの仕様に従う。特記事項なし。

### リクエスト例
```json
{
  "type": "message",
  "event": {
    "user": "U12345678",
    "text": "A社に訪問しました。",
    "channel": "D87654321",
    "ts": "1680000000.000100"
  }
}
```

### レスポンス例
200 OK（verification challenge時は `challenge` の文字列を返す）

---

## ✅ GET /opportunity/{id}

（※ GETなのでリクエストボディなし）

### レスポンス例
```json
{
  "id": "op123",
  "customer": {"id": "c001", "name": "株式会社ABC"},
  "title": "Webシステム導入",
  "amount": 5000000,
  "stage": {"id": 2, "name": "提案"},
  "expected_close_date": "2024-06-01",
  "owners": [{"id": "u001", "name": "田中太郎"}],
  "collaborators": [{"id": "u002", "name": "佐藤花子"}],
  "created_at": "2024-04-10T12:00:00Z",
  "updated_at": "2024-04-20T09:00:00Z"
}
```

---

## ✅ POST /opportunity

### 説明
新規オポチュニティを作成。

### リクエストパラメータ

| 名称                | 型            | 説明                     |
| ------------------- | ------------- | ------------------------ |
| customer_id         | UUID          | 顧客ID                   |
| title               | string        | 案件名                   |
| amount              | number        | 案件金額                 |
| stage_id            | int           | ステージID               |
| expected_close_date | date          | 予想クロージング日       |
| owners              | array[string] | 主担当ユーザーIDリスト   |
| collaborators       | array[string] | 共同担当ユーザーIDリスト |

### リクエスト例
```json
{
  "customer_id": "c001",
  "title": "新システム導入",
  "amount": 4000000,
  "stage_id": 1,
  "expected_close_date": "2024-07-01",
  "owners": ["u001"],
  "collaborators": ["u002", "u003"]
}
```

### レスポンス例
201 Created
```json
{
  "id": "op456"
}
```

---

## ✅ PUT /opportunity/{id}

### 説明
オポチュニティ情報を更新。

### リクエストパラメータ

| 名称                | 型     | 説明                             |
| ------------------- | ------ | -------------------------------- |
| stage_id            | int    | 更新後ステージID（任意）         |
| amount              | number | 更新後金額（任意）               |
| title               | string | 更新後タイトル（任意）           |
| expected_close_date | date   | 更新後予想クロージング日（任意） |

※ 任意項目のみ送信。未指定項目は変更なし。

### リクエスト例
```json
{
  "stage_id": 2,
  "amount": 4500000
}
```

### レスポンス例
200 OK

---

## ✅ DELETE /opportunity/{id}

（※ DELETEなのでリクエストボディなし）

### レスポンス例
204 No Content

---

## ✅ GET /opportunity/search

### 説明
オポチュニティ検索API

### クエリパラメータ

| 名称        | 型     | 説明                   |
| ----------- | ------ | ---------------------- |
| customer_id | UUID   | 顧客ID                 |
| title       | string | 案件名部分一致         |
| stage_id    | int    | ステージID             |
| from_date   | date   | 予想クロージング日開始 |
| to_date     | date   | 予想クロージング日終了 |

### レスポンス例
```json
[
  {
    "id": "op123",
    "customer": {"id": "c001", "name": "株式会社ABC"},
    "title": "Webシステム導入",
    "amount": 5000000,
    "stage": {"id": 2, "name": "提案"},
    "expected_close_date": "2024-06-01"
  },
  {
    "id": "op456",
    "customer": {"id": "c001", "name": "株式会社ABC"},
    "title": "クラウド移行",
    "amount": 8000000,
    "stage": {"id": 1, "name": "見込み"},
    "expected_close_date": "2024-07-10"
  }
]
```

---

## ✅ POST /activity_log

### 説明
アクティビティログを記録。

### リクエストパラメータ

| 名称             | 型     | 説明                 |
| ---------------- | ------ | -------------------- |
| opportunity_id   | UUID   | 対象オポチュニティID |
| user_id          | UUID   | 実施ユーザーID       |
| activity_type_id | int    | 活動種別ID           |
| action_date      | date   | 実施日               |
| comment          | string | コメント（任意）     |

### リクエスト例
```json
{
  "opportunity_id": "op123",
  "user_id": "u001",
  "activity_type_id": 1,
  "action_date": "2024-04-24",
  "comment": "A社訪問済み"
}
```

### レスポンス例
201 Created
```json
{
  "id": "act789"
}
```

---

## ✅ POST /notify/progress

### 説明
進捗確認の通知を送信する内部API。スケジューラーから定期的に呼び出される。

### リクエストパラメータ

| 名称        | 型   | 説明   |
| ----------- | ---- | ------ |
| target_date | date | 対象日 |

### リクエスト例
```json
{
  "target_date": "2024-04-24"
}
```

### レスポンス例
200 OK
```json
{
  "status": "completed",
  "target_date": "2024-04-24",
  "notifications_count": 5,
  "notifications_sent": 3,
  "notifications": [...]
}
```

---

## ✅ POST /notify/kpi

### 説明
KPI達成を促す通知を特定ユーザーに送信する内部API。スケジューラーから定期的に呼び出される。

### リクエストパラメータ

| 名称              | 型     | 説明                     |
| ----------------- | ------ | ------------------------ |
| user_slack_id     | string | 通知先ユーザーのSlack ID |
| message           | string | 通知メッセージ           |
| opportunity_id    | UUID   | 関連する案件ID（任意）   |
| opportunity_title | string | 関連する案件名（任意）   |

### リクエスト例
```json
{
  "user_slack_id": "U12345678",
  "message": "今週の会議数KPIが未達成です。あと2件の会議を設定しましょう。",
  "opportunity_id": "123e4567-e89b-12d3-a456-426614174000",
  "opportunity_title": "A社クラウド移行案件"
}
```

### レスポンス例
200 OK
```json
{
  "status": "completed",
  "success": true,
  "user_slack_id": "U12345678"
}
```

---

## 🔧 設定パラメータ

### 内部API接続設定

| 設定名       | 型     | 説明                       | デフォルト値          |
| ------------ | ------ | -------------------------- | --------------------- |
| API_BASE_URL | string | 内部API呼び出し用ベースURL | http://127.0.0.1:8000 |
| API_TIMEOUT  | float  | API呼び出しのタイムアウト  | 30.0（秒）            |

### スケジューラー設定

| 設定名                        | 型     | 説明                                 | デフォルト値 |
| ----------------------------- | ------ | ------------------------------------ | ------------ |
| SCHEDULER_TIMEZONE            | string | スケジューラーのタイムゾーン         | Asia/Tokyo   |
| SCHEDULER_PROGRESS_CHECK_CRON | string | 進捗確認実行スケジュール（cron形式） | 0 9 * * *    |
| SCHEDULER_KPI_CHECK_CRON      | string | KPI確認実行スケジュール（cron形式）  | 0 10 * * 1   |

### 通知条件設定

| 設定名                       | 型  | 説明                                       | デフォルト値 |
| ---------------------------- | --- | ------------------------------------------ | ------------ |
| NOTIFICATION_INACTIVITY_DAYS | int | この日数以上アクティビティがない場合に通知 | 3            |
| NOTIFICATION_RETRY_DAYS      | int | 通知後、この日数経過で再通知               | 2            |

### Slack通知設定

| 設定名                     | 型      | 説明                                         | デフォルト値 |
| -------------------------- | ------- | -------------------------------------------- | ------------ |
| SLACK_NOTIFICATION_CHANNEL | string  | 特定のチャンネルに通知する場合（空欄ならDM） | 空欄         |
| SLACK_MENTION_ON_CHANNEL   | boolean | チャンネル通知時にメンションをつけるか       | true         |


## 🚩 注意事項

- `/slack/events` は verification challenge 対応必須。
- `/notify/*` は内部APIとして外部非公開 or 認証保護すること。

---

以上
