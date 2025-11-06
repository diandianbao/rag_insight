#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键词提取器 - 使用jieba进行中文关键词提取

功能：
- 中文文本分词
- 关键词提取和评分
- 停用词过滤
- 自定义词典支持
"""

import jieba
import jieba.analyse
import jieba.posseg as pseg
import re
from typing import List, Tuple, Dict, Any

class KeywordExtractor:
    """关键词提取器"""

    def __init__(self):
        """初始化提取器"""
        # 初始化jieba
        self._initialize_jieba()

        # 智能体领域自定义词典
        self.agent_domain_words = [
            # 核心概念
            '智能体', 'Agent', '大语言模型', 'LLM', 'AI', '人工智能',
            '提示链', 'Prompt Chaining', '路由', 'Routing', '并行化', 'Parallelization',
            '反思', 'Reflection', '工具使用', 'Tool Use', '函数调用', 'Function Calling',
            '规划', 'Planning', '多智能体协作', 'Multi-Agent Collaboration',
            '记忆管理', 'Memory Management', '模型上下文协议', 'Model Context Protocol',
            '目标设定', 'Goal Setting', '监控', 'Monitoring', '人在回路', 'Human-in-the-Loop',
            '知识检索', 'Knowledge Retrieval', 'RAG', '智能体间通信', 'Inter-Agent Communication',
            '资源感知优化', 'Resource-Aware Optimization', '推理技术', 'Reasoning Techniques',
            '评估', 'Evaluation', '优先级', 'Prioritization', '探索', 'Exploration', '发现', 'Discovery',

            # 技术术语
            '模块化', '分而治之', '管道模式', '工作流', '上下文', '语义',
            '向量化', '嵌入', '检索', '相似度', '相关性', '重排序',
            'API', '数据库', '外部系统', '实时数据', '结构化输出',
            'JSON', 'XML', '自然语言处理', 'NLP', '机器学习',
            '深度学习', '神经网络', 'Transformer', '注意力机制',

            # 框架和工具
            'LangChain', 'LangGraph', 'Crew AI', 'Google ADK', 'Gemini', 'OpenAI',
            'ChromaDB', 'Pinecone', '向量数据库', 'FastAPI',

            # 应用场景
            '自动化', '智能助手', '客户服务', '数据分析', '内容生成',
            '研究助手', '报告生成', '问答系统', '信息检索', '决策支持',
            '任务规划', '资源分配', '协作系统', '知识管理'
        ]

        # 添加自定义词典
        for word in self.agent_domain_words:
            jieba.add_word(word, freq=1000, tag='n')

        # 短语模式正则表达式
        self.phrase_patterns = [
            r'[\u4e00-\u9fff]+模式',  # XX模式
            r'[\u4e00-\u9fff]+模型',  # XX模型
            r'[\u4e00-\u9fff]+任务',  # XX任务
            r'[\u4e00-\u9fff]+策略',  # XX策略
            r'[\u4e00-\u9fff]+技术',  # XX技术
            r'[\u4e00-\u9fff]+系统',  # XX系统
            r'[\u4e00-\u9fff]+智能体',  # XX智能体
            r'[\u4e00-\u9fff]+算法',  # XX算法
            r'[\u4e00-\u9fff]+框架',  # XX框架
            r'[\u4e00-\u9fff]+工具',  # XX工具
        ]

        # 停用词列表（扩展版）
        self.stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
                           '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他',
                           '她', '它', '我们', '你们', '他们', '她们', '它们', '这个', '那个', '这些', '那些', '这里',
                           '那里', '这样', '那样', '这么', '那么', '什么', '怎么', '为什么', '如何', '哪里', '哪个',
                           '哪些', '多少', '几', '可以', '可能', '能够', '应该', '必须', '需要', '要求', '希望', '想要',
                           '因为', '所以', '但是', '然而', '虽然', '如果', '那么', '然后', '而且', '或者', '例如',
                           '比如', '譬如', '就像', '如同', '似乎', '好像', '大约', '大概', '首先', '其次', '最后',
                           '总之', '总而言之', '另外', '此外', '同时', '通过', '根据', '按照', '关于', '对于', '至于',
                           '由于', '因此', '进行', '完成', '实现', '达到', '取得', '获得', '得到', '提供', '支持',
                           '使用', '利用', '应用', '采用', '选择', '决定', '确定', '确认', '开始', '结束', '停止',
                           '继续', '保持', '维持', '改变', '调整', '重要', '主要', '关键', '核心', '基本', '根本',
                           '必要', '必须', '不同', '相同', '类似', '相似', '相关', '无关', '独立', '依赖', '大', '小',
                           '多', '少', '高', '低', '长', '短', '快', '慢', '强', '弱', '新', '旧', '老', '年轻', '好',
                           '坏', '优', '劣', '正', '负', '前', '后', '左', '右', '上', '下', '内', '外', '中', '间',
                           '以及', '及其', '及其它', '其他', '其余', '剩下', '全部', '所有', '每个', '各个', '各种',
                           '各类', '各项', '各个', '各种', '各类', '一些', '一点', '一部分', '一方面', '另一方面',
                           '非常', '十分', '极其', '特别', '尤其', '更加', '较为', '比较', '一定', '肯定', '确定',
                           '确实', '实在', '真正', '确实', '的确', '可能', '也许', '或许', '大概', '大约', '差不多',
                           '几乎', '近乎', '已经', '曾经', '正在', '将要', '即将', '马上', '立刻', '立即', '刚才',
                           '刚刚', '最近', '近来', '目前', '现在', '当前', '如今', '以前', '之前', '今后', '以后',
                           '未来', '将来', '永远', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                           'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
                           'above', 'below', 'between', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                           'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'can', 'could', 'may', 'might', 'must',
                           'shall', 'should', 'will', 'would', 'there', 'here', 'where', 'when', 'why', 'how', 'what',
                           'which', 'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'I', 'you', 'he', 'she',
                           'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its',
                           'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs', 'myself', 'yourself', 'himself',
                           'herself', 'itself', 'ourselves', 'yourselves', 'themselves'}

    def _initialize_jieba(self):
        """初始化jieba配置"""
        # 设置分词模式
        jieba.setLogLevel(20)  # 减少日志输出

        # 加载用户词典（如果有的话）
        try:
            jieba.load_userdict('user_dict.txt')
        except:
            pass  # 如果没有用户词典，忽略

    def extract_keywords(self, text: str, top_k: int = 10,
                        method: str = 'tfidf',
                        with_weight: bool = False) -> List:
        """
        提取关键词

        Args:
            text: 输入文本
            top_k: 返回关键词数量
            method: 提取方法 ('tfidf', 'textrank')
            with_weight: 是否返回权重

        Returns:
            关键词列表
        """
        # 文本预处理
        clean_text = self._preprocess_text(text)

        if not clean_text.strip():
            return []

        # 根据方法选择提取算法
        if method == 'textrank':
            keywords = jieba.analyse.textrank(
                clean_text, topK=top_k, withWeight=with_weight, allowPOS=('n', 'vn', 'v')
            )
        else:  # 默认使用tfidf
            keywords = jieba.analyse.extract_tags(
                clean_text, topK=top_k, withWeight=with_weight, allowPOS=('n', 'vn', 'v')
            )

        # 过滤停用词
        if with_weight:
            filtered_keywords = [(word, weight) for word, weight in keywords
                               if word not in self.stop_words and len(word) >= 2]
        else:
            filtered_keywords = [word for word in keywords
                              if word not in self.stop_words and len(word) >= 2]

        return filtered_keywords[:top_k]

    def extract_phrases(self, text: str, top_k: int = 10,
                       min_phrase_length: int = 2, max_phrase_length: int = 4) -> List[str]:
        """
        提取短语（名词性短语）

        Args:
            text: 输入文本
            top_k: 返回短语数量
            min_phrase_length: 最小短语长度（词数）
            max_phrase_length: 最大短语长度（词数）

        Returns:
            短语列表
        """
        # 文本预处理
        clean_text = self._preprocess_text(text)

        if not clean_text.strip():
            return []

        # 使用词性标注提取名词性短语
        words = pseg.cut(clean_text)

        phrases = []
        current_phrase = []

        for word, flag in words:
            # 名词性词性：n(名词), vn(动名词), nr(人名), ns(地名), nt(机构名), nz(其他专名)
            if flag.startswith('n') and word not in self.stop_words and len(word) >= 2:
                current_phrase.append(word)
            else:
                # 遇到非名词，保存当前短语
                if (len(current_phrase) >= min_phrase_length and
                    len(current_phrase) <= max_phrase_length):
                    phrase = ''.join(current_phrase)
                    if len(phrase) >= 4:  # 至少2个汉字
                        phrases.append(phrase)
                current_phrase = []

        # 处理最后一个短语
        if (len(current_phrase) >= min_phrase_length and
            len(current_phrase) <= max_phrase_length):
            phrase = ''.join(current_phrase)
            if len(phrase) >= 4:
                phrases.append(phrase)

        # 去重并返回
        unique_phrases = list(set(phrases))
        return unique_phrases[:top_k]

    def extract_concepts(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取概念性短语（基于模式匹配）

        Args:
            text: 输入文本
            top_k: 返回概念数量

        Returns:
            概念列表
        """
        clean_text = self._preprocess_text(text)

        if not clean_text.strip():
            return []

        concepts = []
        for pattern in self.phrase_patterns:
            matches = re.findall(pattern, clean_text)
            for match in matches:
                if (match not in self.stop_words and
                    len(match) >= 4 and  # 至少2个汉字
                    match not in concepts):
                    concepts.append(match)

        return concepts[:top_k]

    def extract_hybrid_keywords(self, text: str, top_k: int = 10,
                               method: str = 'tfidf') -> List[str]:
        """
        混合关键词提取（短语+概念+传统关键词）

        Args:
            text: 输入文本
            top_k: 返回关键词数量
            method: 传统关键词提取方法

        Returns:
            混合关键词列表
        """
        # 提取短语
        phrases = self.extract_phrases(text, top_k=top_k//2)

        # 提取概念
        concepts = self.extract_concepts(text, top_k=top_k//3)

        # 提取传统关键词
        traditional_keywords = self.extract_keywords(
            text, top_k=top_k//3, method=method, with_weight=False
        )

        # 合并并去重
        all_keywords = phrases + concepts + traditional_keywords
        unique_keywords = []
        seen = set()

        for keyword in all_keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)

        return unique_keywords[:top_k]

    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 移除代码块
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

        # 移除markdown格式
        text = re.sub(r'[#*_~`\[\]]', ' ', text)

        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # 移除特殊字符，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\w\u4e00-\u9fff\s.,!?;:，。！？；：]', ' ', text)

        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        综合分析文本

        Args:
            text: 输入文本

        Returns:
            分析结果
        """
        clean_text = self._preprocess_text(text)

        # 分词
        words = list(jieba.cut(clean_text))

        # 提取关键词（带权重）
        tfidf_keywords = self.extract_keywords(text, top_k=15, method='tfidf', with_weight=True)
        textrank_keywords = self.extract_keywords(text, top_k=15, method='textrank', with_weight=True)

        # 提取短语和概念
        phrases = self.extract_phrases(text, top_k=10)
        concepts = self.extract_concepts(text, top_k=10)
        hybrid_keywords = self.extract_hybrid_keywords(text, top_k=15)

        # 统计信息
        word_count = len(words)
        unique_words = len(set(words))
        domain_word_count = sum(1 for word in words if word in self.agent_domain_words)

        return {
            'word_count': word_count,
            'unique_words': unique_words,
            'domain_word_ratio': domain_word_count / word_count if word_count > 0 else 0,
            'tfidf_keywords': tfidf_keywords,
            'textrank_keywords': textrank_keywords,
            'phrases': phrases,
            'concepts': concepts,
            'hybrid_keywords': hybrid_keywords,
            'domain_keywords': [word for word, _ in tfidf_keywords
                              if word in self.agent_domain_words]
        }

    def compare_methods(self, text: str, top_k: int = 10) -> Dict[str, List]:
        """
        比较不同关键词提取方法

        Args:
            text: 输入文本
            top_k: 关键词数量

        Returns:
            不同方法的结果比较
        """
        tfidf_result = self.extract_keywords(text, top_k=top_k, method='tfidf', with_weight=False)
        textrank_result = self.extract_keywords(text, top_k=top_k, method='textrank', with_weight=False)

        # 计算交集和差异
        tfidf_set = set(tfidf_result)
        textrank_set = set(textrank_result)

        intersection = list(tfidf_set & textrank_set)
        tfidf_only = list(tfidf_set - textrank_set)
        textrank_only = list(textrank_set - tfidf_set)

        return {
            'tfidf': tfidf_result,
            'textrank': textrank_result,
            'intersection': intersection,
            'tfidf_only': tfidf_only,
            'textrank_only': textrank_only
        }

def test_extractor():
    """测试关键词提取器"""
    print("=" * 60)
    print("关键词提取器测试")
    print("=" * 60)

    extractor = KeywordExtractor()

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

    # 提取关键词
    print("\nTF-IDF关键词:")
    tfidf_keywords = extractor.extract_keywords(test_text, top_k=10, method='tfidf', with_weight=True)
    for word, weight in tfidf_keywords:
        print(f"  {word}: {weight:.4f}")

    print("\nTextRank关键词:")
    textrank_keywords = extractor.extract_keywords(test_text, top_k=10, method='textrank', with_weight=True)
    for word, weight in textrank_keywords:
        print(f"  {word}: {weight:.4f}")

    print("\n方法比较:")
    comparison = extractor.compare_methods(test_text, top_k=8)
    print(f"  交集: {comparison['intersection']}")
    print(f"  TF-IDF独有: {comparison['tfidf_only']}")
    print(f"  TextRank独有: {comparison['textrank_only']}")

    print("\n文本分析:")
    analysis = extractor.analyze_text(test_text)
    print(f"  总词数: {analysis['word_count']}")
    print(f"  唯一词数: {analysis['unique_words']}")
    print(f"  领域词比例: {analysis['domain_word_ratio']:.2%}")
    print(f"  领域关键词: {analysis['domain_keywords']}")
    print(f"  短语: {analysis['phrases']}")
    print(f"  概念: {analysis['concepts']}")
    print(f"  混合关键词: {analysis['hybrid_keywords']}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='关键词提取器 - 使用jieba进行中文关键词提取')
    parser.add_argument('--text', type=str, help='输入文本')
    parser.add_argument('--file', type=str, help='输入文件路径')
    parser.add_argument('--top_k', type=int, default=10, help='返回关键词数量')
    parser.add_argument('--method', choices=['tfidf', 'textrank'], default='tfidf', help='提取方法')
    parser.add_argument('--test', action='store_true', help='运行测试')

    args = parser.parse_args()

    extractor = KeywordExtractor()

    if args.test:
        test_extractor()
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            keywords = extractor.extract_keywords(text, top_k=args.top_k, method=args.method, with_weight=True)
            print(f"文件: {args.file}")
            print(f"关键词 ({args.method}):")
            for word, weight in keywords:
                print(f"  {word}: {weight:.4f}")
        except Exception as e:
            print(f"处理文件失败: {e}")
    elif args.text:
        keywords = extractor.extract_keywords(args.text, top_k=args.top_k, method=args.method, with_weight=True)
        print(f"关键词 ({args.method}):")
        for word, weight in keywords:
            print(f"  {word}: {weight:.4f}")
    else:
        print("使用说明:")
        print("  --text <文本>     输入文本")
        print("  --file <路径>     输入文件")
        print("  --top_k <数量>    返回关键词数量")
        print("  --method <方法>   提取方法 (tfidf/textrank)")
        print("  --test            运行测试")
        print("\n示例:")
        print("  python keyword_extractor.py --text \"提示链模式的应用场景\"")
        print("  python keyword_extractor.py --file text/07-Chapter-01-Prompt-Chaining.md --top_k 15")
        print("  python keyword_extractor.py --test")