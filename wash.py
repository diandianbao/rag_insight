#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本清洗工具 - 用于清理text目录下的.md文件

功能：
- 删除英文段落
- 保留中文段落（去掉<mark>标签）
- 保持文件结构（标题、列表、图片等）
"""

import os
import re
import glob
from pathlib import Path

def clean_markdown_file(file_path):
    """
    清理单个markdown文件

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否成功清理
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = []
        skip_next = False

        for i, line in enumerate(lines):
            # 如果标记为跳过，则跳过当前行
            if skip_next:
                skip_next = False
                continue

            # 处理标题：将 "英文标题 | <mark>中文标题</mark>" 替换为 "中文标题"
            if '| <mark>' in line and '</mark>' in line:
                # 提取中文标题
                match = re.search(r'\|\s*<mark>(.*?)</mark>', line)
                if match:
                    chinese_title = match.group(1)
                    # 保持标题级别
                    if line.startswith('### '):
                        cleaned_lines.append(f'### {chinese_title}\n')
                    elif line.startswith('## '):
                        cleaned_lines.append(f'## {chinese_title}\n')
                    elif line.startswith('# '):
                        cleaned_lines.append(f'# {chinese_title}\n')
                    else:
                        cleaned_lines.append(f'{chinese_title}\n')
                continue

            # 处理标题：将 "英文标题 | 中文标题" 替换为 "中文标题"（处理已经去掉<mark>标签的情况）
            if ' | ' in line and not '<mark>' in line and not '</mark>' in line:
                parts = line.split(' | ')
                if len(parts) == 2 and re.search(r'[\u4e00-\u9fff]', parts[1]):
                    chinese_title = parts[1].strip()
                    # 保持标题级别
                    if line.startswith('### '):
                        cleaned_lines.append(f'### {chinese_title}\n')
                    elif line.startswith('## '):
                        cleaned_lines.append(f'## {chinese_title}\n')
                    elif line.startswith('# '):
                        cleaned_lines.append(f'# {chinese_title}\n')
                    else:
                        cleaned_lines.append(f'{chinese_title}\n')
                continue

            # 处理中文段落：直接保留中文内容（去掉<mark>标签）
            if '<mark>' in line and '</mark>' in line:
                chinese_content = re.sub(r'<mark>(.*?)</mark>', r'\1', line)
                cleaned_lines.append(chinese_content)
                continue

            # 处理英文段落：如果下一行是中文翻译，则跳过当前英文行
            if i + 1 < len(lines) and '<mark>' in lines[i + 1] and '</mark>' in lines[i + 1]:
                # 当前行是英文，下一行是中文翻译，跳过当前行
                skip_next = True
                # 提取下一行的中文内容
                chinese_content = re.sub(r'<mark>(.*?)</mark>', r'\1', lines[i + 1])
                cleaned_lines.append(chinese_content)
                continue

            # 处理列表项：如果当前是英文列表项，下一行是中文翻译
            if (line.strip().startswith('- ') or line.strip().startswith('* ') or
                re.match(r'^\d+\.', line.strip())):
                if i + 1 < len(lines) and '<mark>' in lines[i + 1] and '</mark>' in lines[i + 1]:
                    # 当前是英文列表项，下一行是中文翻译
                    skip_next = True
                    chinese_content = re.sub(r'<mark>(.*?)</mark>', r'\1', lines[i + 1])
                    cleaned_lines.append(chinese_content)
                    continue

            # 保留其他行（图片、图表说明、分隔线等）
            if (line.startswith('![') or line.startswith('**Fig.') or
                line.startswith('**图') or line.strip() == '---' or
                line.strip() == '***' or line.strip() == ''):
                cleaned_lines.append(line)
                continue

            # 如果是纯英文行（不包含中文且不是特殊格式），跳过
            if not re.search(r'[\u4e00-\u9fff]', line) and not line.strip().startswith('#'):
                continue

            # 其他情况保留原行
            cleaned_lines.append(line)

        # 重新组合内容
        cleaned_content = ''.join(cleaned_lines)

        # 清理多余的空行（连续3个以上空行替换为2个）
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        print(f"✓ 已清理: {file_path}")
        return True

    except Exception as e:
        print(f"✗ 清理失败 {file_path}: {e}")
        return False

def clean_all_files():
    """
    清理text目录下的所有.md文件
    """
    text_dir = Path('text')

    if not text_dir.exists():
        print("✗ text目录不存在")
        return

    # 获取所有.md文件
    md_files = list(text_dir.glob('*.md'))

    if not md_files:
        print("✗ 在text目录下未找到.md文件")
        return

    print(f"找到 {len(md_files)} 个.md文件，开始清理...")
    print("-" * 50)

    success_count = 0
    failed_files = []

    for file_path in md_files:
        if clean_markdown_file(file_path):
            success_count += 1
        else:
            failed_files.append(file_path.name)

    print("-" * 50)
    print(f"清理完成!")
    print(f"成功: {success_count}/{len(md_files)} 个文件")

    if failed_files:
        print(f"失败: {len(failed_files)} 个文件")
        for file_name in failed_files:
            print(f"  - {file_name}")

