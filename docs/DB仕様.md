
# DB仕様

本ドキュメントは、営業オポチュニティマネジメント AIアシスタントシステムにおけるデータベース設計の仕様を示す。

以下に：
1. テーブル定義
2. エンティティ間リレーション
3. マスタ化しなかったフィールドとその理由
を記載する。

---

## 🎯 1️⃣ テーブル定義

### ✅ customer（顧客マスタ）

| カラム名   | 型          | 説明                     |
| ---------- | ----------- | ------------------------ |
| id         | UUID/SERIAL | 一意ID                   |
| name       | VARCHAR     | 顧客名                   |
| industry   | VARCHAR     | 業種（今回は文字列管理） |
| created_at | TIMESTAMP   | 作成日時                 |

---

### ✅ stage（案件ステージマスタ）

| カラム名   | 型        | 説明                               |
| ---------- | --------- | ---------------------------------- |
| id         | SERIAL    | 一意ID                             |
| name       | VARCHAR   | ステージ名（例：“見込み”、“提案”） |
| order_no   | INT       | ステージの順序                     |
| is_active  | BOOLEAN   | 有効フラグ                         |
| created_at | TIMESTAMP | 作成日時                           |

---

### ✅ activity_type（アクティビティ種別マスタ）

| カラム名   | 型        | 説明                                       |
| ---------- | --------- | ------------------------------------------ |
| id         | SERIAL    | 一意ID                                     |
| name       | VARCHAR   | 活動種別名（例：“訪問”、“電話”、“メール”） |
| is_active  | BOOLEAN   | 有効フラグ                                 |
| created_at | TIMESTAMP | 作成日時                                   |

---

### ✅ user（営業担当者）

| カラム名   | 型          | 説明           |
| ---------- | ----------- | -------------- |
| id         | UUID/SERIAL | 一意ID         |
| name       | VARCHAR     | 氏名           |
| email      | VARCHAR     | メールアドレス |
| slack_id   | VARCHAR     | SlackのUser ID |
| created_at | TIMESTAMP   | 作成日時       |

---

### ✅ opportunity（オポチュニティ）

| カラム名            | 型          | 説明                       |
| ------------------- | ----------- | -------------------------- |
| id                  | UUID/SERIAL | 一意ID                     |
| customer_id         | UUID        | 顧客ID（FK: customer.id）  |
| title               | VARCHAR     | 案件名                     |
| amount              | NUMERIC     | 案件金額                   |
| stage_id            | INT         | ステージID（FK: stage.id） |
| expected_close_date | DATE        | 予想クロージング日         |
| created_at          | TIMESTAMP   | 作成日時                   |
| updated_at          | TIMESTAMP   | 更新日時                   |

---

### ✅ opportunity_user（オポチュニティ担当者）

| カラム名       | 型          | 説明                                   |
| -------------- | ----------- | -------------------------------------- |
| id             | UUID/SERIAL | 一意ID                                 |
| opportunity_id | UUID        | オポチュニティID（FK: opportunity.id） |
| user_id        | UUID        | ユーザーID（FK: user.id）              |
| role           | VARCHAR     | 役割（“owner” or “collaborator”）      |
| created_at     | TIMESTAMP   | 作成日時                               |

---

### ✅ activity_log（アクティビティログ）

| カラム名         | 型          | 説明                                   |
| ---------------- | ----------- | -------------------------------------- |
| id               | UUID/SERIAL | 一意ID                                 |
| opportunity_id   | UUID        | オポチュニティID（FK: opportunity.id） |
| user_id          | UUID        | 実施者ID（FK: user.id）                |
| activity_type_id | INT         | 活動種別ID（FK: activity_type.id）     |
| action_date      | DATE        | 実施日                                 |
| comment          | TEXT        | 備考                                   |
| created_at       | TIMESTAMP   | 作成日時                               |

---

## 🎯 2️⃣ エンティティ間リレーション
```
customer ────< opportunity >────< opportunity_user >──── user
                        │
                        └───< activity_log >──── user
                                     │
                                     └── activity_type
```

- customer 1:N opportunity
- opportunity N:M user（中間テーブル: opportunity_user）
- opportunity 1:N activity_log
- activity_log N:1 activity_type
- activity_log N:1 user

---

## 🎯 3️⃣ マスタ化していないフィールドと設計意図

### ❌ user.department（部署）
- 現時点では分析軸として不要
- 営業担当者は部署単位ではなく個人単位で行動記録・分析を行う
- 組織の変化（組織改編や異動）に左右されないため初期設計に含めない
- 将来的に必要なら別テーブル or 属性追加可能

---

### ❌ opportunity.category（案件カテゴリ）
- 初期段階では案件カテゴリを手入力・明示入力させない
- 案件分類は将来的にクラスタリングやML分類結果から導出した方が“現場に合わせた分類”になりやすい
- 誤入力・不明入力のリスクを避けるため固定リスト入力・マスタ管理を今は行わない

---

### ❌ opportunity.source（案件流入元）
- 流入元を正確に入力させる運用フローが未確立
- 初期段階ではヒアリングや自由記述情報から後処理で分析する方が実態に即す
- 将来的に正規データ化する運用が定着した場合にマスタ管理を導入予定

---

## ✅ 設計方針まとめ

- 分析軸として確実に利用する顧客・ステージ・アクティビティ種別のみマスタ管理
- 他の分析軸は「後から発見」「将来的に必要に応じて導入」
- “無駄な正規化”を避け、シンプル・拡張性を残した構造とする

---

以上
