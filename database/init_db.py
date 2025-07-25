#!/usr/bin/env python3
"""
データベース初期化スクリプト
SQLiteデータベースの作成とスキーマの適用を行います。
"""

import sqlite3
import os
import logging
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_path():
    """データベースファイルのパスを取得"""
    # 環境変数から取得、デフォルトはapp.db
    db_path = os.getenv('DATABASE_PATH', 'app.db')
    return db_path

def get_schema_path():
    """スキーマファイルのパスを取得"""
    current_dir = Path(__file__).parent
    schema_path = current_dir / 'schema.sql'
    return schema_path

def initialize_database(db_path=None, schema_path=None):
    """
    データベースを初期化する
    
    Args:
        db_path (str, optional): データベースファイルのパス
        schema_path (str, optional): スキーマファイルのパス
    
    Returns:
        bool: 初期化が成功した場合True
    """
    if db_path is None:
        db_path = get_database_path()
    
    if schema_path is None:
        schema_path = get_schema_path()
    
    try:
        # スキーマファイルの存在確認
        if not os.path.exists(schema_path):
            logger.error(f"スキーマファイルが見つかりません: {schema_path}")
            return False
        
        # データベース接続
        logger.info(f"データベースを初期化中: {db_path}")
        conn = sqlite3.connect(db_path)
        
        try:
            # スキーマファイルを読み込み
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # スキーマを実行
            conn.executescript(schema_sql)
            conn.commit()
            
            logger.info("データベースの初期化が完了しました")
            
            # テーブル作成確認
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.info(f"作成されたテーブル: {[table[0] for table in tables]}")
            
            return True
            
        except sqlite3.Error as e:
            logger.error(f"データベース初期化エラー: {e}")
            return False
            
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        return False

def check_database_exists(db_path=None):
    """
    データベースファイルの存在確認
    
    Args:
        db_path (str, optional): データベースファイルのパス
    
    Returns:
        bool: データベースファイルが存在する場合True
    """
    if db_path is None:
        db_path = get_database_path()
    
    return os.path.exists(db_path)

def verify_database_schema(db_path=None):
    """
    データベーススキーマの検証
    
    Args:
        db_path (str, optional): データベースファイルのパス
    
    Returns:
        bool: スキーマが正しい場合True
    """
    if db_path is None:
        db_path = get_database_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 必要なテーブルの存在確認
        required_tables = ['search_history', 'articles']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        for table in required_tables:
            if table not in existing_tables:
                logger.error(f"必要なテーブルが見つかりません: {table}")
                return False
        
        # インデックスの存在確認
        required_indexes = [
            'idx_search_query',
            'idx_platform', 
            'idx_url',
            'idx_search_history_id',
            'idx_published_date',
            'idx_created_at'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        existing_indexes = [index[0] for index in cursor.fetchall()]
        
        for index in required_indexes:
            if index not in existing_indexes:
                logger.warning(f"インデックスが見つかりません: {index}")
        
        conn.close()
        logger.info("データベーススキーマの検証が完了しました")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"スキーマ検証エラー: {e}")
        return False

def main():
    """メイン関数 - スクリプトとして実行された場合の処理"""
    logger.info("データベース初期化スクリプトを開始します")
    
    db_path = get_database_path()
    
    # データベースが既に存在するかチェック
    if check_database_exists(db_path):
        logger.info(f"データベースファイルが既に存在します: {db_path}")
        
        # スキーマ検証
        if verify_database_schema(db_path):
            logger.info("既存のデータベーススキーマは正常です")
        else:
            logger.warning("既存のデータベーススキーマに問題があります")
    
    # データベース初期化実行
    if initialize_database(db_path):
        logger.info("データベース初期化が正常に完了しました")
        
        # 検証実行
        if verify_database_schema(db_path):
            logger.info("データベーススキーマの検証が成功しました")
        else:
            logger.error("データベーススキーマの検証が失敗しました")
    else:
        logger.error("データベース初期化が失敗しました")

if __name__ == '__main__':
    main()