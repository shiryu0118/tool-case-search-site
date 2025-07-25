"""
記事データモデル
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """記事を表すデータクラス"""
    title: str
    url: str
    platform: str
    published_date: Optional[datetime] = None
    summary: Optional[str] = None
    
    def __post_init__(self):
        """データバリデーション"""
        if not self.title or not self.title.strip():
            raise ValueError("タイトルは必須です")
        
        if not self.url or not self.url.strip():
            raise ValueError("URLは必須です")
            
        if not self.platform or not self.platform.strip():
            raise ValueError("プラットフォームは必須です")
            
        # URLの基本的な形式チェック
        if not (self.url.startswith('http://') or self.url.startswith('https://')):
            raise ValueError("URLは有効な形式である必要があります")