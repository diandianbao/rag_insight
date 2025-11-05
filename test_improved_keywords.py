#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的关键词提取效果
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_splitter import DocumentSplitter
from keyword_extractor import KeywordExtractor

def test_keyword_extraction_comparison():
    """比较改进前后的关键词提取效果"""
    print("=" * 60)
    print("关键词提取效果对比测试")
    print("=" * 60)

    # 测试文本
    test_text = """
    提示链模式，也称为「管道模式」，是利用大语言模型处理复杂任务的一种强大范式。
    它不期望用单一步骤解决复杂问题，而是采用「分而治之」策略。其核心思想是将难题拆解为一系列更小、更易管理的子问题。
    每个子问题通过专门设计的提示独立解决，前一步的输出传递给下一步作为输入。

    这种顺序处理技术天然具备模块化和清晰性特点。通过分解复杂任务，每个独立步骤都变得更易于理解和调试，
    从而使整个流程更加稳健、更具可解释性。链条中的每一步都可以被精心设计和优化，
    专注于解决整体问题中的某个特定方面，最终带来更精准、更聚焦的输出。

    上一步的输出成为下一步的输入，这一点至关重要。这种信息传递建立起一个依赖链（链式结构由此得名），
    前序操作的上下文和结果引导后续处理。这使得模型能够在先前工作的基础上不断深化理解，逐步接近最终期望的解决方案。

    提示链不仅能分解问题，还能整合外部知识与工具。每一步都可以指示模型调用外部系统、API 或数据库，
    极大丰富其知识和能力，突破训练数据的局限。这让模型从孤立的个体，演变为更广阔智能系统中的关键组件。
    """

    print("测试文本:")
    print(test_text[:200] + "...")
    print("\n" + "-" * 40)

    # 使用独立的关键词提取器
    print("\n1. 独立关键词提取器结果:")
    extractor = KeywordExtractor()

    # TF-IDF方法
    tfidf_keywords = extractor.extract_keywords(test_text, top_k=8, method='tfidf', with_weight=True)
    print("  TF-IDF关键词:")
    for word, weight in tfidf_keywords:
        print(f"    {word}: {weight:.4f}")

    # TextRank方法
    textrank_keywords = extractor.extract_keywords(test_text, top_k=8, method='textrank', with_weight=True)
    print("\n  TextRank关键词:")
    for word, weight in textrank_keywords:
        print(f"    {word}: {weight:.4f}")

    # 文本分析
    analysis = extractor.analyze_text(test_text)
    print(f"\n  文本分析:")
    print(f"    总词数: {analysis['word_count']}")
    print(f"    唯一词数: {analysis['unique_words']}")
    print(f"    领域词比例: {analysis['domain_word_ratio']:.2%}")
    print(f"    领域关键词: {analysis['domain_keywords']}")

    # 使用文档分割器的关键词提取
    print("\n2. 文档分割器关键词提取结果:")
    splitter = DocumentSplitter()

    # 模拟文档块的关键词提取
    keywords = splitter._extract_keywords(test_text, max_keywords=8)
    print(f"  提取的关键词: {keywords}")

    # 测试回退方法
    print("\n3. 回退方法测试:")
    fallback_keywords = splitter._extract_keywords_fallback(test_text, max_keywords=8)
    print(f"  回退方法关键词: {fallback_keywords}")

def test_document_splitting_with_improved_keywords():
    """测试文档分割时改进的关键词提取"""
    print("\n" + "=" * 60)
    print("文档分割关键词提取测试")
    print("=" * 60)

    # 测试文件路径
    test_file = "text/11-Chapter-05-Tool-Use.md"

    if os.path.exists(test_file):
        splitter = DocumentSplitter()
        chunks = splitter.split_document(test_file)

        print(f"\n测试文件: {test_file}")
        print(f"生成块数: {len(chunks)}")

        if chunks:
            print("\n前3个块的关键词预览:")
            for i, chunk in enumerate(chunks[:3]):
                print(f"\n--- 块 {i+1} ---")
                print(f"ID: {chunk.id}")
                print(f"标题: {chunk.metadata.get('title', '无')}")
                print(f"字数: {chunk.metadata.get('word_count', 0)}")
                print(f"关键词: {chunk.metadata.get('keywords', [])}")
                print(f"内容预览: {chunk.content[:80]}...")
    else:
        print(f"测试文件不存在: {test_file}")

if __name__ == "__main__":
    test_keyword_extraction_comparison()
    test_document_splitting_with_improved_keywords()