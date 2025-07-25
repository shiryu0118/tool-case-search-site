#!/usr/bin/env python3
"""
エンドツーエンドテストとパフォーマンステストを実行するスクリプト
"""

import os
import sys
import subprocess
import argparse
import time


def run_tests(test_type=None):
    """
    指定されたタイプのテストを実行する
    
    Args:
        test_type (str): 実行するテストのタイプ ('e2e', 'performance', 'integration', 'all')
    """
    start_time = time.time()
    
    # テストコマンドの構築
    cmd = ["pytest", "-v"]
    
    if test_type == "e2e":
        cmd.append("-m")
        cmd.append("e2e")
        print("エンドツーエンドテストを実行します...")
    elif test_type == "performance":
        cmd.append("-m")
        cmd.append("performance")
        print("パフォーマンステストを実行します...")
    elif test_type == "integration":
        cmd.append("-m")
        cmd.append("integration")
        print("統合テストを実行します...")
    elif test_type == "all":
        cmd.append("-m")
        cmd.append("e2e or performance or integration")
        print("すべてのエンドツーエンドテスト、パフォーマンステスト、統合テストを実行します...")
    else:
        print("有効なテストタイプを指定してください: e2e, performance, integration, all")
        sys.exit(1)
    
    # テストの実行
    try:
        result = subprocess.run(cmd, check=True)
        print(f"テスト実行が完了しました。所要時間: {time.time() - start_time:.2f}秒")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
        return e.returncode


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="エンドツーエンドテストとパフォーマンステストを実行するスクリプト")
    parser.add_argument("test_type", choices=["e2e", "performance", "integration", "all"],
                        help="実行するテストのタイプ")
    
    args = parser.parse_args()
    
    # 現在のディレクトリをプロジェクトルートに設定
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # テストの実行
    return run_tests(args.test_type)


if __name__ == "__main__":
    sys.exit(main())