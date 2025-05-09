
# CI/CD設計方針

本ドキュメントは、営業オポチュニティマネジメント AIアシスタントシステムのCI/CD設計方針を示す。

---

## 🎯 設計目的

- CI: テスト・Lint・ビルド確認を自動化
- CD: コンテナイメージをGitHub Container RegistryにPush
- デプロイ処理はこのリポジトリの責務外（外部プロセスで管理）

---

## ✅ CI構成

| 項目 | 内容 |
|------|------|
| 実行環境 | GitHub Actions runner (ubuntu-latest) |
| 実行タイミング | `push`, `pull_request` 時 |
| 実行内容 | |
|  | 1. `docker-compose up --build` |
|  | 2. `docker-compose exec app pytest` |
|  | 3. `docker-compose exec app black --check` |
|  | 4. `docker-compose exec app flake8` |
| 成功条件 | pytest / black / flake8 が全てパス |

### CI目的
- コード品質の維持
- テスト全通過の確認
- Docker環境内での実行保証

---

## ✅ CD構成

| 項目 | 内容 |
|------|------|
| 実行環境 | GitHub Actions runner (ubuntu-latest) |
| 実行タイミング | `main` ブランチ push または `tag` push 時 |
| 実行内容 | |
|  | 1. `docker build` |
|  | 2. `docker tag` |
|  | 3. `docker push ghcr.io/USERNAME/REPO:tag` |
| レジストリ | GitHub Container Registry (ghcr.io) |
| 成果物 | ghcr.io にバージョンタグ付きイメージ |

### CD目的
- コンテナイメージの一元管理
- デプロイ対象物のバージョン管理
- 外部システムからpull可能な状態の提供

---

## ✅ Docker構成

必要ファイル：

- `Dockerfile`: アプリ用ビルド定義
- `docker-compose.yml`: テスト実行用（app + postgres）

CI/CD pipelineでは `docker-compose` を用いてアプリ・DBを同時起動し、コンテナ内でpytest/lintを実行する。

---

## ✅ 設計意図

- CI/CDとも **Dockerを中心とした一貫性ある環境** に統一
- 開発／本番の実行環境差異を最小化
- デプロイ処理自体は本リポジトリの責務外とすることでシンプル化

---

以上
