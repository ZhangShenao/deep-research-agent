#!/usr/bin/env python3
"""
代码静态分析脚本

用于辅助代码审查，检测常见的代码问题：
- 安全漏洞模式
- 代码复杂度
- 命名规范
- 代码风格

使用方法：
    python analyze_code.py <file_path>
    python analyze_code.py <file_path> --format json
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(str, Enum):
    """问题严重程度"""
    CRITICAL = "critical"  # 🔴 严重
    HIGH = "high"          # 🟠 高
    MEDIUM = "medium"      # 🟡 中
    LOW = "low"            # 🟢 低


class Category(str, Enum):
    """问题类别"""
    SECURITY = "security"           # 安全性
    PERFORMANCE = "performance"     # 性能
    READABILITY = "readability"     # 可读性
    BEST_PRACTICE = "best_practice" # 最佳实践


@dataclass
class Issue:
    """表示一个代码问题"""
    line: int
    column: int
    severity: Severity
    category: Category
    title: str
    description: str
    suggestion: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class PythonCodeAnalyzer:
    """Python 代码静态分析器"""

    def __init__(self, code: str, filename: str = "<string>"):
        self.code = code
        self.filename = filename
        self.lines = code.split('\n')
        self.issues: list[Issue] = []

    def analyze(self) -> list[Issue]:
        """执行所有分析"""
        self._check_security_patterns()
        self._check_ast_issues()
        self._check_style_issues()
        return sorted(self.issues, key=lambda x: (x.line, x.column))

    def _check_security_patterns(self):
        """检查安全漏洞模式"""
        security_patterns = [
            # SQL 注入
            (
                r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE|DROP).*\{.*\}',
                Severity.CRITICAL,
                "潜在 SQL 注入漏洞",
                "使用 f-string 构建 SQL 查询可能导致 SQL 注入攻击",
                "使用参数化查询，例如: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
            ),
            # 命令注入
            (
                r'os\.system\s*\(.*\+.*\)|subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True',
                Severity.CRITICAL,
                "潜在命令注入漏洞",
                "使用 shell=True 或字符串拼接执行命令可能导致命令注入",
                "使用参数列表而非 shell=True，避免字符串拼接"
            ),
            # 硬编码凭据
            (
                r'(?:password|passwd|pwd|secret|api_key|apikey|token)\s*=\s*["\'][^"\']+["\']',
                Severity.HIGH,
                "硬编码凭据",
                "代码中包含硬编码的敏感信息",
                "使用环境变量或配置文件存储敏感信息"
            ),
            # eval 使用
            (
                r'\beval\s*\(',
                Severity.HIGH,
                "使用 eval() 函数",
                "eval() 可能执行任意代码，存在安全风险",
                "考虑使用 ast.literal_eval() 或其他安全替代方案"
            ),
            # pickle 不安全反序列化
            (
                r'pickle\.loads?\s*\(',
                Severity.MEDIUM,
                "使用 pickle 反序列化",
                "pickle 反序列化不受信任的数据可能导致代码执行",
                "考虑使用 JSON 或其他安全的序列化格式"
            ),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, severity, title, desc, suggestion in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(Issue(
                        line=line_num,
                        column=0,
                        severity=severity,
                        category=Category.SECURITY,
                        title=title,
                        description=desc,
                        suggestion=suggestion
                    ))

    def _check_ast_issues(self):
        """使用 AST 检查代码结构问题"""
        try:
            tree = ast.parse(self.code)
        except SyntaxError as e:
            self.issues.append(Issue(
                line=e.lineno or 0,
                column=e.offset or 0,
                severity=Severity.CRITICAL,
                category=Category.READABILITY,
                title="语法错误",
                description=str(e.msg),
                suggestion="修复语法错误后重新分析"
            ))
            return

        for node in ast.walk(tree):
            # 检查函数复杂度
            if isinstance(node, ast.FunctionDef):
                self._check_function_complexity(node)
            
            # 检查 except 裸捕获
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.issues.append(Issue(
                        line=node.lineno,
                        column=node.col_offset,
                        severity=Severity.MEDIUM,
                        category=Category.BEST_PRACTICE,
                        title="裸 except 捕获",
                        description="except: 会捕获所有异常，包括 KeyboardInterrupt 和 SystemExit",
                        suggestion="指定具体的异常类型，如 except ValueError:"
                    ))

            # 检查 assert 在生产代码中的使用
            if isinstance(node, ast.Assert):
                self.issues.append(Issue(
                    line=node.lineno,
                    column=node.col_offset,
                    severity=Severity.LOW,
                    category=Category.BEST_PRACTICE,
                    title="使用 assert 语句",
                    description="assert 在 python -O 模式下会被忽略",
                    suggestion="对于输入验证，使用显式的条件判断和异常抛出"
                ))

    def _check_function_complexity(self, func: ast.FunctionDef):
        """检查函数复杂度"""
        # 检查函数行数
        if func.end_lineno and func.lineno:
            func_lines = func.end_lineno - func.lineno
            if func_lines > 50:
                self.issues.append(Issue(
                    line=func.lineno,
                    column=func.col_offset,
                    severity=Severity.MEDIUM,
                    category=Category.READABILITY,
                    title=f"函数 '{func.name}' 过长",
                    description=f"函数长度为 {func_lines} 行，超过建议的 50 行",
                    suggestion="考虑将函数拆分为更小的、职责单一的函数"
                ))

        # 检查参数数量
        num_args = len(func.args.args) + len(func.args.kwonlyargs)
        if num_args > 5:
            self.issues.append(Issue(
                line=func.lineno,
                column=func.col_offset,
                severity=Severity.LOW,
                category=Category.READABILITY,
                title=f"函数 '{func.name}' 参数过多",
                description=f"函数有 {num_args} 个参数，超过建议的 5 个",
                suggestion="考虑使用数据类或字典来组织相关参数"
            ))

        # 检查嵌套深度
        max_depth = self._get_max_nesting_depth(func)
        if max_depth > 4:
            self.issues.append(Issue(
                line=func.lineno,
                column=func.col_offset,
                severity=Severity.MEDIUM,
                category=Category.READABILITY,
                title=f"函数 '{func.name}' 嵌套过深",
                description=f"最大嵌套深度为 {max_depth} 层",
                suggestion="使用早返回（early return）或提取子函数来减少嵌套"
            ))

    def _get_max_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """计算最大嵌套深度"""
        max_depth = depth
        nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                child_depth = self._get_max_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_max_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth

    def _check_style_issues(self):
        """检查代码风格问题"""
        for line_num, line in enumerate(self.lines, 1):
            # 检查行长度
            if len(line) > 120:
                self.issues.append(Issue(
                    line=line_num,
                    column=120,
                    severity=Severity.LOW,
                    category=Category.READABILITY,
                    title="行过长",
                    description=f"行长度为 {len(line)} 字符，超过 120 字符",
                    suggestion="将长行拆分为多行"
                ))

            # 检查 TODO/FIXME
            if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                self.issues.append(Issue(
                    line=line_num,
                    column=0,
                    severity=Severity.LOW,
                    category=Category.BEST_PRACTICE,
                    title="未处理的标记",
                    description="发现 TODO/FIXME/XXX/HACK 标记",
                    suggestion="处理标记或创建相关的 issue 跟踪"
                ))


def format_text_report(issues: list[Issue], filename: str) -> str:
    """生成文本格式报告"""
    severity_icons = {
        Severity.CRITICAL: "🔴",
        Severity.HIGH: "🟠",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🟢"
    }

    if not issues:
        return f"✅ {filename}: 未发现问题"

    lines = [
        f"# 代码分析报告: {filename}",
        f"\n发现 {len(issues)} 个问题\n",
        "-" * 60
    ]

    for issue in issues:
        icon = severity_icons[issue.severity]
        lines.extend([
            f"\n{icon} [{issue.severity.value.upper()}] {issue.title}",
            f"   位置: 第 {issue.line} 行, 第 {issue.column} 列",
            f"   类别: {issue.category.value}",
            f"   描述: {issue.description}"
        ])
        if issue.suggestion:
            lines.append(f"   建议: {issue.suggestion}")

    return "\n".join(lines)


def format_json_report(issues: list[Issue], filename: str) -> str:
    """生成 JSON 格式报告"""
    return json.dumps({
        "filename": filename,
        "total_issues": len(issues),
        "issues": [issue.to_dict() for issue in issues]
    }, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Python 代码静态分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python analyze_code.py example.py
    python analyze_code.py example.py --format json
    cat code.py | python analyze_code.py -
        """
    )
    parser.add_argument("file", help="要分析的文件路径，使用 - 从标准输入读取")
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式 (default: text)"
    )
    
    args = parser.parse_args()

    # 读取代码
    if args.file == "-":
        code = sys.stdin.read()
        filename = "<stdin>"
    else:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"错误: 文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
        code = filepath.read_text(encoding="utf-8")
        filename = args.file

    # 分析代码
    analyzer = PythonCodeAnalyzer(code, filename)
    issues = analyzer.analyze()

    # 输出报告
    if args.format == "json":
        print(format_json_report(issues, filename))
    else:
        print(format_text_report(issues, filename))

    # 根据问题严重程度返回退出码
    if any(i.severity == Severity.CRITICAL for i in issues):
        sys.exit(2)
    elif any(i.severity == Severity.HIGH for i in issues):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

