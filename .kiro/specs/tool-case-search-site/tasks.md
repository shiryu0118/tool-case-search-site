# 実装計画

- [x] 1. プロジェクト構造とコア設定の作成





  - プロジェクトディレクトリ構造を作成（models、services、integrations、templates、static）
  - requirements.txtに必要なパッケージを定義
  - .env.sampleファイルと.gitignoreファイルを作成
  - _要件: 5.1, 5.2, 6.4_

- [x] 2. データモデルとバリデーションの実装





  - [x] 2.1 コアデータモデルの作成


    - models/article.py にArticleデータクラスを実装
    - models/search_result.py にSearchResultデータクラスを実装
    - データバリデーション機能を追加
    - _要件: 1.3, 3.2_

  - [x] 2.2 SQLiteデータベーススキーマの作成






    - database/schema.sqlファイルを作成してテーブル定義を実装
    - インデックスとリレーションシップを設定
    - database/init_db.pyスクリプトを作成してデータベース初期化機能を実装
    - _要件: 2.3, 3.1_

- [x] 3. 外部API統合の実装




  - [x] 3.1 Zenn API クライアントの実装


    - integrations/zenn_client.py を作成
    - 記事検索機能を実装
    - エラーハンドリングとレート制限対応を追加
    - _要件: 1.1, 4.3, 4.4_

  - [x] 3.2 Qiita API クライアントの実装


    - integrations/qiita_client.py を作成
    - 記事検索機能を実装
    - エラーハンドリングとレート制限対応を追加
    - _要件: 1.1, 4.3, 4.4_

  - [x] 3.3 はてなブログ検索クライアントの実装


    - integrations/hatena_client.py を作成
    - BeautifulSoup4を使用したスクレイピング機能を実装
    - エラーハンドリングとレート制限対応を追加
    - _要件: 1.1, 4.3, 4.4_

  - [x] 3.4 Google Sheets API クライアントの実装


    - integrations/google_sheets_client.py を作成
    - 認証とデータ書き込み機能を実装
    - エラーハンドリングとフォールバック機能を追加
    - _要件: 2.1, 2.2, 2.4_

- [x] 4. ビジネスロジック層の実装




  - [x] 4.1 検索サービスの実装


    - services/search_service.py を作成
    - 複数プラットフォーム検索の統合機能を実装
    - キャッシュ機能（requests-cache）を統合
    - _要件: 1.1, 1.2, 4.1, 4.2_

  - [x] 4.2 ストレージサービスの実装


    - services/storage_service.py にStorageServiceクラスを実装
    - SQLiteデータベースの初期化機能を実装
    - SQLiteへの検索結果保存機能を実装
    - 検索履歴取得機能を実装
    - オプションでGoogle Sheetsへの保存機能を追加
    - _要件: 2.1, 2.2, 2.3, 3.1, 3.2_

- [x] 5. Flaskアプリケーションの実装

  - [x] 5.1 メインアプリケーションの作成









    - app.py を作成してFlaskアプリケーションを初期化
    - 環境変数読み込みと設定管理を実装
    - ログ設定を実装
    - _要件: 5.1, 5.3, 5.4_

  - [x] 5.2 ルーティングとビューの実装



    - ホームページ（GET /）のルートを実装
    - 検索実行（POST /search）のルートを実装
    - 検索履歴（GET /history）のルートを実装
    - 検索結果詳細（GET /history/<id>）のルートを実装
    - _要件: 1.1, 1.2, 3.1, 3.3_

- [x] 6. フロントエンド実装







  - [x] 6.1 ベーステンプレートの作成





    - templates/base.html を作成
    - レスポンシブデザインのHTMLベースを実装
    - CSS/JSファイルの読み込み設定を追加
    - _要件: 1.3, 3.2_

  - [x] 6.2 検索フォームページの実装







    - templates/index.html を作成
    - 検索フォームUIを実装
    - フロントエンドバリデーションを追加
    - _要件: 1.1, 1.4_

  - [x] 6.3 検索結果表示ページの実装







    - templates/results.html を作成
    - 検索結果一覧表示機能を実装
    - ページネーション機能を追加
    - _要件: 1.2, 1.3, 1.4_

  - [x] 6.4 検索履歴ページの実装










    - templates/history.html を作成
    - 検索履歴一覧表示機能を実装
    - 詳細表示リンク機能を追加
    - _要件: 3.1, 3.2, 3.3, 3.4_

  - [x] 6.5 スタイルとJavaScriptの実装



    - static/css/style.css を作成してスタイリングを実装
    - static/js/main.js を作成してフロントエンド機能を実装
    - レスポンシブデザインを適用
    - _要件: 1.3, 3.2_

- [x] 7. テスト実装

  - [x] 7.1 ユニットテストの作成



    - tests/test_models.py でデータモデルのテストを実装
    - tests/test_services.py でサービス層のテストを実装
    - tests/test_integrations.py で外部API統合のテストを実装
    - _要件: 1.1, 2.1, 4.1_

  - [x] 7.2 統合テストの作成





    - tests/test_app.py でFlaskアプリケーションのテストを実装
    - データベース操作のテストを実装
    - 外部API統合のモックテストを実装
    - _要件: 1.2, 2.3, 4.4_

- [ ] 8. デプロイメント設定


  - [x] 8.1 Docker設定の作成







    - Dockerfileを作成してコンテナ設定を実装
    - docker-compose.ymlを作成してローカル開発環境を設定
    - .dockerignoreファイルを作成
    - _要件: 5.3, 6.2_

  - [x] 8.2 Render デプロイ設定









    - render.yamlを作成してBlueprint設定を実装
    - scripts/setup_render.sh を作成してCLI自動化を実装
    - 環境変数設定を文書化
    - _要件: 5.3, 6.2_

  - [x] 8.3 CI/CD パイプラインの実装



    - .github/workflows/deploy.yml を作成
    - 自動デプロイ機能を実装
    - コード品質チェック（Black、isort）を統合
    - _要件: 6.1, 6.2, 6.3_

- [x] 9. 統合とエンドツーエンドテスト



  - 全機能の統合テストを実行
  - 検索フローの完全テストを実装
  - パフォーマンステストを実行
  - エラーハンドリングの動作確認を実施
  - _要件: 1.1, 1.2, 2.1, 3.1, 4.1_