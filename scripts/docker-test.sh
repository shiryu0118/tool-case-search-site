#!/bin/bash

# Docker環境でテストを実行するスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# プロジェクトルートに移動
cd "$PROJECT_ROOT"

# テストの種類を取得
TEST_TYPE=${1:-"all"}

# 開発用コンテナを起動
echo "開発用コンテナでテストを実行しています..."
docker-compose run --rm dev-tools python run_tests.py $TEST_TYPE

echo "テストが完了しました。"