#!/usr/bin/env python3
"""
Step 7: 自检套件
用法: python3 check-self.py <ViewModel文件> <Screen文件>

检查项:
  7.1 ViewModel 方法可见性（除入口外均为 private）
  7.2 Screen 层只通过 onEvent/onIntent 调用 ViewModel
  7.3 Preview 数据完整性（无违规 emptyList()）
"""

import re
import sys
from pathlib import Path


def strip_strings_and_comments(text: str) -> str:
    """Remove string literals and comments to reduce false positives."""
    result = []
    in_single_str = False
    in_double_str = False
    i = 0
    while i < len(text):
        ch = text[i]
        # Escape sequences
        if ch == "\\" and i + 1 < len(text):
            result.append("  ")
            i += 2
            continue
        # Toggle string state
        if ch == '"' and not in_single_str:
            in_double_str = not in_double_str
            result.append(" ")  # replace string opening with space for token break
            i += 1
            continue
        if ch == "'" and not in_double_str:
            in_single_str = not in_single_str
            result.append(" ")
            i += 1
            continue
        # Skip string content
        if in_single_str or in_double_str:
            result.append(" ")
            i += 1
            continue
        # Skip line comments
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        # Skip block comments
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            i += 2
            while i < len(text):
                if text[i] == "*" and i + 1 < len(text) and text[i + 1] == "/":
                    i += 2
                    break
                i += 1
            continue
        result.append(ch)
        i += 1
    return "".join(result)


def check_visibility(vm_text: str, vm_file: str) -> list[str]:
    """7.1 ViewModel 方法可见性"""
    errors = []
    lines = vm_text.splitlines()
    public_methods = []

    for lineno, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        # Match "    fun xxx" or "    suspend fun xxx" that are not private/override
        m = re.match(r"^\s*(suspend\s+)?fun\s+(\w+)", stripped)
        if m:
            leading = raw_line[: len(raw_line) - len(raw_line.lstrip())]
            # Only count methods indented by 4 spaces (member level)
            if leading == "    " or leading == "\t":
                is_private = "private" in stripped
                is_override = "override" in stripped
                if not is_private and not is_override:
                    func_name = m.group(2)
                    if func_name not in ("onEvent", "onIntent", "onAction"):
                        public_methods.append(f"  {lineno}: {raw_line.rstrip()}")

    if public_methods:
        errors.append("=== 7.1 ViewModel 方法可见性 ===")
        errors.append("  ✗ 非 private 方法（除 onEvent/onIntent 外）:")
        errors.extend(public_methods)
    else:
        errors.append("=== 7.1 ViewModel 方法可见性 ===")
        errors.append("  ✓ 通过：无非公开方法（除 onEvent/onIntent 等入口外）")
    return errors


def check_screen_calls(screen_text: str) -> list[str]:
    """7.2 Screen 层事件调用
    注意：仅检测 viewModel.xxx 形式的直接调用。
    若开发者将 viewModel 赋值给局部变量后调用（如 val vm = viewModel; vm.logout()），
    脚本无法检测，需人工核查。
    """
    errors = []
    lines = screen_text.splitlines()
    found = []

    for lineno, raw_line in enumerate(lines, 1):
        stripped = strip_strings_and_comments(raw_line)
        # Look for viewModel.xxx calls that aren't uiState/uiEffect/onEvent
        for m in re.finditer(r"viewModel\.(\w+)", stripped):
            method = m.group(1)
            if method not in ("uiState", "uiEffect", "onEvent", "onIntent"):
                # Must exclude method references like viewModel::onEvent too
                full_line = raw_line.strip()
                if "::" not in full_line:
                    found.append(f"  {lineno}: {raw_line.rstrip()}")

    if found:
        errors.append("=== 7.2 Screen 层事件调用 ===")
        errors.append("  ✗ 存在直接调用 ViewModel 方法:")
        errors.extend(found)
    else:
        errors.append("=== 7.2 Screen 层事件调用 ===")
        errors.append("  ✓ 通过：Screen 层只通过 onEvent 调用 ViewModel")
    return errors


def find_preview_empty_lists(screen_text: str) -> list[str]:
    """7.3 Preview 数据完整性 - 检测 emptyList() 在 Preview 函数中"""
    errors = []
    lines = screen_text.splitlines()

    in_preview = False
    brace_depth = 0
    preview_start = 0
    entered_body = False  # True once we've seen at least one '{'

    for lineno, raw_line in enumerate(lines, 1):
        stripped = strip_strings_and_comments(raw_line)
        if not in_preview and "@Preview" in stripped:
            in_preview = True
            preview_start = lineno
            brace_depth = 0
            entered_body = False
            continue

        if in_preview:
            opens = stripped.count("{")
            closes = stripped.count("}")
            brace_depth += opens - closes
            if opens > 0:
                entered_body = True
            # Only exit when depth returns to <=0 AFTER having entered a body
            if entered_body and brace_depth <= 0:
                in_preview = False
                continue
            # Check for emptyList() usage
            if "emptyList()" in stripped or "emptyMap()" in stripped or "emptySet()" in stripped:
                errors.append(f"  {preview_start}: Preview 在第 {lineno} 行使用了 emptyList()/emptyMap()/emptySet()")

    return errors


def check_preview_data(screen_text: str) -> list[str]:
    """7.3 Preview 数据完整性"""
    errors = []
    empty_hits = find_preview_empty_lists(screen_text)

    errors.append("=== 7.3 Preview 数据完整性 ===")
    if empty_hits:
        errors.append("  ✗ Preview 中存在 emptyList()/emptyMap()/emptySet():")
        errors.extend(empty_hits)
    else:
        errors.append("  ✓ 通过：Preview 中无违规 emptyList()")
    return errors


def main():
    if len(sys.argv) != 3:
        print("用法: python3 check-self.py <ViewModel文件> <Screen文件>")
        sys.exit(1)

    vm_file, screen_file = sys.argv[1], sys.argv[2]

    if not Path(vm_file).exists():
        print(f"✗ 文件不存在: {vm_file}")
        sys.exit(1)
    if not Path(screen_file).exists():
        print(f"✗ 文件不存在: {screen_file}")
        sys.exit(1)

    vm_text = Path(vm_file).read_text(encoding="utf-8")
    screen_text = Path(screen_file).read_text(encoding="utf-8")

    all_pass = True
    output_lines: list[str] = []

    for check_name, check_fn, text, path in [
        ("ViewModel 方法可见性", lambda t: check_visibility(t, vm_file), vm_text, vm_file),
        ("Screen 层事件调用", check_screen_calls, screen_text, screen_file),
        ("Preview 数据完整性", check_preview_data, screen_text, screen_file),
    ]:
        result = check_fn(text)
        output_lines.extend(result)
        if any("✗" in line for line in result):
            all_pass = False

    print("\n".join(output_lines))
    print()
    if all_pass:
        print("✓ 全部自检通过")
        sys.exit(0)
    else:
        print("✗ 存在未通过项，请修复后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
