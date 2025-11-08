#!/usr/bin/env python3
"""
简化向量存储测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vector_store import PgVectorStore, VectorStoreConfig, DocumentChunk

def test_simple():
    """简化测试"""

    # 从环境变量获取数据库配置
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
        print("=== 简化向量存储测试 ===")

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

        # 5. 存储单个文档块
        print("\n5. 存储单个文档块...")
        test_chunk = DocumentChunk(
            content="智能体设计模式是现代人工智能系统的重要架构模式",
            metadata={"title": "智能体设计模式介绍", "section": "1.1"},
            chunk_id="simple_test_chunk",
            document_id="test_doc_1"
        )

        success = vector_store.store_chunk(test_chunk)
        print(f"✓ 存储结果: {'成功' if success else '失败'}")

        # 6. 获取统计信息
        print("\n6. 获取统计信息...")
        stats = vector_store.get_statistics()
        print(f"存储统计:")
        print(f"  - 总文档块数: {stats['total_chunks']}")
        print(f"  - 唯一文档数: {stats['unique_documents']}")

        print("\n=== 简化测试完成 ===")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭连接
        vector_store.disconnect()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    test_simple()