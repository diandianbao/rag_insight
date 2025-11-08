"""
文档向量化处理工具
将项目中的文档进行分割、向量化并存储到pgvector数据库
"""

import os
import sys
import glob
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_splitter import DocumentSplitter
from vector_store import PgVectorStore, VectorStoreConfig, DocumentChunk


class DocumentVectorizer:
    """文档向量化处理器"""

    def __init__(self, database_url: str = "postgresql://localhost/hello_vector"):
        self.document_splitter = DocumentSplitter()

        # 配置向量存储
        self.config = VectorStoreConfig(
            database_url=database_url,
            table_name="document_chunks"
        )
        self.vector_store = PgVectorStore(self.config)

    def initialize(self) -> bool:
        """初始化向量存储系统"""
        try:
            print("初始化向量存储系统...")

            # 连接数据库
            self.vector_store.connect()
            print("✓ 数据库连接成功")

            # 创建表
            self.vector_store.create_table()
            print("✓ 向量存储表创建成功")

            # 健康检查
            health = self.vector_store.health_check()
            print(f"✓ 健康检查: {health}")

            return True

        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False

    def process_single_document(self, file_path: str, document_id: str = None) -> bool:
        """处理单个文档文件"""
        try:
            if not document_id:
                document_id = Path(file_path).stem

            print(f"处理文档: {file_path}")

            # 读取文档内容
            with open(file_path, 'r', encoding='utf-8') as f:
                # 分割文档
                chunks = self.document_splitter.split_document(file_path)
                print(f"  - 分割为 {len(chunks)} 个文档块")

            # 转换为向量存储格式
            vector_chunks = []
            for i, chunk in enumerate(chunks):
                vector_chunk = DocumentChunk(
                    content=chunk.content,
                    metadata=chunk.metadata,
                    chunk_id=f"{document_id}_chunk_{i}",
                    document_id=document_id
                )
                vector_chunks.append(vector_chunk)

            # 批量向量化存储
            success = self.vector_store.batch_embed_and_store(vector_chunks)

            if success:
                print(f"  ✓ 文档 {document_id} 向量化存储完成")
                return True
            else:
                print(f"  ❌ 文档 {document_id} 向量化存储失败")
                return False

        except Exception as e:
            print(f"  ❌ 处理文档 {file_path} 失败: {e}")
            return False

    def process_directory(self, directory_path: str, pattern: str = "*.md") -> dict:
        """处理目录中的所有文档"""
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "failed_files": []
        }

        # 查找所有匹配的文件
        search_pattern = os.path.join(directory_path, pattern)
        files = glob.glob(search_pattern)
        results["total_files"] = len(files)

        print(f"发现 {len(files)} 个文档文件")

        for file_path in files:
            document_id = Path(file_path).stem

            if self.process_single_document(file_path, document_id):
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["failed_files"].append(file_path)

        return results

    def get_statistics(self) -> dict:
        """获取向量存储统计信息"""
        try:
            return self.vector_store.get_statistics()
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}

    def cleanup(self):
        """清理资源"""
        self.vector_store.disconnect()
        print("向量存储连接已关闭")


def main(db_url: str):
    """主函数 - 处理项目中的所有文档"""

    # 创建向量化处理器
    vectorizer = DocumentVectorizer(db_url)

    try:
        # 初始化系统
        if not vectorizer.initialize():
            print("系统初始化失败，退出")
            return

        print("\n=== 开始处理项目文档 ===")

        # 处理text目录中的所有markdown文档
        text_dir = os.path.join(os.path.dirname(__file__), "text")

        if os.path.exists(text_dir):
            results = vectorizer.process_directory(text_dir, "*.md")

            print(f"\n=== 处理结果 ===")
            print(f"总文件数: {results['total_files']}")
            print(f"成功: {results['successful']}")
            print(f"失败: {results['failed']}")

            if results['failed_files']:
                print(f"失败文件:")
                for file in results['failed_files']:
                    print(f"  - {file}")
        else:
            print(f"❌ 文档目录不存在: {text_dir}")

        # 显示最终统计信息
        print(f"\n=== 最终统计 ===")
        stats = vectorizer.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理资源
        vectorizer.cleanup()


if __name__ == "__main__":
    # 从环境变量获取数据库配置
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hello_vector")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    main(database_url)