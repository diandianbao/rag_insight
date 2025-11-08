"""
向量化存储模块
实现文档块的向量化存储到pgvector数据库
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import psycopg2
from psycopg2.extras import Json
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VectorStoreConfig:
    """向量存储配置"""
    database_url: str
    table_name: str = "document_chunks"
    embedding_model: str = "qwen3-embedding:4b"
    embedding_endpoint: str = "http://localhost:11434/api/embeddings"
    vector_dimension: int = 2560  # qwen3-embedding:4b的实际向量维度
    batch_size: int = 100
    timeout: int = 30


@dataclass
class DocumentChunk:
    """文档块数据结构（扩展版本）"""
    content: str
    metadata: dict
    chunk_id: str
    document_id: str
    vector: Optional[List[float]] = None
    embedding_model: Optional[str] = None
    created_at: Optional[datetime] = None


class VectorStoreError(Exception):
    """向量存储基础异常"""
    pass


class EmbeddingError(VectorStoreError):
    """向量化异常"""
    pass


class DatabaseError(VectorStoreError):
    """数据库操作异常"""
    pass


class ConnectionError(VectorStoreError):
    """连接异常"""
    pass


class PgVectorStore:
    """基于pgvector的向量存储实现"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.connection = None
        self._ensure_pgvector_extension()

    def connect(self) -> bool:
        """连接PostgreSQL + pgvector数据库"""
        try:
            self.connection = psycopg2.connect(self.config.database_url)
            self.connection.autocommit = True
            logger.info("成功连接到向量数据库")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise ConnectionError(f"数据库连接失败: {e}")

    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")

    def _ensure_pgvector_extension(self):
        """确保pgvector扩展已安装"""
        try:
            conn = psycopg2.connect(self.config.database_url)
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.close()
            conn.close()
            logger.info("pgvector扩展已确保安装")
        except Exception as e:
            logger.warning(f"pgvector扩展检查失败: {e}")

    def create_table(self, force_recreate: bool = False) -> bool:
        """创建支持向量的文档块表"""
        if not self.connection:
            raise ConnectionError("数据库未连接")

        try:
            cursor = self.connection.cursor()

            # 如果强制重新创建，先删除现有表
            if force_recreate:
                cursor.execute(f"DROP TABLE IF EXISTS {self.config.table_name}")
                logger.info(f"删除现有表: {self.config.table_name}")

            # 创建文档块表
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                id SERIAL PRIMARY KEY,
                chunk_id VARCHAR(255) UNIQUE NOT NULL,
                document_id VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                vector VECTOR({self.config.vector_dimension}),
                embedding_model VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            cursor.execute(create_table_sql)

            # 创建字段索引
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_document_id ON {self.config.table_name} (document_id)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_created_at ON {self.config.table_name} (created_at)")

            # 创建向量索引（对于高维向量使用HNSW）
            try:
                if self.config.vector_dimension <= 2000:
                    # 对于2000维以下的向量使用IVFFlat
                    create_index_sql = f"""
                    CREATE INDEX IF NOT EXISTS idx_vector
                    ON {self.config.table_name}
                    USING ivfflat (vector vector_l2_ops)
                    WITH (lists = 100)
                    """
                else:
                    # 对于高维向量使用HNSW
                    create_index_sql = f"""
                    CREATE INDEX IF NOT EXISTS idx_vector
                    ON {self.config.table_name}
                    USING hnsw (vector vector_l2_ops)
                    WITH (m = 16, ef_construction = 64)
                    """
                cursor.execute(create_index_sql)
                logger.info("向量索引创建成功")
            except Exception as e:
                logger.warning(f"向量索引创建失败，将使用顺序扫描: {e}")
                # 如果索引创建失败，仍然继续，只是性能会受影响

            cursor.close()
            logger.info(f"表 {self.config.table_name} 创建成功")
            return True

        except Exception as e:
            logger.error(f"创建表失败: {e}")
            raise DatabaseError(f"创建表失败: {e}")

    def embed_text(self, text: str) -> List[float]:
        """使用Ollama的embedding模型向量化文本"""
        try:
            payload = {
                "model": self.config.embedding_model,
                "prompt": text
            }

            response = requests.post(
                self.config.embedding_endpoint,
                json=payload,
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", [])

                if len(embedding) != self.config.vector_dimension:
                    logger.warning(f"向量维度不匹配: 期望{self.config.vector_dimension}, 实际{len(embedding)}")

                return embedding
            else:
                logger.error(f"向量化请求失败: {response.status_code} - {response.text}")
                raise EmbeddingError(f"向量化请求失败: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"向量化服务连接失败: {e}")
            raise EmbeddingError(f"向量化服务连接失败: {e}")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文本"""
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
                # 避免频繁请求导致服务过载
                time.sleep(0.1)
            except EmbeddingError as e:
                logger.error(f"批量向量化失败: {e}")
                # 对于失败的文本，使用零向量作为占位符
                embeddings.append([0.0] * self.config.vector_dimension)
        return embeddings

    def store_chunk(self, chunk: DocumentChunk) -> bool:
        """存储单个文档块"""
        if not self.connection:
            raise ConnectionError("数据库未连接")

        try:
            cursor = self.connection.cursor()

            # 如果还没有向量，先进行向量化
            if chunk.vector is None:
                chunk.vector = self.embed_text(chunk.content)
                chunk.embedding_model = self.config.embedding_model

            insert_sql = f"""
            INSERT INTO {self.config.table_name}
            (chunk_id, document_id, content, metadata, vector, embedding_model)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                vector = EXCLUDED.vector,
                embedding_model = EXCLUDED.embedding_model
            """

            cursor.execute(insert_sql, (
                chunk.chunk_id,
                chunk.document_id,
                chunk.content,
                Json(chunk.metadata),
                chunk.vector,
                chunk.embedding_model
            ))

            cursor.close()
            logger.debug(f"文档块 {chunk.chunk_id} 存储成功")
            return True

        except Exception as e:
            logger.error(f"存储文档块失败: {e}")
            raise DatabaseError(f"存储文档块失败: {e}")

    def store_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """批量存储文档块"""
        success_count = 0
        for chunk in chunks:
            try:
                self.store_chunk(chunk)
                success_count += 1
            except DatabaseError as e:
                logger.error(f"存储文档块 {chunk.chunk_id} 失败: {e}")

        logger.info(f"批量存储完成: {success_count}/{len(chunks)} 成功")
        return success_count == len(chunks)

    def batch_embed_and_store(self, chunks: List[DocumentChunk]) -> bool:
        """批量向量化并存储文档块"""
        try:
            # 批量向量化
            texts = [chunk.content for chunk in chunks]
            embeddings = self.embed_batch(texts)

            # 更新文档块的向量信息
            for chunk, embedding in zip(chunks, embeddings):
                chunk.vector = embedding
                chunk.embedding_model = self.config.embedding_model

            # 批量存储
            return self.store_chunks(chunks)

        except Exception as e:
            logger.error(f"批量向量化存储失败: {e}")
            raise VectorStoreError(f"批量向量化存储失败: {e}")

    def search_similar(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """基于向量相似度搜索相关文档"""
        if not self.connection:
            raise ConnectionError("数据库未连接")

        try:
            # 向量化查询文本
            query_vector = self.embed_text(query)

            cursor = self.connection.cursor()

            search_sql = f"""
            SELECT chunk_id, document_id, content, metadata, embedding_model, created_at,
                   (1 - (vector <-> %s::vector)) as similarity
            FROM {self.config.table_name}
            ORDER BY vector <-> %s::vector
            LIMIT %s
            """

            cursor.execute(search_sql, (query_vector, query_vector, top_k))
            results = cursor.fetchall()
            cursor.close()

            # 转换为DocumentChunk对象
            chunks = []
            for row in results:
                chunk = DocumentChunk(
                    content=row[2],
                    metadata=row[3] if row[3] else {},
                    chunk_id=row[0],
                    document_id=row[1],
                    embedding_model=row[4],
                    created_at=row[5]
                )
                # 添加相似度分数到元数据
                chunk.metadata["similarity"] = float(row[6])
                chunks.append(chunk)

            logger.info(f"相似度搜索完成: 找到 {len(chunks)} 个相关文档块")
            return chunks

        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            raise VectorStoreError(f"相似度搜索失败: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        if not self.connection:
            raise ConnectionError("数据库未连接")

        try:
            cursor = self.connection.cursor()

            # 总文档块数
            cursor.execute(f"SELECT COUNT(*) FROM {self.config.table_name}")
            total_chunks = cursor.fetchone()[0]

            # 唯一文档数
            cursor.execute(f"SELECT COUNT(DISTINCT document_id) FROM {self.config.table_name}")
            unique_documents = cursor.fetchone()[0]

            # 向量维度分布
            cursor.execute(f"SELECT embedding_model, COUNT(*) FROM {self.config.table_name} GROUP BY embedding_model")
            model_distribution = dict(cursor.fetchall())

            cursor.close()

            return {
                "total_chunks": total_chunks,
                "unique_documents": unique_documents,
                "model_distribution": model_distribution,
                "table_name": self.config.table_name
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise DatabaseError(f"获取统计信息失败: {e}")

    def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        health_status = {
            "database": False,
            "embedding_service": False,
            "table_exists": False
        }

        # 检查数据库连接
        try:
            if self.connection and not self.connection.closed:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                health_status["database"] = True
        except Exception:
            health_status["database"] = False

        # 检查向量化服务
        try:
            response = requests.get(
                self.config.embedding_endpoint.replace("/api/embeddings", "/api/tags"),
                timeout=5
            )
            health_status["embedding_service"] = response.status_code == 200
        except Exception:
            health_status["embedding_service"] = False

        # 检查表是否存在
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = %s
                )
            """, (self.config.table_name,))
            health_status["table_exists"] = cursor.fetchone()[0]
            cursor.close()
        except Exception:
            health_status["table_exists"] = False

        return health_status


# 使用示例
if __name__ == "__main__":
    # 配置向量存储
    config = VectorStoreConfig(
        database_url="postgresql://localhost/hello_vector",
        table_name="document_chunks"
    )

    # 创建向量存储实例
    vector_store = PgVectorStore(config)

    try:
        # 连接数据库
        vector_store.connect()

        # 创建表
        vector_store.create_table()

        # 健康检查
        health = vector_store.health_check()
        print("健康检查结果:", health)

        # 获取统计信息
        stats = vector_store.get_statistics()
        print("存储统计:", stats)

    except Exception as e:
        print(f"向量存储初始化失败: {e}")
    finally:
        vector_store.disconnect()