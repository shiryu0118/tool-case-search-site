# ツール活用事例検索サイト - テスト

## テスト構成

このプロジェクトでは以下のテストを実装しています：

### ユニットテスト

- `test_models.py` - データモデルのテスト
  - Articleクラスのテスト
  - SearchResultクラスのテスト

- `test_services.py` - サービス層のテスト
  - SearchServiceのテスト
  - StorageServiceのテスト

- `test_integrations.py` - 外部API統合のテスト
  - GoogleSheetsClientのテスト

### 統合テスト

- `test_app.py` - Flaskアプリケーションのテスト
  - エンドポイントのテスト
  - データベース操作の統合テスト

- `test_api_integration.py` - 外部API統合のモックテスト
  - Zenn APIのモックテスト
  - Qiita APIのモックテスト
  - はてなブログのモックテスト
  - SearchServiceの統合テスト

- `test_cache.py` - キャッシュ機能のテスト
  - SearchServiceのキャッシュ機能テスト

## テストの実行方法

テストを実行するには、プロジェクトのルートディレクトリで以下のコマンドを実行します：

```bash
# ユニットテストのみ実行
python run_tests.py unit

# 統合テストのみ実行
python run_tests.py integration

# すべてのテストを実行
python run_tests.py all
```

## テスト環境

テストでは以下の環境を使用しています：

- pytest - テストフレームワーク
- unittest.mock - モック作成
- responses - HTTP リクエストのモック

## テストデータ

テストでは以下のフィクスチャを使用しています：

- `app` - テスト用のFlaskアプリケーション
- `client` - テスト用のFlaskクライアント
- `test_db` - テスト用のインメモリSQLiteデータベース
- `sample_articles` - テスト用のサンプル記事データ
- `sample_search_result` - テスト用のサンプル検索結果データ
- `mock_external_apis` - 外部APIをモック化するフィクスチャ