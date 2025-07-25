# エンドツーエンドテストガイド

このドキュメントでは、ツール活用事例検索サイトのエンドツーエンドテスト、統合テスト、パフォーマンステストの実行方法について説明します。

## テストの種類

### 1. エンドツーエンドテスト (E2E)

エンドツーエンドテストは、実際のブラウザを使用してユーザーの視点からアプリケーション全体の動作を検証します。

- **ファイル**: `tests/test_e2e_search_flow.py`
- **テスト内容**:
  - 検索フローの完全テスト
  - エラーハンドリングの動作確認

### 2. 統合テスト

統合テストは、複数のコンポーネントが連携して正しく動作することを検証します。

- **ファイル**: `tests/test_full_integration.py`
- **テスト内容**:
  - 検索サービスとストレージサービスの統合
  - エラーハンドリングの統合
  - Webフロー全体の統合

### 3. パフォーマンステスト

パフォーマンステストは、アプリケーションの応答時間やリソース使用量を検証します。

- **ファイル**: `tests/test_performance.py`
- **テスト内容**:
  - 検索機能のパフォーマンス
  - 履歴表示のパフォーマンス
  - データベース操作のパフォーマンス

## 前提条件

エンドツーエンドテストを実行するには、以下のソフトウェアが必要です：

1. Python 3.11以上
2. pytest
3. Selenium
4. ChromeDriver (または他のWebドライバー)

### 依存パッケージのインストール

```bash
pip install pytest selenium webdriver-manager
```

## テストの実行方法

### コマンドラインから直接実行

```bash
# エンドツーエンドテストのみ実行
pytest -m e2e

# 統合テストのみ実行
pytest -m integration

# パフォーマンステストのみ実行
pytest -m performance

# すべてのテストを実行
pytest -m "e2e or integration or performance"
```

### スクリプトを使用して実行

提供されているスクリプトを使用して、特定のタイプのテストを実行できます：

```bash
# Linuxの場合
python scripts/run_e2e_tests.py e2e
python scripts/run_e2e_tests.py integration
python scripts/run_e2e_tests.py performance
python scripts/run_e2e_tests.py all

# Windowsの場合
python scripts\run_e2e_tests.py e2e
python scripts\run_e2e_tests.py integration
python scripts\run_e2e_tests.py performance
python scripts\run_e2e_tests.py all
```

## Docker環境でのテスト実行

Docker環境でテストを実行するには、以下のコマンドを使用します：

```bash
# すべてのテストを実行
docker-compose run --rm dev-tools python scripts/run_e2e_tests.py all

# 特定のタイプのテストを実行
docker-compose run --rm dev-tools python scripts/run_e2e_tests.py e2e
docker-compose run --rm dev-tools python scripts/run_e2e_tests.py integration
docker-compose run --rm dev-tools python scripts/run_e2e_tests.py performance
```

## テスト結果の解釈

テスト実行後、以下の情報が表示されます：

- テストの成功/失敗状況
- パフォーマンステストの場合は応答時間の統計
- エラーが発生した場合はエラーメッセージと詳細情報

## トラブルシューティング

### Seleniumテストが失敗する場合

1. ChromeDriverのバージョンがインストールされているChromeのバージョンと一致していることを確認してください。
2. ヘッドレスモードでテストが失敗する場合は、`options.add_argument("--headless")`の行をコメントアウトして、ブラウザを表示モードで実行してみてください。
3. テスト中のタイミング問題が発生する場合は、`WebDriverWait`の待機時間を増やしてみてください。

### パフォーマンステストが失敗する場合

1. テスト環境のリソース（CPU、メモリ）が十分であることを確認してください。
2. 許容時間の閾値を調整してください（例：`assert avg_time < 1.0`の値を変更）。
3. 実行中の他のプロセスがテスト結果に影響を与えていないか確認してください。

## CI/CD環境でのテスト実行

GitHub Actionsでテストを実行するには、ワークフローファイル（`.github/workflows/test.yml`）に以下の設定を追加します：

```yaml
- name: Run E2E and Integration Tests
  run: |
    python -m pip install pytest selenium webdriver-manager
    python scripts/run_e2e_tests.py integration  # CI環境ではE2Eテストを除外
```

注意: CI環境では、ブラウザを必要とするE2Eテストは特別な設定が必要な場合があります。