def preview_clean(file_path):
    """
    预览清理效果（不实际修改文件）

    Args:
        file_path: 文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = []
        skip_next = False

        for i, line in enumerate(lines):
            # 如果标记为跳过，则跳过当前行
            if skip_next:
                skip_next = False
                continue

            # 处理标题：将 "英文标题 | <mark>中文标题</mark>" 替换为 "中文标题"
            if '| <mark>' in line and '</mark>' in line:
                # 提取中文标题
                match = re.search(r'\|\s*<mark>(.*?)</mark>', line)
                if match:
                    chinese_title = match.group(1)
                    # 保持标题级别
                    if line.startswith('### '):
                        cleaned_lines.append(f'### {chinese_title}\n')
                    elif line.startswith('## '):
                        cleaned_lines.append(f'## {chinese_title}\n')
                    elif line.startswith('# '):
                        cleaned_lines.append(f'# {chinese_title}\n')
                    else:
                        cleaned_lines.append(f'{chinese_title}\n')
                continue

            # 处理标题：将 "英文标题 | 中文标题" 替换为 "中文标题"（处理已经去掉<mark>标签的情况）
            if ' | ' in line and not '<mark>' in line and not '</mark>' in line:
                parts = line.split(' | ')
                if len(parts) == 2 and re.search(r'[\u4e00-\u9fff]', parts[1]):
                    chinese_title = parts[1].strip()
                    # 保持标题级别
                    if line.startswith('### '):
                        cleaned_lines.append(f'### {chinese_title}\n')
                    elif line.startswith('## '):
                        cleaned_lines.append(f'## {chinese_title}\n')
                    elif line.startswith('# '):
                        cleaned_lines.append(f'# {chinese_title}\n')
                    else:
                        cleaned_lines.append(f'{chinese_title}\n')
                continue

            # 处理中文段落：直接保留中文内容（去掉<mark>标签）
            if '<mark>' in line and '</mark>' in line:
                chinese_content = re.sub(r'<mark>(.*?)</mark>', r'\1', line)
                cleaned_lines.append(chinese_content)
                continue

            # 处理英文段落：如果下一行是中文翻译，则跳过当前英文行
            if i + 1 < len(lines) and '<mark>' in lines[i + 1] and '</mark>' in lines[i + 1]:
                # 当前行是英文，下一行是中文翻译，跳过当前行
                skip_next = True
                # 提取下一行的中文内容
                chinese_content = re.sub(r'<mark>(.*?)</mark>', r'\1', lines[i + 1])
                cleaned_lines.append(chinese_content)
                continue

            # 处理列表项：如果当前是英文列表项，下一行是中文翻译
            if (line.strip().startswith('- ') or line.strip().startswith('* ') or
                re.match(r'^\d+\.', line.strip())):
                if i + 1 < len(lines) and '<mark>' in lines[i + 1] and '</mark>' in lines[i + 1]:
                    # 当前是英文列表项，下一行是中文翻译
                    skip_next = True
                    chinese_content = re.sub(r'<mark>(.*?)</mark>', r'\1', lines[i + 1])
                    cleaned_lines.append(chinese_content)
                    continue

            # 保留其他行（图片、图表说明、分隔线等）
            if (line.startswith('![') or line.startswith('**Fig.') or
                line.startswith('**图') or line.strip() == '---' or
                line.strip() == '***' or line.strip() == ''):
                cleaned_lines.append(line)
                continue

            # 如果是纯英文行（不包含中文且不是特殊格式），跳过
            if not re.search(r'[\u4e00-\u9fff]', line) and not line.strip().startswith('#'):
                continue

            # 其他情况保留原行
            cleaned_lines.append(line)

        # 重新组合内容
        cleaned_content = ''.join(cleaned_lines)

        # 清理多余的空行（连续3个以上空行替换为2个）
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)

        print("=" * 60)
        print(f"预览清理效果 - {file_path}")
        print("=" * 60)
        print("\n清理前（前20行）:")
        print("-" * 40)
        print(''.join(lines[:20]))
        print("\n清理后（前20行）:")
        print("-" * 40)
        print(''.join(cleaned_lines[:20]))

    except Exception as e:
        print(f"预览失败: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='清理text目录下的.md文件，删除英文段落，保留中文内容')
    parser.add_argument('--preview', type=str, help='预览指定文件的清理效果（不实际修改）')
    parser.add_argument('--file', type=str, help='清理单个指定文件')

    args = parser.parse_args()

    if args.preview:
        preview_clean(args.preview)
    elif args.file:
        clean_markdown_file(args.file)
    else:
        clean_all_files()