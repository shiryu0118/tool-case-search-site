# ツール活用事例検索サイト デプロイメントガイド

このガイドでは、ツール活用事例検索サイトを本番環境にデプロイする方法について説明します。

## デプロイ方法の選択

このアプリケーションは以下の方法でデプロイできます：

1. **Render.com** - 推奨される方法（自動デプロイ対応）
2. **Docker** - どのホスティングプラットフォームでも使用可能
3. **手動デプロイ** - 従来のサーバーへの直接デプロイ

## 1. Render.com へのデプロイ（推奨）

### 前提条件

- Render.com アカウント
- GitHubリポジトリ（このコードがプッシュされている）

### デプロイ手順

1. **Render.com にログイン**:
   - [Render Dashboard](https://dashboard.render.com/) にアクセスしてログイン

2. **Blueprint を使用したデプロイ**:
   - 「New +」ボタンをクリックし、「Blueprint」を選択
   - GitHubリポジトリを接続
   - `render.yaml` ファイルのパスを確認（ルートディレクトリにあるはず）
   - 「Apply Blueprint」をクリックしてデプロイを開始

3. **環境変数の設定**:
   - デプロイ後、サービスの「Environment」タブに移動
   - 以下の環境変数を設定：
     - `SECRET_KEY`: 安全なランダム文字列（自動生成可能）
     - `DATABASE_PATH`: `/data/app.db`
     - `LOG_LEVEL`: `INFO`（本番環境では）
     - `FLASK_DEBUG`: `false`（本番環境では）
     - `CACHE_EXPIRE_HOURS`: `1`（または必要に応じて調整）
     - `GSHEET_ID`: Google スプレッドシートの ID（オプション）
     - `SHEET_NAME`: シート名（デフォルト: `Sheet1`）
     - `CREDENTIALS_JSON_CONTENT`: Google サービスアカウントの認証情報（オプション）

4. **ディスクストレージの設定**:
   - 「Disks」タブに移動
   - 「Add Disk」をクリックして以下の設定でディスクを追加：
     - Name: `data`
     - Mount Path: `/data`
     - Size: `1 GB`（必要に応じて調整）

5. **デプロイの確認**:
   - 「Overview」タブでデプロイステータスを確認
   - デプロイが完了したら、提供されたURLでアプリケーションにアクセス

### CI/CD の設定

GitHub Actions を使用して自動デプロイを設定するには：

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」に移動
2. 以下のシークレットを追加：
   - `RENDER_API_KEY`: Render.com の API キー
   - `RENDER_SERVICE_ID`: デプロイしたサービスの ID

これにより、`.github/workflows/deploy.yml` で定義された CI/CD パイプラインが有効になります。

## 2. Docker を使用したデプロイ

### 前提条件

- Docker と Docker Compose がインストールされているサーバー
- Git（コードの取得用）

### デプロイ手順

1. **コードの取得**:
   ```bash
   git clone <repository-url>
   cd tool-case-search-site
   ```

2. **環境変数の設定**:
   ```bash
   cp .env.sample .env
   # .env ファイルを編集して必要な環境変数を設定
   ```

3. **Docker イメージのビルドと起動**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **デプロイの確認**:
   ```bash
   docker-compose ps
   # アプリケーションが正常に実行されていることを確認
   ```

詳細な Docker デプロイ手順については、`docker-README.md` を参照してください。

## 3. 手動デプロイ

### 前提条件

- Python 3.11 以上がインストールされているサーバー
- pip（Python パッケージマネージャー）
- Git（コードの取得用）

### デプロイ手順

1. **コードの取得**:
   ```bash
   git clone <repository-url>
   cd tool-case-search-site
   ```

2. **仮想環境の作成と依存関係のインストール**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **環境変数の設定**:
   ```bash
   cp .env.sample .env
   # .env ファイルを編集して必要な環境変数を設定
   ```

4. **データベースの初期化**:
   ```bash
   python -c "from database.init_db import initialize_database; initialize_database()"
   ```

5. **アプリケーションの起動**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
   ```

6. **Nginx または Apache の設定**（オプション）:
   - リバースプロキシとして Nginx または Apache を設定
   - HTTPS を有効化
   - 静的ファイルの提供を最適化

## 本番環境のベストプラクティス

### セキュリティ

1. **環境変数の保護**:
   - 本番環境の `SECRET_KEY` は強力でランダムな値を使用
   - API キーや認証情報は環境変数として安全に保存

2. **HTTPS の有効化**:
   - Render.com は自動的に HTTPS を提供
   - 他の環境では Let's Encrypt などを使用して SSL/TLS を設定

3. **アクセス制限**:
   - 必要に応じて IP 制限やベーシック認証を設定

### パフォーマンス

1. **キャッシュの最適化**:
   - `CACHE_EXPIRE_HOURS` を適切な値に設定
   - 必要に応じて Redis などの外部キャッシュを導入

2. **ワーカー数の調整**:
   - サーバーのリソースに応じて Gunicorn ワーカー数を調整
   - `--workers` オプションで設定（通常はCPUコア数 × 2 + 1）

3. **データベースのバックアップ**:
   - 定期的なバックアップを設定
   - Render.com のディスクは永続的ですが、追加のバックアップを推奨

### モニタリング

1. **ログの確認**:
   - Render.com のログダッシュボードを使用
   - `LOG_LEVEL` を適切に設定

2. **ヘルスチェック**:
   - `/health` エンドポイントを定期的に監視
   - 監視サービス（UptimeRobot など）の設定を検討

## トラブルシューティング

### 一般的な問題

1. **アプリケーションが起動しない**:
   - ログを確認して具体的なエラーを特定
   - 環境変数が正しく設定されているか確認
   - 依存関係が正しくインストールされているか確認

2. **データベースエラー**:
   - データベースパスとアクセス権限を確認
   - 以下のコマンドでデータベースを再初期化：
     ```bash
     python -c "from database.init_db import initialize_database; initialize_database()"
     ```

3. **API 統合の問題**:
   - 外部 API へのアクセスが可能か確認
   - レート制限に達していないか確認
   - 認証情報が正しいか確認

### Render.com 特有の問題

1. **ディスクマウントの問題**:
   - ディスクが正しく設定されているか確認
   - アプリケーションが `/data` ディレクトリに書き込み権限を持っているか確認

2. **環境変数の問題**:
   - 機密情報が正しく設定されているか確認
   - 変更後にサービスを再起動

3. **デプロイ失敗**:
   - ビルドログを確認して具体的なエラーを特定
   - リポジトリが最新の状態か確認
   - `render.yaml` ファイルに構文エラーがないか確認

## 更新とメンテナンス

1. **コードの更新**:
   - GitHub リポジトリに変更をプッシュ
   - CI/CD パイプラインが自動的にデプロイ（設定されている場合）

2. **手動更新**:
   - Render.com ダッシュボードで「Manual Deploy」をクリック
   - Docker 環境の場合：
     ```bash
     git pull
     docker-compose down
     docker-compose build
     docker-compose up -d
     ```

3. **定期的なメンテナンス**:
   - 依存パッケージの更新
   - データベースのバックアップ
   - ログの確認と分析

## サポートとリソース

- **Render.com ドキュメント**: [Render Docs](https://render.com/docs)
- **Flask ドキュメント**: [Flask Documentation](https://flask.palletsprojects.com/)
- **Docker ドキュメント**: [Docker Documentation](https://docs.docker.com/)

問題が解決しない場合は、プロジェクトの GitHub リポジトリで Issue を作成してください。