"""
リントコマンド集の実行スクリプト
"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def run_command(command):
    """コマンドを実行し結果を表示する"""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
        
    return result.returncode




def run_flake8():
    """Flake8の実行"""
    print("== Running Flake8 ==")
    returncode = run_command(["flake8", "src", "tests"])
    return returncode


def run_black_check():
    """Blackのチェックモード実行"""
    print("== Running Black (check mode) ==")
    returncode = run_command(["black", "--check", "src", "tests"])
    return returncode


def run_isort_check():
    """isortのチェックモード実行"""
    print("== Running isort (check mode) ==")
    returncode = run_command(["isort", "--check", "src", "tests"])
    return returncode


def run_dependency_check():
    """依存関係チェックの実行"""
    print("== Checking Dependency Rules ==")
    from scripts.check_dependencies import main as check_deps
    try:
        check_deps()
        return 0
    except SystemExit as e:
        return e.code

def run_all_linters():
    """すべてのリンターを実行"""
    print("Running all linters...")
    results = []

    results.append(run_flake8())
    results.append(run_black_check())
    results.append(run_isort_check())
    results.append(run_dependency_check())

    # エラーが1つでもあれば終了コード1を返す
    if any(result != 0 for result in results):
        sys.exit(1)

    print("All linters passed!")
    sys.exit(0)


if __name__ == "__main__":
    run_all_linters()