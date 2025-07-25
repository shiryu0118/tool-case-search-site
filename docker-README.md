# Docker環境でのツール活用事例検索サイトの実行

このドキュメントでは、Docker環境でツール活用事例検索サイトを実行する方法を説明します。

## 前提条件

以下のソフトウェアがインストールされている必要があります：

- Docker
- Docker Compose

## 環境構築

### 1. 環境変数の設定

`.env.sample`ファイルをコピーして`.env`ファイルを作成し、必要に応じて環境変数を編集します：

```bash
cp .env.sample .env
```

### 2. Dockerイメージのビルド

以下のコマンドでDockerイメージをビルドします：

```bash
docker-compose build
```

### 3. アプリケーションの起動

以下のコマンドでアプリケーションを起動します：

```bash
docker-compose up -d
```

アプリケーションは http://localhost:5000 でアクセスできます。

### 4. ログの確認

以下のコマンドでアプリケーションのログを確認できます：

```bash
docker-compose logs -f
```

### 5. アプリケーションの停止

以下のコマンドでアプリケーションを停止します：

```bash
docker-compose down
```

## 開発環境

### 開発用コンテナの起動

開発用ツールを含むコンテナを起動するには、以下のコマンドを実行します：

```bash
docker-compose --profile dev up -d
```

### テストの実行

Docker環境でテストを実行するには、以下のコマンドを実行します：

```bash
# すべてのテストを実行
docker-compose run --rm dev-tools python run_tests.py all

# ユニットテストのみ実行
docker-compose run --rm dev-tools python run_tests.py unit

# 統合テストのみ実行
docker-compose run --rm dev-tools python run_tests.py integration
```

### コード整形

Docker環境でコード整形を実行するには、以下のコマンドを実行します：

```bash
# Blackによるコード整形
docker-compose run --rm dev-tools black .

# isortによるインポート整形
docker-compose run --rm dev-tools isort .
```

## データの永続化

アプリケーションのデータは`data-volume`という名前のDockerボリュームに保存されます。このボリュームは`docker-compose down`コマンドを実行しても削除されません。

ボリュームを削除するには、以下のコマンドを実行します：

```bash
docker-compose down -v
```

## トラブルシューティング

### アプリケーションにアクセスできない

- ポート5000が他のアプリケーションで使用されていないか確認してください。
- `docker-compose ps`コマンドでコンテナが正常に起動しているか確認してください。
- `docker-compose logs app`コマンドでエラーメッセージを確認してください。

### データベースエラー

- `docker-compose exec app python -c "from database.init_db import initialize_database; initialize_database()"`コマンドでデータベースを再初期化してください。