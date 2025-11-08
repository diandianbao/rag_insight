"""
向量化存储测试脚本
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vector_store import PgVectorStore, VectorStoreConfig, DocumentChunk


def test_vector_store():
    """测试向量化存储功能"""

    # 从环境变量获取数据库配置，如果没有则使用默认值
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hello_vector")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # 配置向量存储
    config = VectorStoreConfig(
        database_url=database_url,
        table_name="document_chunks"
    )

    # 创建向量存储实例
    vector_store = PgVectorStore(config)

    try:
        print("=== 向量化存储测试开始 ===")

        # 1. 连接数据库
        print("\n1. 连接数据库...")
        vector_store.connect()
        print("✓ 数据库连接成功")

        # 2. 健康检查
        print("\n2. 健康检查...")
        health = vector_store.health_check()
        print(f"健康检查结果: {health}")

        # 3. 创建表
        print("\n3. 创建表...")
        vector_store.create_table(force_recreate=True)
        print("✓ 表创建成功")

        # 4. 测试向量化
        print("\n4. 测试向量化...")
        test_text = "这是一个测试文档，用于验证向量化功能"
        embedding = vector_store.embed_text(test_text)
        print(f"✓ 向量化成功，向量维度: {len(embedding)}")

        # 5. 创建测试文档块
        print("\n5. 创建测试文档块...")
        test_chunks = [
            DocumentChunk(
                content="智能体设计模式是现代人工智能系统的重要架构模式",
                metadata={"title": "智能体设计模式介绍", "section": "1.1"},
                chunk_id="test_chunk_1",
                document_id="test_doc_1"
            ),
            DocumentChunk(
                content="文档分割技术是RAG系统的核心组件之一",
                metadata={"title": "文档分割技术", "section": "2.3"},
                chunk_id="test_chunk_2",
                document_id="test_doc_1"
            ),
            DocumentChunk(
                content="向量化存储能够实现语义级别的文档检索",
                metadata={"title": "向量化存储", "section": "3.2"},
                chunk_id="test_chunk_3",
                document_id="test_doc_2"
            )
        ]

        # 6. 批量存储文档块
        print("\n6. 批量存储文档块...")
        success = vector_store.batch_embed_and_store(test_chunks)
        print(f"✓ 批量存储结果: {'成功' if success else '失败'}")

        # 7. 测试相似度搜索
        print("\n7. 测试相似度搜索...")
        query = "智能体架构模式"
        results = vector_store.search_similar(query, top_k=3)
        print(f"搜索查询: '{query}'")
        print(f"找到 {len(results)} 个相关文档:")

        for i, chunk in enumerate(results, 1):
            print(f"  {i}. 相似度: {chunk.metadata.get('similarity', 0):.4f}")
            print(f"     内容: {chunk.content[:80]}...")
            print(f"     文档ID: {chunk.document_id}")

        # 8. 获取统计信息
        print("\n8. 获取统计信息...")
        stats = vector_store.get_statistics()
        print(f"存储统计:")
        print(f"  - 总文档块数: {stats['total_chunks']}")
        print(f"  - 唯一文档数: {stats['unique_documents']}")
        print(f"  - 模型分布: {stats['model_distribution']}")

        print("\n=== 向量化存储测试完成 ===")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭连接
        vector_store.disconnect()
        print("\n数据库连接已关闭")


def test_integration_with_document_splitter():
    """测试与文档分割器的集成"""

    try:
        print("\n=== 与文档分割器集成测试 ===")

        # 从环境变量获取数据库配置，如果没有则使用默认值
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "hello_vector")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")

        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # 导入文档分割器
        from document_splitter import DocumentSplitter

        # 创建文档分割器实例
        splitter = DocumentSplitter()

        # 测试文档内容
        test_document = """
# 智能体设计模式

## 概述
智能体设计模式是现代人工智能系统的重要架构模式，它允许系统以自主的方式与环境交互。

## 核心组件
智能体通常包含感知、决策和执行三个核心组件。

### 感知组件
负责从环境中收集信息，包括传感器数据和用户输入。

### 决策组件
基于感知信息和内部状态做出决策，确定下一步行动。

### 执行组件
将决策转化为具体的行动，与环境进行交互。
        """

        # 创建一个临时文件用于测试
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_document)
            temp_file = f.name

        # 分割文档
        print("分割测试文档...")
        chunks = splitter.split_document(temp_file)
        print(f"✓ 文档分割完成，生成 {len(chunks)} 个文档块")

        # 清理临时文件
        os.unlink(temp_file)

        # 转换为向量存储格式
        vector_chunks = []
        for i, chunk in enumerate(chunks):
            vector_chunk = DocumentChunk(
                content=chunk.content,
                metadata=chunk.metadata,
                chunk_id=f"agent_design_{i}",
                document_id="agent_design_patterns"
            )
            vector_chunks.append(vector_chunk)

        # 配置向量存储
        config = VectorStoreConfig(
            database_url=database_url,
            table_name="document_chunks"
        )

        vector_store = PgVectorStore(config)
        vector_store.connect()

        # 创建表
        vector_store.create_table(force_recreate=True)

        # 批量存储
        print("批量向量化存储文档块...")
        success = vector_store.batch_embed_and_store(vector_chunks)

        if success:
            print("✓ 集成测试成功完成")

            # 测试检索
            query = "智能体的核心组件有哪些"
            results = vector_store.search_similar(query, top_k=3)
            print(f"\n检索查询: '{query}'")
            print(f"找到 {len(results)} 个相关文档:")

            for i, chunk in enumerate(results, 1):
                print(f"  {i}. 相似度: {chunk.metadata.get('similarity', 0):.4f}")
                print(f"     内容: {chunk.content[:60]}...")
        else:
            print("❌ 集成测试失败")

    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行基础测试
    test_vector_store()

    # 运行集成测试
    test_integration_with_document_splitter()