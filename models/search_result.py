"""
検索結果データモデル
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from .article import Article


@dataclass
class SearchResult:
    """検索結果を表すデータクラス"""
    search_query: str
    articles: List[Article]
    search_date: datetime
    total_count: int
    id: Optional[int] = None
    
    def __post_init__(self):
        """データバリデーション"""
        if not self.search_query or not self.search_query.strip():
            raise ValueError("検索クエリは必須です")
            
        if self.total_count < 0:
            raise ValueError("記事数は0以上である必要があります")
            
        if len(self.articles) != self.total_count:
            raise ValueError("記事リストの長さと記事数が一致しません")