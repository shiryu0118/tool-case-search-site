# 設計書

## 概要

Flask製のツール活用事例検索サイトは、複数のブログプラットフォーム（Zenn、Qiita、はてなブログ）から記事を検索し、結果をSQLiteデータベースに保存し、オプションでGoogleスプレッドシートにも保存するWebアプリケーションです。

## アーキテクチャ

### システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask App     │    │  External APIs  │
│                 │◄──►│                 │◄──►│                 │
│  - 検索UI       │    │  - ルーティング │    │  - Zenn API     │
│  - 結果表示     │    │  - ビジネス     │    │  - Qiita API    │
│  - 履歴表示     │    │    ロジック     │    │  - はてなブログ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Data Storage   │
                       │                 │
                       │ - Google Sheets │
                       │ - SQLite DB     │
                       └─────────────────┘
```

### 技術スタック

- **フレームワーク**: Flask 2.x
- **テンプレートエンジン**: Jinja2
- **データベース**: SQLite3
- **外部ストレージ**: Google Sheets API v4
- **HTTPクライアント**: requests + requests-cache
- **HTMLパーサー**: BeautifulSoup4
- **コード整形**: Black + isort
- **デプロイ**: Docker + Render
- **CI/CD**: GitHub Actions

## コンポーネントと インターフェース

### 1. Webアプリケーション層

#### app.py (メインアプリケーション)
```python
# 主要ルート
- GET /              # ホームページ（検索フォーム）
- POST /search       # 検索実行
- GET /history       # 検索履歴表示
- GET /history/<id>  # 特定の検索結果詳細
```

#### templates/
- `base.html` - ベーステンプレート
- `index.html` - 検索フォーム
- `results.html` - 検索結果表示
- `history.html` - 検索履歴一覧

#### static/
- `css/style.css` - スタイルシート
- `js/main.js` - フロントエンドJavaScript

### 2. ビジネスロジック層

#### services/search_service.py
```python
class SearchService:
    def search_articles(self, tool_name: str) -> List[Article]
    def _search_zenn(self, query: str) -> List[Article]
    def _search_qiita(self, query: str) -> List[Article]
    def _search_hatena(self, query: str) -> List[Article]
```

#### services/storage_service.py
```python
class StorageService:
    def save_search_result(self, search_result: SearchResult) -> bool
    def _save_to_sqlite(self, data: dict) -> bool
    def _save_to_google_sheets(self, data: dict) -> bool  # オプション
    def get_search_history(self) -> List[SearchResult]
    def initialize_database(self) -> bool
```

### 3. データアクセス層

#### models/article.py
```python
@dataclass
class Article:
    title: str
    url: str
    platform: str
    published_date: Optional[datetime]
    summary: Optional[str]
```

#### models/search_result.py
```python
@dataclass
class SearchResult:
    id: Optional[int]
    search_query: str
    articles: List[Article]
    search_date: datetime
    total_count: int
```

### 4. 外部API統合層

#### integrations/zenn_client.py
```python
class ZennClient:
    def search_articles(self, query: str) -> List[Article]
```

#### integrations/qiita_client.py
```python
class QiitaClient:
    def search_articles(self, query: str) -> List[Article]
```

#### integrations/hatena_client.py
```python
class HatenaClient:
    def search_articles(self, query: str) -> List[Article]
```

#### integrations/google_sheets_client.py
```python
class GoogleSheetsClient:
    def append_row(self, values: List[str]) -> bool
    def get_credentials(self) -> Credentials
```

## データモデル

### SQLiteスキーマ

```sql
-- 検索履歴テーブル
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_query TEXT NOT NULL,
    search_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_articles INTEGER DEFAULT 0
);

-- 記事テーブル
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_history_id INTEGER,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL,
    published_date DATETIME,
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_history_id) REFERENCES search_history (id)
);

-- インデックス
CREATE INDEX idx_search_query ON search_history(search_query);
CREATE INDEX idx_platform ON articles(platform);
CREATE INDEX idx_url ON articles(url);
```

### Googleスプレッドシート構造

| 列名 | 説明 |
|------|------|
| A: 検索日時 | 検索実行日時 |
| B: 検索キーワード | 入力されたツール名 |
| C: 記事タイトル | 見つかった記事のタイトル |
| D: URL | 記事のURL |
| E: プラットフォーム | Zenn/Qiita/はてなブログ |
| F: 公開日 | 記事の公開日 |

## エラーハンドリング

### エラー分類と対応

1. **外部API エラー**
   - レート制限: 指数バックオフで再試行
   - タイムアウト: 他のプラットフォーム検索を継続
   - 認証エラー: ログ出力してスキップ

2. **データ保存エラー**
   - SQLite書き込み失敗: エラーログ出力とユーザーへの通知
   - Google Sheets API失敗: ログ出力のみ（SQLiteが成功していれば処理継続）

3. **バリデーションエラー**
   - 空の検索クエリ: フロントエンドでバリデーション
   - 不正なURL: ログ出力してスキップ

### ログ設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## テスト戦略

### テストピラミッド

1. **ユニットテスト** (70%)
   - 各サービスクラスのメソッド
   - データモデルのバリデーション
   - ユーティリティ関数

2. **統合テスト** (20%)
   - 外部API統合
   - データベース操作
   - Google Sheets連携

3. **E2Eテスト** (10%)
   - 検索フローの完全テスト
   - UI操作テスト

### テストツール

- **pytest**: テストフレームワーク
- **pytest-mock**: モック作成
- **responses**: HTTP リクエストモック
- **pytest-cov**: カバレッジ測定

### テスト環境

```python
# conftest.py
@pytest.fixture
def test_app():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_external_apis():
    # 外部API呼び出しをモック化
    pass
```

## セキュリティ考慮事項

1. **認証情報管理**
   - Google サービスアカウントキーの安全な保存
   - 環境変数での機密情報管理
   - .gitignoreでの認証ファイル除外

2. **入力検証**
   - XSS対策: Jinja2の自動エスケープ
   - SQLインジェクション対策: パラメータ化クエリ
   - CSRF対策: Flask-WTFの使用

3. **レート制限**
   - requests-cacheでの1時間キャッシュ
   - 外部API呼び出し頻度制限

## パフォーマンス最適化

1. **キャッシュ戦略**
   - HTTP レスポンスキャッシュ (1時間)
   - データベースクエリ最適化
   - 静的ファイルのブラウザキャッシュ

2. **非同期処理**
   - 複数プラットフォーム検索の並列実行
   - バックグラウンドでのデータ保存

3. **データベース最適化**
   - 適切なインデックス設定
   - クエリの最適化

## デプロイメント設計

### Docker設定

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### 環境変数

```bash
# 必須
GSHEET_ID=your_google_sheet_id
SECRET_KEY=your_secret_key

# オプション
SHEET_NAME=Sheet1
CREDENTIALS_JSON=credentials.json
DATABASE_URL=sqlite:///app.db
```

### CI/CD パイプライン

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          # Render API経由でデプロイ実行
```