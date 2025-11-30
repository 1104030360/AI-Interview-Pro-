#!/usr/bin/env python3
"""
自動修復 Markdown 文件中缺少語言標註的代碼塊
"""
import re
import sys
from pathlib import Path

def fix_fenced_code_blocks(file_path):
    """為沒有語言標註的代碼塊添加默認語言"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 匹配沒有語言標註的代碼塊（三個反引號後直接換行）
    # 不匹配已經有語言標註的（如 ```python, ```bash 等）
    pattern = r'^```\s*$'
    
    lines = content.split('\n')
    modified_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        # 檢查是否是代碼塊開始
        if line.strip() == '```':
            if not in_code_block:
                # 這是代碼塊開始，嘗試推斷語言
                # 檢查接下來幾行的內容來推斷語言
                lang = guess_language(lines, i + 1)
                modified_lines.append(f'```{lang}')
                in_code_block = True
            else:
                # 這是代碼塊結束
                modified_lines.append(line)
                in_code_block = False
        else:
            modified_lines.append(line)
    
    new_content = '\n'.join(modified_lines)
    
    if new_content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def guess_language(lines, start_idx):
    """根據代碼內容猜測語言"""
    # 檢查接下來的幾行
    sample_lines = []
    for i in range(start_idx, min(start_idx + 10, len(lines))):
        if lines[i].strip() == '```':
            break
        sample_lines.append(lines[i])
    
    sample = '\n'.join(sample_lines).lower()
    
    # 簡單的啟發式規則
    if any(word in sample for word in ['python', 'def ', 'import ', 'class ', 'pip install']):
        return 'python'
    elif any(word in sample for word in ['bash', 'cd ', 'ls ', 'mkdir', 'conda', 'npm', 'git']):
        return 'bash'
    elif any(word in sample for word in ['javascript', 'const ', 'let ', 'function', 'var ', '=>']):
        return 'javascript'
    elif any(word in sample for word in ['json', '{', '}']):
        return 'json'
    elif any(word in sample for word in ['typescript', 'interface ', 'type ']):
        return 'typescript'
    elif any(word in sample for word in ['sql', 'select ', 'insert ', 'create table']):
        return 'sql'
    elif any(word in sample for word in ['yaml', 'yml']):
        return 'yaml'
    elif any(word in sample for word in ['html', '<div', '<p>', '<html']):
        return 'html'
    elif any(word in sample for word in ['css', '{', '}']):
        return 'css'
    else:
        # 默認是文本
        return 'text'

def main():
    # 獲取所有 Markdown 文件
    root = Path('/Users/linjunting/Desktop/專題python')
    md_files = list(root.glob('**/*.md'))
    
    # 排除某些目錄
    exclude_dirs = {'node_modules', '.venv', 'venv', '.git', '__pycache__'}
    md_files = [f for f in md_files if not any(ex in f.parts for ex in exclude_dirs)]
    
    fixed_count = 0
    for md_file in md_files:
        try:
            if fix_fenced_code_blocks(md_file):
                print(f'✓ 已修復: {md_file.relative_to(root)}')
                fixed_count += 1
        except Exception as e:
            print(f'✗ 錯誤 {md_file.relative_to(root)}: {e}', file=sys.stderr)
    
    print(f'\n總計修復 {fixed_count} 個文件')

if __name__ == '__main__':
    main()
