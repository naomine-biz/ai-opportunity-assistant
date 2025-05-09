#!/usr/bin/env python
"""
独自の依存関係チェックスクリプト
指定された依存関係ルールに違反するインポートがないかチェックする
"""
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# プロジェクトルートディレクトリ
ROOT_DIR = Path(__file__).parent.parent

# ソースディレクトリ
SRC_DIR = ROOT_DIR / "src"

# 依存関係ルール (source_module -> set(forbidden_modules))
DEPENDENCY_RULES: Dict[str, Set[str]] = {
    "api": {"slack", "db", "agents", "scheduler"},
    "slack": {"services", "db", "agents", "scheduler"},
    "services": {"api", "scheduler"},
    "scheduler": {"api", "slack", "db", "agents"},
    "db": {"api", "services", "agents", "slack", "scheduler"},
    "agents": {"api", "services", "db", "slack", "scheduler"},
}


class ImportVisitor(ast.NodeVisitor):
    """ASTノードビジタークラス: importを検出する"""

    def __init__(self):
        self.imports = []

    def visit_Import(self, node):
        """通常のimport文を処理"""
        for name in node.names:
            self.imports.append(name.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """from ... import文を処理"""
        if node.module is not None:
            self.imports.append(node.module)
        self.generic_visit(node)


def find_imports_in_file(file_path: Path) -> List[str]:
    """指定されたファイルからすべてのインポートを検索"""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
            visitor = ImportVisitor()
            visitor.visit(tree)
            return visitor.imports
        except SyntaxError:
            print(f"Syntax error in {file_path}")
            return []


def get_module_from_path(file_path: Path) -> str:
    """ファイルパスからモジュール名を取得"""
    rel_path = file_path.relative_to(SRC_DIR)
    parts = rel_path.parts
    return parts[0] if parts else ""


def check_dependencies() -> List[Tuple[str, str, str]]:
    """
    依存関係チェック実行
    
    Returns:
        List[Tuple[str, str, str]]: (違反ファイル, モジュール, 禁止されたインポート)
    """
    violations = []
    
    # Pythonファイルを探索
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_path = Path(root) / file
            if file == "__init__.py" and len(file_path.parent.parts) <= len(SRC_DIR.parts) + 1:
                # ルートの__init__.pyはスキップ
                continue
            
            # このファイルが属するモジュール
            module = get_module_from_path(file_path)
            if not module or module not in DEPENDENCY_RULES:
                continue
                
            # 禁止されているモジュール
            forbidden_modules = DEPENDENCY_RULES[module]
            
            # このファイルのインポート
            imports = find_imports_in_file(file_path)
            
            # ローカル（src）のインポートのみを考慮
            for imp in imports:
                parts = imp.split(".")
                if parts[0] in forbidden_modules:
                    rel_path = file_path.relative_to(ROOT_DIR)
                    violations.append((str(rel_path), module, parts[0]))
                    
    return violations


def main():
    """メイン実行関数"""
    print("依存関係をチェックしています...")
    violations = check_dependencies()
    
    if violations:
        print("\n依存関係の違反が見つかりました:")
        for file_path, module, forbidden in violations:
            print(f"ERROR: {file_path}: モジュール {module} から {forbidden} への依存は禁止されています")
        sys.exit(1)
    else:
        print("すべての依存関係ルールが守られています！")
        sys.exit(0)


if __name__ == "__main__":
    main()