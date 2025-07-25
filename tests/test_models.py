"""
モデルのユニットテスト
"""

import pytest
from datetime import datetime
from models.article import Article
from models.search_result import SearchResult


class TestArticle:
    """Articleモデルのテスト"""
    
    def test_valid_article_creation(self):
        """有効なパラメータでArticleが作成できることを確認"""
        article = Article(
            title="テスト記事",
            url="https://example.com/test",
            platform="zenn",
            published_date=datetime(2023, 1, 1),
            summary="テスト記事の概要"
        )
        
        assert article.title == "テスト記事"
        assert article.url == "https://example.com/test"
        assert article.platform == "zenn"
        assert article.published_date == datetime(2023, 1, 1)
        assert article.summary == "テスト記事の概要"
    
    def test_article_without_optional_fields(self):
        """オプションフィールドなしでArticleが作成できることを確認"""
        article = Article(
            title="テスト記事",
            url="https://example.com/test",
            platform="qiita"
        )
        
        assert article.title == "テスト記事"
        assert article.url == "https://example.com/test"
        assert article.platform == "qiita"
        assert article.published_date is None
        assert article.summary is None
    
    def test_article_with_empty_title(self):
        """空のタイトルでArticleが作成できないことを確認"""
        with pytest.raises(ValueError, match="タイトルは必須です"):
            Article(
                title="",
                url="https://example.com/test",
                platform="zenn"
            )
    
    def test_article_with_empty_url(self):
        """空のURLでArticleが作成できないことを確認"""
        with pytest.raises(ValueError, match="URLは必須です"):
            Article(
                title="テスト記事",
                url="",
                platform="zenn"
            )
    
    def test_article_with_empty_platform(self):
        """空のプラットフォームでArticleが作成できないことを確認"""
        with pytest.raises(ValueError, match="プラットフォームは必須です"):
            Article(
                title="テスト記事",
                url="https://example.com/test",
                platform=""
            )
    
    def test_article_with_invalid_url(self):
        """無効なURLでArticleが作成できないことを確認"""
        with pytest.raises(ValueError, match="URLは有効な形式である必要があります"):
            Article(
                title="テスト記事",
                url="invalid-url",
                platform="zenn"
            )


class TestSearchResult:
    """SearchResultモデルのテスト"""
    
    def test_valid_search_result_creation(self):
        """有効なパラメータでSearchResultが作成できることを確認"""
        articles = [
            Article(
                title="テスト記事1",
                url="https://example.com/test1",
                platform="zenn"
            ),
            Article(
                title="テスト記事2",
                url="https://example.com/test2",
                platform="qiita"
            )
        ]
        
        search_date = datetime.now()
        search_result = SearchResult(
            search_query="テスト",
            articles=articles,
            search_date=search_date,
            total_count=2,
            id=1
        )
        
        assert search_result.search_query == "テスト"
        assert search_result.articles == articles
        assert search_result.search_date == search_date
        assert search_result.total_count == 2
        assert search_result.id == 1
    
    def test_search_result_without_id(self):
        """IDなしでSearchResultが作成できることを確認"""
        articles = [
            Article(
                title="テスト記事",
                url="https://example.com/test",
                platform="zenn"
            )
        ]
        
        search_date = datetime.now()
        search_result = SearchResult(
            search_query="テスト",
            articles=articles,
            search_date=search_date,
            total_count=1
        )
        
        assert search_result.search_query == "テスト"
        assert search_result.articles == articles
        assert search_result.search_date == search_date
        assert search_result.total_count == 1
        assert search_result.id is None
    
    def test_search_result_with_empty_query(self):
        """空の検索クエリでSearchResultが作成できないことを確認"""
        articles = [
            Article(
                title="テスト記事",
                url="https://example.com/test",
                platform="zenn"
            )
        ]
        
        with pytest.raises(ValueError, match="検索クエリは必須です"):
            SearchResult(
                search_query="",
                articles=articles,
                search_date=datetime.now(),
                total_count=1
            )
    
    def test_search_result_with_negative_count(self):
        """負の記事数でSearchResultが作成できないことを確認"""
        articles = []
        
        with pytest.raises(ValueError, match="記事数は0以上である必要があります"):
            SearchResult(
                search_query="テスト",
                articles=articles,
                search_date=datetime.now(),
                total_count=-1
            )
    
    def test_search_result_with_mismatched_count(self):
        """記事数と記事リストの長さが一致しない場合にSearchResultが作成できないことを確認"""
        articles = [
            Article(
                title="テスト記事",
                url="https://example.com/test",
                platform="zenn"
            )
        ]
        
        with pytest.raises(ValueError, match="記事リストの長さと記事数が一致しません"):
            SearchResult(
                search_query="テスト",
                articles=articles,
                search_date=datetime.now(),
                total_count=2
            )