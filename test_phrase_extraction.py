#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试短语提取效果对比
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from keyword_extractor import KeywordExtractor

def test_phrase_extraction_comparison():
    """对比短语提取和传统关键词提取效果"""
    print("=" * 70)
    print("短语提取 vs 传统关键词提取 效果对比")
    print("=" * 70)

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

    extractor = KeywordExtractor()

    print("\n1. 传统关键词提取方法:")
    print("-" * 30)

    # TF-IDF
    tfidf_keywords = extractor.extract_keywords(test_text, top_k=10, method='tfidf', with_weight=False)
    print(f"  TF-IDF关键词: {tfidf_keywords}")

    # TextRank
    textrank_keywords = extractor.extract_keywords(test_text, top_k=10, method='textrank', with_weight=False)
    print(f"  TextRank关键词: {textrank_keywords}")

    print("\n2. 改进的短语提取方法:")
    print("-" * 30)

    # 短语提取
    phrases = extractor.extract_phrases(test_text, top_k=10)
    print(f"  短语提取: {phrases}")

    # 概念提取
    concepts = extractor.extract_concepts(test_text, top_k=10)
    print(f"  概念提取: {concepts}")

    # 混合提取
    hybrid_keywords = extractor.extract_hybrid_keywords(test_text, top_k=15)
    print(f"  混合关键词: {hybrid_keywords}")

    print("\n3. 综合分析:")
    print("-" * 30)

    analysis = extractor.analyze_text(test_text)
    print(f"  总词数: {analysis['word_count']}")
    print(f"  唯一词数: {analysis['unique_words']}")
    print(f"  领域词比例: {analysis['domain_word_ratio']:.2%}")

    print("\n4. 效果对比总结:")
    print("-" * 30)
    print("  传统方法问题:")
    print("    - 提取单个词汇，缺乏语义完整性")
    print("    - 不符合用户搜索习惯")
    print("    - 领域特征不明显")

    print("\n  改进方法优势:")
    print("    - 提取完整短语，语义更丰富")
    print("    - 符合用户搜索习惯（如'提示链模式'）")
    print("    - 突出领域专业术语")
    print("    - 支持多种提取策略")

def test_document_chunk_keywords():
    """测试文档块的关键词提取效果"""
    print("\n" + "=" * 70)
    print("文档块关键词提取测试")
    print("=" * 70)

    # 模拟文档块内容
    chunk_texts = [
        """
        工具使用模式通常通过函数调用（Function Calling）机制实现，使智能体能够与外部 API、数据库、服务交互，
        甚至直接执行代码。它允许作为智能体核心的大语言模型根据用户请求或当前任务状态，来决定何时以及如何使用特定的外部函数。
        """,

        """
        这种模式很关键，因为它突破了大语言模型训练数据的局限，使其能够获取最新信息、执行内部无法处理的计算、
        访问用户特定的数据，或触发现实世界的动作。函数调用是连接大语言模型推理能力与外部功能的技术桥梁。
        """,

        """
        虽然「函数调用」这个说法确实能准确描述调用预定义代码函数的过程，但从更广阔的视角理解「工具调用」这一概念更为有益。
        通过这个更广义的术语，我们看到智能体的能力可以远远超出简单的函数执行。
        """
    ]

    extractor = KeywordExtractor()

    for i, chunk_text in enumerate(chunk_texts, 1):
        print(f"\n--- 文档块 {i} ---")
        print(f"内容: {chunk_text.strip()[:80]}...")

        # 传统方法
        traditional_keywords = extractor.extract_keywords(chunk_text, top_k=5, method='tfidf', with_weight=False)
        print(f"  传统关键词: {traditional_keywords}")

        # 改进方法
        hybrid_keywords = extractor.extract_hybrid_keywords(chunk_text, top_k=5)
        print(f"  混合关键词: {hybrid_keywords}")

        # 短语提取
        phrases = extractor.extract_phrases(chunk_text, top_k=3)
        print(f"  短语提取: {phrases}")

if __name__ == "__main__":
    test_phrase_extraction_comparison()
    test_document_chunk_keywords()