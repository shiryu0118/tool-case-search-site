#!/bin/bash

# Docker環境でアプリケーションを実行するスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# プロジェクトルートに移動
cd "$PROJECT_ROOT"

# .envファイルが存在するか確認
if [ ! -f .env ]; then
    echo "環境変数ファイル (.env) が見つかりません。.env.sampleをコピーして作成します。"
    cp .env.sample .env
    echo ".envファイルを作成しました。必要に応じて編集してください。"
fi

# Dockerコンテナを起動
echo "Dockerコンテナを起動しています..."
docker-compose up -d

echo "アプリケーションが起動しました。http://localhost:5000 にアクセスしてください。"
echo "ログを表示するには: docker-compose logs -f"
echo "コンテナを停止するには: docker-compose down"