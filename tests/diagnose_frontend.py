#!/usr/bin/env python3
"""
前端功能診斷腳本

檢查 index.html 中的 JavaScript 代碼是否有潛在問題
"""

import re
from pathlib import Path

def analyze_html(html_path):
    """分析 HTML 文件"""
    print("=" * 60)
    print("前端代碼診斷")
    print("=" * 60)

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []
    warnings = []

    # 1. 檢查 onclick 處理器
    print("\n1. 檢查 onclick 處理器...")
    onclick_handlers = re.findall(r'onclick="(\w+)\(\)"', content)
    print(f"   找到 {len(onclick_handlers)} 個 onclick 處理器:")
    for handler in set(onclick_handlers):
        print(f"   - {handler}()")

        # 檢查函數是否定義
        func_pattern = rf'function\s+{handler}\s*\('
        if not re.search(func_pattern, content):
            issues.append(f"函數 {handler}() 被調用但未定義")

    # 2. 檢查 DOMContentLoaded 事件
    print("\n2. 檢查 DOMContentLoaded 事件...")
    dom_ready = re.findall(r"addEventListener\('DOMContentLoaded'", content)
    print(f"   找到 {len(dom_ready)} 個 DOMContentLoaded 監聽器")
    if len(dom_ready) > 1:
        warnings.append(f"有 {len(dom_ready)} 個 DOMContentLoaded 監聽器（可能導致重複執行）")

    # 3. 檢查 script 標籤
    print("\n3. 檢查 <script> 標籤...")
    script_blocks = re.findall(r'<script[^>]*>[\s\S]*?</script>', content)
    print(f"   找到 {len(script_blocks)} 個 <script> 區塊")
    for i, block in enumerate(script_blocks, 1):
        lines = block.split('\n')
        print(f"   區塊 {i}: {len(lines)} 行")

    # 4. 檢查 getElementById 調用
    print("\n4. 檢查 getElementById 調用...")
    get_by_id = re.findall(r"getElementById\('([^']+)'\)", content)
    print(f"   找到 {len(get_by_id)} 個 getElementById 調用")
    unique_ids = set(get_by_id)
    print(f"   唯一 ID 數量: {len(unique_ids)}")

    # 檢查這些 ID 是否存在
    for elem_id in unique_ids:
        id_pattern = rf'id="{elem_id}"'
        if not re.search(id_pattern, content):
            issues.append(f"ID '{elem_id}' 被調用但在 HTML 中未找到")

    # 5. 檢查 API endpoints
    print("\n5. 檢查 API endpoint 調用...")
    api_calls = re.findall(r"fetch\('(/api/[^']+)'\)", content)
    print(f"   找到 {len(api_calls)} 個 API 調用:")
    for api in set(api_calls):
        print(f"   - {api}")

    # 6. 檢查 Jinja2 模板語法
    print("\n6. 檢查 Jinja2 模板語法...")
    jinja_vars = re.findall(r'\{\{\s*([^}]+)\s*\}\}', content)
    print(f"   找到 {len(jinja_vars)} 個 Jinja2 變數")

    # 檢查是否有語法錯誤（空格分開）
    bad_jinja = re.findall(r'\{\s+\{\s+([^}]+)\s+\}\s+\}', content)
    if bad_jinja:
        for var in bad_jinja:
            issues.append(f"Jinja2 語法錯誤: {{ {{ {var} }} }} (應該是 {{ {var} }})")

    # 7. 檢查 querySelector/querySelectorAll
    print("\n7. 檢查 querySelector 調用...")
    query_selectors = re.findall(r"querySelector(?:All)?\('([^']+)'\)", content)
    print(f"   找到 {len(query_selectors)} 個 querySelector 調用:")
    for selector in set(query_selectors):
        print(f"   - {selector}")

    # 8. 檢查全局函數定義
    print("\n8. 檢查全局函數定義...")
    functions = re.findall(r'(?:async\s+)?function\s+(\w+)\s*\(', content)
    print(f"   找到 {len(functions)} 個函數定義:")
    for func in set(functions):
        print(f"   - {func}()")

    # 總結
    print("\n" + "=" * 60)
    print("診斷結果")
    print("=" * 60)

    if issues:
        print(f"\n❌ 發現 {len(issues)} 個問題:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ 未發現嚴重問題")

    if warnings:
        print(f"\n⚠️  發現 {len(warnings)} 個警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")

    return issues, warnings


def check_button_handlers():
    """檢查按鈕處理器是否正確綁定"""
    print("\n" + "=" * 60)
    print("按鈕處理器檢查")
    print("=" * 60)

    html_path = Path(__file__).parent.parent / 'templates' / 'index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 檢查各個按鈕
    buttons = {
        'refreshBtn': {
            'type': 'addEventListener',
            'event': 'click',
            'handler': 'initRefreshBtn'
        },
        'btnStart': {
            'type': 'onclick',
            'handler': 'startSystem'
        },
        'btnStop': {
            'type': 'onclick',
            'handler': 'stopSystem'
        }
    }

    print("\n檢查按鈕綁定:")
    for btn_id, info in buttons.items():
        print(f"\n{btn_id}:")

        # 檢查按鈕是否存在
        if f'id="{btn_id}"' in content:
            print(f"  ✓ 按鈕元素存在")
        else:
            print(f"  ✗ 按鈕元素不存在")
            continue

        # 檢查處理器
        if info['type'] == 'onclick':
            if f'onclick="{info["handler"]}()"' in content:
                print(f"  ✓ onclick 處理器已設置")
            else:
                print(f"  ✗ onclick 處理器未設置")

            # 檢查函數定義
            if f'function {info["handler"]}' in content or f'async function {info["handler"]}' in content:
                print(f"  ✓ 函數 {info['handler']}() 已定義")
            else:
                print(f"  ✗ 函數 {info['handler']}() 未定義")

        elif info['type'] == 'addEventListener':
            if f'function {info["handler"]}' in content:
                print(f"  ✓ 函數 {info['handler']}() 已定義")
            else:
                print(f"  ✗ 函數 {info['handler']}() 未定義")


def main():
    """主函數"""
    html_path = Path(__file__).parent.parent / 'templates' / 'index.html'

    if not html_path.exists():
        print(f"錯誤: {html_path} 不存在")
        return 1

    print(f"分析文件: {html_path}\n")

    # 執行分析
    issues, warnings = analyze_html(html_path)

    # 檢查按鈕處理器
    check_button_handlers()

    print("\n" + "=" * 60)
    print("診斷完成")
    print("=" * 60)

    if issues:
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
