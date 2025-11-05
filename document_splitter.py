#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档分割器 - 用于RAG系统的文档智能分割

功能：
- 按标题层级智能分割markdown文档
- 提取丰富的元数据
- 保持语义完整性
- 支持批量处理
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """文档块数据结构"""
    id: str
    content: str
    metadata: Dict[str, Any]

class DocumentSplitter:
    """文档分割器"""

    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 800):
        """
        初始化分割器

        Args:
            min_chunk_size: 最小块大小（字符数）
            max_chunk_size: 最大块大小（字符数）
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

        # 标题正则表达式
        self.title_patterns = {
            1: re.compile(r'^#\s+(.+)$'),
            2: re.compile(r'^##\s+(.+)$'),
            3: re.compile(r'^###\s+(.+)$')
        }

        # 特殊格式检测
        self.code_block_pattern = re.compile(r'^```')
        self.list_item_pattern = re.compile(r'^\s*[-*]\s+')
        self.numbered_list_pattern = re.compile(r'^\s*\d+\.\s+')

    def split_document(self, file_path: str) -> List[DocumentChunk]:
        """
        分割单个文档

        Args:
            file_path: 文档文件路径

        Returns:
            文档块列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            chunks = []
            current_chunk = []
            current_metadata = self._extract_base_metadata(file_path)

            in_code_block = False
            current_title_level = 0
            current_title = ""
            block_index = 0

            for i, line in enumerate(lines):
                line = line.rstrip('\n')

                # 检测代码块开始/结束
                if self.code_block_pattern.match(line):
                    in_code_block = not in_code_block
                    current_chunk.append(line)
                    continue

                # 如果在代码块中，直接添加到当前块
                if in_code_block:
                    current_chunk.append(line)
                    continue

                # 检测标题
                title_match = self._detect_title(line)
                if title_match:
                    level, title = title_match

                    # 如果当前块有内容，先保存
                    if current_chunk and self._should_save_chunk(current_chunk):
                        chunk = self._create_chunk(
                            current_chunk, current_metadata,
                            current_title_level, current_title, block_index
                        )
                        if chunk:
                            chunks.append(chunk)
                        block_index += 1
                        current_chunk = []

                    # 开始新块
                    current_title_level = level
                    current_title = title
                    current_chunk.append(line)

                    # 更新元数据
                    current_metadata.update(self._extract_title_metadata(level, title))

                else:
                    # 普通内容行
                    current_chunk.append(line)

                    # 检查是否需要分割（基于大小）
                    if self._should_split_chunk(current_chunk):
                        chunk = self._create_chunk(
                            current_chunk, current_metadata,
                            current_title_level, current_title, block_index
                        )
                        if chunk:
                            chunks.append(chunk)
                        block_index += 1
                        current_chunk = []

            # 处理最后一个块
            if current_chunk and self._should_save_chunk(current_chunk):
                chunk = self._create_chunk(
                    current_chunk, current_metadata,
                    current_title_level, current_title, block_index
                )
                if chunk:
                    chunks.append(chunk)

            print(f"✓ 分割完成: {file_path} -> {len(chunks)} 个块")
            return chunks

        except Exception as e:
            print(f"✗ 分割失败 {file_path}: {e}")
            return []

    def _detect_title(self, line: str) -> tuple:
        """检测标题行"""
        for level, pattern in self.title_patterns.items():
            match = pattern.match(line)
            if match:
                return level, match.group(1).strip()
        return None

    def _should_save_chunk(self, chunk_lines: List[str]) -> bool:
        """判断是否应该保存当前块"""
        content = '\n'.join(chunk_lines)

        # 忽略空块或纯格式块
        if not content.strip():
            return False

        # 忽略分隔线
        if content.strip() in ['---', '***', '___']:
            return False

        return True

    def _should_split_chunk(self, chunk_lines: List[str]) -> bool:
        """判断是否应该分割当前块"""
        content = '\n'.join(chunk_lines)

        # 基于字符数判断
        if len(content) >= self.max_chunk_size:
            return True

        # 基于段落边界判断
        if len(chunk_lines) >= 3 and chunk_lines[-1].strip() == '':
            return True

        return False

    def _create_chunk(self, chunk_lines: List[str], base_metadata: Dict,
                     title_level: int, title: str, block_index: int) -> DocumentChunk:
        """创建文档块"""
        content = '\n'.join(chunk_lines).strip()

        if not content:
            return None

        # 生成ID
        chapter_id = base_metadata.get('chapter_id', 'unknown')
        chunk_id = f"chapter_{chapter_id}_block_{block_index:03d}"

        # 构建完整元数据
        metadata = base_metadata.copy()
        metadata.update({
            'block_index': block_index,
            'word_count': len(content.split()),
            'char_count': len(content),
            'title_level': title_level,
            'title': title,
            'has_code': self._has_code(content),
            'has_list': self._has_list(content),
            'keywords': self._extract_keywords(content)
        })

        return DocumentChunk(
            id=chunk_id,
            content=content,
            metadata=metadata
        )

    def _extract_base_metadata(self, file_path: str) -> Dict[str, Any]:
        """提取基础元数据"""
        file_name = Path(file_path).name

        # 从文件名提取章节信息
        match = re.match(r'(\d+)-(.+)\.md', file_name)
        if match:
            chapter_id = match.group(1)
            chapter_name_raw = match.group(2).replace('-', ' ')

            # 简化章节名称（去掉Chapter-前缀等）
            chapter_name = re.sub(r'^Chapter\s*\d+\s*', '', chapter_name_raw)
            chapter_name = re.sub(r'^\d+\s*', '', chapter_name)

            # 中文章节名称映射
            chapter_name_cn = self._get_chinese_chapter_name(chapter_id)

            return {
                'chapter_id': chapter_id,
                'chapter_name_en': chapter_name,
                'chapter_name_cn': chapter_name_cn,
                'file_path': file_path,
                'file_name': file_name
            }

        return {
            'file_path': file_path,
            'file_name': file_name
        }

    def _extract_title_metadata(self, level: int, title: str) -> Dict[str, Any]:
        """从标题提取元数据"""
        metadata = {}

        # 判断章节类型
        if level == 2:
            if '概述' in title or 'Overview' in title:
                metadata['section_type'] = '模式概述'
            elif '应用' in title or 'Application' in title:
                metadata['section_type'] = '实际应用'
            elif '要点' in title or 'Takeaway' in title:
                metadata['section_type'] = '核心要点'
            elif '示例' in title or 'Example' in title:
                metadata['section_type'] = '代码示例'
            else:
                metadata['section_type'] = '其他'

        return metadata

    def _get_chinese_chapter_name(self, chapter_id: str) -> str:
        """获取中文章节名称"""
        chapter_map = {
            '00': '目录',
            '01': '致谢',
            '02': '鸣谢',
            '03': '前言',
            '04': '思想领袖',
            '05': '介绍',
            '06': '什么是智能体',
            '07': '第一章：提示链',
            '08': '第二章：路由',
            '09': '第三章：并行化',
            '10': '第四章：反思',
            '11': '第五章：工具使用',
            '12': '第六章：规划',
            '13': '第七章：多智能体协作',
            '14': '第八章：记忆管理',
            '16': '第十章：模型上下文协议',
            '17': '第十一章：目标设定与监控',
            '19': '第十三章：人在回路',
            '20': '第十四章：知识检索RAG',
            '21': '第十五章：智能体间通信',
            '22': '第十六章：资源感知优化',
            '23': '第十七章：推理技术',
            '25': '第十九章：评估与监控',
            '26': '第二十章：优先级',
            '27': '第二十一章：探索与发现'
        }
        return chapter_map.get(chapter_id, f"第{chapter_id}章")

    def _has_code(self, content: str) -> bool:
        """检测是否包含代码"""
        return '```' in content

    def _has_list(self, content: str) -> bool:
        """检测是否包含列表"""
        return bool(self.list_item_pattern.search(content) or
                   self.numbered_list_pattern.search(content))

    def _extract_keywords(self, content: str, max_keywords: int = 5) -> List[str]:
        """提取关键词（使用jieba改进版本）"""
        try:
            # 导入关键词提取器
            from keyword_extractor import KeywordExtractor

            # 创建提取器实例
            extractor = KeywordExtractor()

            # 使用TF-IDF方法提取关键词
            keywords_with_weights = extractor.extract_keywords(
                content, top_k=max_keywords, method='tfidf', with_weight=True
            )

            # 只返回关键词，不返回权重
            return [word for word, weight in keywords_with_weights]

        except ImportError:
            # 如果keyword_extractor不可用，回退到简单方法
            print("警告: 无法导入keyword_extractor，使用简单关键词提取")
            return self._extract_keywords_fallback(content, max_keywords)

    def _extract_keywords_fallback(self, content: str, max_keywords: int = 5) -> List[str]:
        """回退的关键词提取方法"""
        # 移除代码块和特殊字符
        clean_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        clean_content = re.sub(r'[^\w\u4e00-\u9fff\s]', ' ', clean_content)

        # 简单的关键词提取
        words = clean_content.split()

        # 过滤停用词和短词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它'}

        keywords = []
        for word in words:
            if (len(word) >= 2 and
                word not in stop_words and
                (re.search(r'[\u4e00-\u9fff]', word) or len(word) >= 3)):
                keywords.append(word)

        # 返回前N个关键词
        return keywords[:max_keywords]

    def batch_split(self, input_dir: str, output_dir: str = None) -> Dict[str, List[DocumentChunk]]:
        """
        批量分割目录中的所有文档

        Args:
            input_dir: 输入目录
            output_dir: 输出目录（可选，保存分割结果）

        Returns:
            文件名到文档块列表的映射
        """
        input_path = Path(input_dir)

        if not input_path.exists():
            print(f"✗ 输入目录不存在: {input_dir}")
            return {}

        # 获取所有markdown文件
        md_files = list(input_path.glob('*.md'))

        if not md_files:
            print(f"✗ 在目录中未找到.md文件: {input_dir}")
            return {}

        print(f"找到 {len(md_files)} 个.md文件，开始批量分割...")

        all_chunks = {}

        for file_path in md_files:
            chunks = self.split_document(str(file_path))
            all_chunks[file_path.name] = chunks

            # 如果指定了输出目录，保存分割结果
            if output_dir:
                self._save_chunks(chunks, output_dir, file_path.name)

        # 统计信息
        total_chunks = sum(len(chunks) for chunks in all_chunks.values())
        print(f"批量分割完成! 总共生成 {total_chunks} 个文档块")

        return all_chunks

    def _save_chunks(self, chunks: List[DocumentChunk], output_dir: str, source_file: str):
        """保存分割结果"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存为JSON文件
        output_file = output_path / f"{Path(source_file).stem}_chunks.json"

        chunk_data = []
        for chunk in chunks:
            chunk_data.append({
                'id': chunk.id,
                'content': chunk.content,
                'metadata': chunk.metadata
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)

        print(f"  ✓ 保存分割结果: {output_file}")

def test_splitter():
    """测试分割器功能"""
    print("=" * 60)
    print("文档分割器测试")
    print("=" * 60)

    splitter = DocumentSplitter()

    # 测试单个文件
    test_file = "text/07-Chapter-01-Prompt-Chaining.md"
    if os.path.exists(test_file):
        chunks = splitter.split_document(test_file)

        print(f"\n测试文件: {test_file}")
        print(f"生成块数: {len(chunks)}")

        if chunks:
            print("\n前3个块预览:")
            for i, chunk in enumerate(chunks[:3]):
                print(f"\n--- 块 {i+1} ---")
                print(f"ID: {chunk.id}")
                print(f"标题: {chunk.metadata.get('title', '无')}")
                print(f"字数: {chunk.metadata.get('word_count', 0)}")
                print(f"内容预览: {chunk.content[:100]}...")
    else:
        print(f"测试文件不存在: {test_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='文档分割器 - 智能分割markdown文档')
    parser.add_argument('--input', type=str, help='输入文件或目录路径')
    parser.add_argument('--output', type=str, help='输出目录路径（批量处理时使用）')
    parser.add_argument('--test', action='store_true', help='运行测试')

    args = parser.parse_args()

    if args.test:
        test_splitter()
    elif args.input:
        splitter = DocumentSplitter()

        if os.path.isfile(args.input):
            # 单个文件处理
            chunks = splitter.split_document(args.input)
            if args.output:
                splitter._save_chunks(chunks, args.output, os.path.basename(args.input))
        elif os.path.isdir(args.input):
            # 批量处理
            splitter.batch_split(args.input, args.output)
        else:
            print(f"✗ 输入路径不存在: {args.input}")
    else:
        print("使用说明:")
        print("  --input <路径>   输入文件或目录")
        print("  --output <路径>  输出目录（批量处理时使用）")
        print("  --test           运行测试")
        print("\n示例:")
        print("  python document_splitter.py --input text/07-Chapter-01-Prompt-Chaining.md")
        print("  python document_splitter.py --input text --output chunks")
        print("  python document_splitter.py --test")