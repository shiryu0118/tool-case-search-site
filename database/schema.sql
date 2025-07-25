-- ツール活用事例検索サイト データベーススキーマ
-- SQLite データベース用テーブル定義

-- 検索履歴テーブル
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_query TEXT NOT NULL,
    search_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_articles INTEGER DEFAULT 0
);

-- 記事テーブル
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_history_id INTEGER,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL,
    published_date DATETIME,
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_history_id) REFERENCES search_history (id) ON DELETE CASCADE
);

-- インデックス作成
-- 検索クエリでの高速検索用
CREATE INDEX IF NOT EXISTS idx_search_query ON search_history(search_query);

-- プラットフォーム別フィルタリング用
CREATE INDEX IF NOT EXISTS idx_platform ON articles(platform);

-- URL重複チェック用（UNIQUE制約があるが、検索性能向上のため）
CREATE INDEX IF NOT EXISTS idx_url ON articles(url);

-- 検索履歴IDでの記事検索用
CREATE INDEX IF NOT EXISTS idx_search_history_id ON articles(search_history_id);

-- 公開日での並び替え用
CREATE INDEX IF NOT EXISTS idx_published_date ON articles(published_date);

-- 作成日での並び替え用
CREATE INDEX IF NOT EXISTS idx_created_at ON articles(created_at);