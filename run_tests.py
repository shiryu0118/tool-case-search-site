#!/usr/bin/env python3
"""
テスト実行スクリプト
"""

import os
import sys
import pytest


def main():
    """テストを実行"""
    print("ツール活用事例検索サイト - テスト実行")
    print("=" * 50)
    
    # テストディレクトリが存在することを確認
    if not os.path.exists('tests'):
        print("Error: testsディレクトリが見つかりません。")
        return 1
    
    # テストの種類を選択
    test_type = None
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    
    # pytestの引数を設定
    args = [
        '-v',                  # 詳細出力
        '--color=yes',         # カラー出力
    ]
    
    # テストの種類に応じてテストを実行
    if test_type == 'unit':
        print("ユニットテストを実行します...")
        args.extend(['tests/test_models.py', 'tests/test_services.py', 'tests/test_integrations.py'])
    elif test_type == 'integration':
        print("統合テストを実行します...")
        args.extend(['tests/test_app.py', 'tests/test_api_integration.py', 'tests/test_cache.py'])
    elif test_type == 'all':
        print("すべてのテストを実行します...")
        args.append('tests/')
    else:
        print("テストの種類を指定してください: unit, integration, all")
        print("例: python run_tests.py unit")
        return 1
    
    # その他のコマンドライン引数があれば追加
    if len(sys.argv) > 2:
        args.extend(sys.argv[2:])
    
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())