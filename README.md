# ツール活用事例検索サイト

複数のブログプラットフォーム（Zenn、Qiita、はてなブログ）から技術記事を横断検索できるWebアプリケーションです。

## 🚀 機能

- **横断検索**: 複数のプラットフォームから一度に記事を検索
- **検索履歴**: 過去の検索結果を保存・参照
- **Google Sheets連携**: 検索結果をスプレッドシートに保存（オプション）
- **キャッシュ機能**: 外部API呼び出しを最適化
- **レスポンシブデザイン**: モバイル対応

## 🛠️ 技術スタック

- **Backend**: Python 3.11+, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render.com (無料プラン対応)
- **CI/CD**: GitHub Actions

## 📦 デプロイ

### Render.com (推奨)

1. このリポジトリをGitHubにプッシュ
2. [Render.com](https://render.com)でアカウント作成
3. 「New +」→「Blueprint」を選択
4. GitHubリポジトリを接続
5. 自動デプロイ開始

詳細は [docs/deployment_guide.md](docs/deployment_guide.md) を参照してください。

### ローカル実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.sample .env

# アプリケーション起動
python app.py
```

## 🧪 テスト

```bash
# 全テスト実行
python run_tests.py all

# ユニットテストのみ
python run_tests.py unit

# 統合テストのみ
python run_tests.py integration
```

## 📚 ドキュメント

- [デプロイメントガイド](docs/deployment_guide.md)
- [Render無料プラン設定](docs/render_free_plan.md)
- [CI/CDガイド](docs/ci_cd_guide.md)
- [E2Eテストガイド](docs/e2e_testing_guide.md)

## 🔧 開発

```bash
# 開発環境でのDocker起動
docker-compose -f docker-compose.yml up --build

# コードフォーマット
python -m black .
python -m isort .
```

## 📄 ライセンス

MIT License