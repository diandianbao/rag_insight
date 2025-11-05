"""
Reranker 示例代码 - 使用 Qwen/Qwen3-Reranker-4B 模型

这个脚本演示了如何使用 reranker 模型对文档进行重新排序。
Reranker 通常用于检索增强生成(RAG)系统中，根据查询的相关性对候选文档进行排序。

注意：这个测试脚本需要配合 reranker web server 使用。
"""

import requests
import json
from typing import List, Tuple

def check_server_health() -> bool:
    """检查 reranker server 是否正常运行"""
    url = "http://localhost:11435/v1/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "healthy" and result.get("model_loaded"):
                print("✓ Reranker server 正常运行")
                return True
            else:
                print("✗ Reranker server 模型未加载")
                return False
        else:
            print(f"✗ Reranker server 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到 Reranker server: {e}")
        return False

def rerank_documents(query: str, documents: List[str], instruction: str = None) -> List[Tuple[str, float]]:
    """
    使用 reranker 模型对文档进行重新排序

    Args:
        query: 查询文本
        documents: 文档列表
        instruction: 可选的自定义指令

    Returns:
        排序后的文档列表，包含文档和相关性分数
    """
    url = "http://localhost:11435/v1/reranker"
    headers = {"Content-Type": "application/json"}

    # 构建符合server API的请求数据
    data = {
        "query": query,
        "documents": documents
    }

    # 如果提供了自定义指令，添加到请求中
    if instruction:
        data["instruction"] = instruction

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                scores = result["scores"]
                # 将文档和得分配对
                scored_docs = list(zip(documents, scores))
                # 按得分降序排序
                sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
                return sorted_docs
            else:
                raise Exception(f"API返回错误: {result.get('error', '未知错误')}")
        else:
            raise Exception(f"HTTP错误: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"✗ Reranking失败: {e}")
        # 返回原始文档顺序，分数为0
        return [(doc, 0.0) for doc in documents]

def test_reranker():
    """测试 reranker 功能"""
    print("=" * 60)
    print("Reranker 测试 - Qwen/Qwen3-Reranker-4B")
    print("=" * 60)

    # 首先检查server状态
    if not check_server_health():
        print("请先启动 reranker server: python reranker_server.py")
        return []

    # 测试数据
    query = "人工智能和机器学习"

    documents = [
        "人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。",
        "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
        "深度学习是机器学习的一个分支，使用具有多个层的神经网络。",
        "自然语言处理是人工智能的一个领域，专注于计算机与人类语言之间的交互。",
        "计算机视觉是人工智能的一个领域，使计算机能够从数字图像或视频中获取高级理解。",
        "强化学习是机器学习的一个领域，关注软件代理如何在环境中采取行动以最大化累积奖励。"
    ]

    print(f"\n查询: '{query}'")
    print(f"文档数量: {len(documents)}")
    print(f"\n原始文档顺序:")
    for i, doc in enumerate(documents):
        print(f"  {i+1}. {doc[:50]}...")

    # 执行 reranking
    print(f"\n执行 Reranking...")
    ranked_docs = rerank_documents(query, documents)

    print(f"\n重新排序后的结果:")
    print("-" * 60)
    for i, (doc, score) in enumerate(ranked_docs):
        print(f"{i+1}. [相关性: {score:.4f}] {doc[:60]}...")

    return ranked_docs

def test_multiple_queries():
    """测试多个查询的 reranking"""
    print("\n" + "=" * 60)
    print("多查询测试")
    print("=" * 60)

    # 文档集合
    documents = [
        "Python是一种高级编程语言，以其简洁的语法和强大的库而闻名。",
        "Java是一种面向对象的编程语言，广泛用于企业级应用开发。",
        "JavaScript主要用于网页开发，可以在浏览器中运行。",
        "C++是一种系统编程语言，提供了对硬件的低级访问。",
        "SQL是用于管理和查询关系数据库的标准语言。",
        "HTML是用于创建网页的标准标记语言。"
    ]

    # 不同的查询
    queries = [
        "网页开发",
        "系统编程",
        "数据库管理"
    ]

    for query in queries:
        print(f"\n查询: '{query}'")
        ranked_docs = rerank_documents(query, documents)

        print(f"\n前3个相关文档:")
        for i, (doc, score) in enumerate(ranked_docs[:3]):
            print(f"  {i+1}. [分数: {score:.4f}] {doc[:50]}...")
        print()

def test_custom_instruction():
    """测试自定义指令功能"""
    print("\n" + "=" * 60)
    print("自定义指令测试")
    print("=" * 60)

    query = "Python编程"

    documents = [
        "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
        "Python的设计哲学强调代码的可读性和简洁的语法。",
        "Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。",
        "Python拥有丰富的标准库和第三方库，适用于各种应用场景。",
        "Python在数据科学、机器学习、Web开发等领域有广泛应用。"
    ]

    # 使用自定义指令
    instruction = "请重点关注Python语言的语法特性和应用领域"

    print(f"查询: '{query}'")
    print(f"自定义指令: '{instruction}'")

    ranked_docs = rerank_documents(query, documents, instruction)

    print(f"\n使用自定义指令的排序结果:")
    for i, (doc, score) in enumerate(ranked_docs):
        print(f"{i+1}. [分数: {score:.4f}] {doc[:60]}...")

if __name__ == "__main__":
    # 测试基本 reranking
    ranked_results = test_reranker()

    # 测试多查询
    test_multiple_queries()

    # 测试自定义指令
    test_custom_instruction()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)