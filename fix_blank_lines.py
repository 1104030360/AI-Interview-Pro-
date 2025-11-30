#!/usr/bin/env python3
"""
自動修復 Markdown 文件中代碼塊和列表周圍缺少空行的問題
"""
import re
from pathlib import Path

def fix_blank_lines(file_path):
    """在代碼塊和列表前後添加空行"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    lines = content.split('\n')
    result_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        prev_line = lines[i-1] if i > 0 else ''
        next_line = lines[i+1] if i < len(lines) - 1 else ''
        
        # 檢查是否是代碼塊開始
        if line.strip().startswith('```'):
            # 在代碼塊前添加空行（如果前一行不是空的且不是列表項末尾）
            if prev_line.strip() and not result_lines[-1:] == ['']:
                result_lines.append('')
            result_lines.append(line)
            
            # 跳過代碼塊內容直到結束
            i += 1
            while i < len(lines):
                result_lines.append(lines[i])
                if lines[i].strip().startswith('```'):
                    # 代碼塊結束，檢查是否需要在後面添加空行
                    if i + 1 < len(lines) and lines[i+1].strip() and not lines[i+1].strip().startswith('```'):
                        result_lines.append('')
                    break
                i += 1
        else:
            result_lines.append(line)
        
        i += 1
    
    # 清理多餘的空行（超過2個連續空行合併為2個）
    final_lines = []
    empty_count = 0
    for line in result_lines:
        if line.strip() == '':
            empty_count += 1
            if empty_count <= 2:
                final_lines.append(line)
        else:
            empty_count = 0
            final_lines.append(line)
    
    new_content = '\n'.join(final_lines)
    
    if new_content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root = Path('/Users/linjunting/Desktop/專題python')
    md_files = list(root.glob('**/*.md'))
    
    # 排除某些目錄
    exclude_dirs = {'node_modules', '.venv', 'venv', '.git', '__pycache__', 'opencv-4.x'}
    md_files = [f for f in md_files if not any(ex in f.parts for ex in exclude_dirs)]
    
    fixed_count = 0
    for md_file in md_files:
        try:
            if fix_blank_lines(md_file):
                print(f'✓ 已修復: {md_file.relative_to(root)}')
                fixed_count += 1
        except Exception as e:
            print(f'✗ 錯誤 {md_file.relative_to(root)}: {e}')
    
    print(f'\n總計修復 {fixed_count} 個文件')

if __name__ == '__main__':
    main()
