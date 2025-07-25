#!/usr/bin/env python3
"""
ツール活用事例検索サイト - メインアプリケーション
Flask製のWebアプリケーションで、複数のブログプラットフォームから記事を検索し、
結果をSQLiteデータベースとオプションでGoogleスプレッドシートに保存します。
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# 自作モジュールのインポート
from services.search_service import SearchService
from services.storage_service import StorageService
from database.init_db import initialize_database

# 環境変数の読み込み
load_dotenv()

def create_app(testing=False):
    """
    Flaskアプリケーションファクトリ
    
    Args:
        testing (bool): テスト環境フラグ
    
    Returns:
        Flask: 設定済みのFlaskアプリケーション
    """
    app = Flask(__name__)
    
    # アプリケーション設定
    configure_app(app, testing)
    
    # ログ設定
    configure_logging(app)
    
    # データベース初期化
    if not testing:
        initialize_database()
    
    # サービス初期化
    search_service = SearchService()
    storage_service = StorageService()
    
    # ルート定義
    register_routes(app, search_service, storage_service)
    
    return app

def configure_app(app, testing=False):
    """
    アプリケーション設定
    
    Args:
        app (Flask): Flaskアプリケーション
        testing (bool): テスト環境フラグ
    """
    # 基本設定
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # データベース設定
    if testing:
        app.config['DATABASE_PATH'] = ':memory:'
    else:
        app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'app.db')
    
    # Google Sheets設定（オプション）
    app.config['GSHEET_ID'] = os.getenv('GSHEET_ID')
    app.config['SHEET_NAME'] = os.getenv('SHEET_NAME', 'Sheet1')
    app.config['CREDENTIALS_JSON'] = os.getenv('CREDENTIALS_JSON', 'credentials.json')
    
    # キャッシュ設定
    app.config['CACHE_EXPIRE_HOURS'] = int(os.getenv('CACHE_EXPIRE_HOURS', '1'))
    
    # テスト環境設定
    app.config['TESTING'] = testing

def configure_logging(app):
    """
    ログ設定
    
    Args:
        app (Flask): Flaskアプリケーション
    """
    if not app.config['TESTING']:
        # ログレベル設定
        log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
        
        # ログフォーマット
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # ファイルハンドラー
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # アプリケーションロガー設定
        app.logger.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # Werkzeugログレベル調整
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

def register_routes(app, search_service, storage_service):
    """
    ルート登録
    
    Args:
        app (Flask): Flaskアプリケーション
        search_service (SearchService): 検索サービス
        storage_service (StorageService): ストレージサービス
    """
    
    @app.route('/')
    def index():
        """
        ホームページ（検索フォーム）
        
        Returns:
            str: レンダリングされたHTMLテンプレート
        """
        app.logger.info("ホームページにアクセスされました")
        return render_template('index.html')
    
    @app.route('/search', methods=['POST'])
    def search():
        """
        検索実行
        
        Returns:
            str: 検索結果ページまたはリダイレクト
        """
        tool_name = request.form.get('tool_name', '').strip()
        
        # バリデーション
        if not tool_name:
            flash('ツール名を入力してください', 'error')
            return redirect(url_for('index'))
        
        app.logger.info(f"検索実行: {tool_name}")
        
        try:
            # 検索実行
            articles = search_service.search_articles(tool_name)
            
            # 検索結果をデータベースに保存
            search_result = {
                'search_query': tool_name,
                'articles': articles,
                'search_date': datetime.now(),
                'total_count': len(articles)
            }
            
            # ストレージに保存
            storage_success = storage_service.save_search_result(search_result)
            
            if not storage_success:
                app.logger.warning("検索結果の保存に失敗しました")
                flash('検索結果の保存に失敗しましたが、検索は完了しました', 'warning')
            
            app.logger.info(f"検索完了: {len(articles)}件の記事が見つかりました")
            
            # プラットフォーム別の記事数を計算
            from collections import Counter
            platform_counts = Counter(article.platform for article in articles)
            platform_stats = {platform: count for platform, count in platform_counts.items()}
            
            return render_template('results.html', 
                                 tool_name=tool_name,
                                 articles=articles,
                                 total_count=len(articles),
                                 platform_stats=platform_stats)
        
        except Exception as e:
            app.logger.error(f"検索エラー: {str(e)}")
            flash('検索中にエラーが発生しました。しばらく時間をおいて再試行してください。', 'error')
            return redirect(url_for('index'))
    
    @app.route('/history')
    def history():
        """
        検索履歴表示
        
        Returns:
            str: 検索履歴ページ
        """
        app.logger.info("検索履歴ページにアクセスされました")
        
        try:
            search_history = storage_service.get_search_history()
            
            # 統計情報の計算
            total_articles = sum(h['total_articles'] for h in search_history) if search_history else 0
            unique_tools = len(set(h['search_query'].lower() for h in search_history)) if search_history else 0
            
            # 今週の検索数
            one_week_ago = datetime.now() - timedelta(days=7)
            recent_searches = sum(1 for h in search_history if h['search_date'] > one_week_ago) if search_history else 0
            
            return render_template('history.html', 
                                 search_history=search_history,
                                 total_articles=total_articles,
                                 unique_tools=unique_tools,
                                 recent_searches=recent_searches)
        
        except Exception as e:
            app.logger.error(f"検索履歴取得エラー: {str(e)}")
            flash('検索履歴の取得に失敗しました', 'error')
            return render_template('history.html', 
                                 search_history=[],
                                 total_articles=0,
                                 unique_tools=0,
                                 recent_searches=0)
    
    @app.route('/history/<int:search_id>')
    def history_detail(search_id):
        """
        特定の検索結果詳細
        
        Args:
            search_id (int): 検索履歴ID
        
        Returns:
            str: 検索結果詳細ページ
        """
        app.logger.info(f"検索履歴詳細ページにアクセス: ID={search_id}")
        
        try:
            search_result = storage_service.get_search_result_by_id(search_id)
            
            if not search_result:
                flash('指定された検索結果が見つかりません', 'error')
                return redirect(url_for('history'))
            
            return render_template('results.html',
                                 tool_name=search_result['search_query'],
                                 articles=search_result['articles'],
                                 total_count=search_result['total_count'],
                                 search_date=search_result['search_date'],
                                 platform_stats=search_result.get('platform_stats', {}),
                                 is_history=True)
        
        except Exception as e:
            app.logger.error(f"検索履歴詳細取得エラー: {str(e)}")
            flash('検索結果の取得に失敗しました', 'error')
            return redirect(url_for('history'))
    
    @app.route('/health')
    def health_check():
        """
        ヘルスチェックエンドポイント
        
        Returns:
            dict: ヘルスチェック結果
        """
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found_error(error):
        """
        404エラーハンドラー
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            tuple: エラーページとステータスコード
        """
        app.logger.warning(f"404エラー: {request.url}")
        return render_template('error.html', 
                             error_code=404,
                             error_message='ページが見つかりません'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        500エラーハンドラー
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            tuple: エラーページとステータスコード
        """
        app.logger.error(f"500エラー: {str(error)}")
        return render_template('error.html',
                             error_code=500,
                             error_message='内部サーバーエラーが発生しました'), 500

# アプリケーション作成
app = create_app()

if __name__ == '__main__':
    # 開発サーバー起動
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.logger.info(f"アプリケーションを起動します (ポート: {port}, デバッグ: {debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)