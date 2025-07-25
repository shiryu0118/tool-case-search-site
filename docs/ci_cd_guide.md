# CI/CD パイプライン ガイド

このドキュメントでは、ツール活用事例検索サイトのCI/CDパイプラインについて説明します。

## 概要

CI/CDパイプラインは、GitHub Actionsを使用して以下の機能を提供します：

1. コード品質チェック（Black、isort、flake8）
2. 自動テスト実行
3. Render.comへの自動デプロイ

## ワークフロー

### 1. コード品質チェック

`.github/workflows/code-quality.yml`ファイルで定義されています。

- **トリガー**: プルリクエスト作成時、mainブランチへのプッシュ時
- **実行内容**:
  - Blackによるコードフォーマットチェック
  - isortによるインポート順序チェック
  - flake8による基本的なコードエラーチェック
  - プルリクエスト時にはreviewdogによるコメント自動追加

### 2. テスト実行

`.github/workflows/test.yml`ファイルで定義されています。

- **トリガー**: プルリクエスト作成時
- **実行内容**:
  - pytestによるテスト実行
  - テスト結果のプルリクエストへのコメント追加

### 3. デプロイ

`.github/workflows/deploy.yml`ファイルで定義されています。

- **トリガー**: mainブランチへのプッシュ時（テスト成功後のみ）
- **実行内容**:
  - Render CLIのインストール
  - Render.comへのデプロイ実行

## 設定方法

### GitHub Secretsの設定

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」に移動
2. 「New repository secret」をクリック
3. 以下のシークレットを追加:
   - `RENDER_API_KEY`: Render.comのAPIキー

### 手動でのコード整形

コードを手動で整形するには、以下のスクリプトを実行します：

- Linux/macOS: `./scripts/format_code.sh`
- Windows: `scripts\format_code.bat`

## トラブルシューティング

### CI/CDパイプラインが失敗する場合

1. **コード品質チェックの失敗**:
   - エラーメッセージを確認し、指摘された問題を修正
   - ローカルで`black .`と`isort .`を実行してコードを整形

2. **テストの失敗**:
   - テストログを確認して失敗したテストを特定
   - ローカルで`pytest`を実行して問題を再現

3. **デプロイの失敗**:
   - Render APIキーが正しく設定されているか確認
   - `render.yaml`ファイルの構文エラーをチェック

## カスタマイズ

CI/CDパイプラインをカスタマイズするには、`.github/workflows/`ディレクトリ内のYAMLファイルを編集します。

### コード品質チェックの調整

`pyproject.toml`ファイルでBlackとisortの設定を変更できます：

```toml
[tool.black]
line-length = 88  # 行の長さを変更する場合はここを編集

[tool.isort]
profile = "black"
line_length = 88  # 行の長さを変更する場合はここを編集
```