"""
RAG 检索器
实现向量检索功能
"""

import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from rag_cli.models.config import RetrieverConfig
from rag_cli.models.results import SearchResult, SearchStats
from vector_store import PgVectorStore, DocumentChunk


class RAGRetriever:
    """RAG 检索器"""

    def __init__(self, config: RetrieverConfig):
        self.config = config
        self.vector_store = PgVectorStore(config.vector_store_config)
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """连接向量数据库"""
        try:
            return self.vector_store.connect()
        except Exception as e:
            self.logger.error(f"连接向量数据库失败: {e}")
            return False

    def disconnect(self):
        """断开向量数据库连接"""
        self.vector_store.disconnect()

    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """
        向量检索

        Args:
            query: 查询文本
            top_k: 返回结果数量，如果为None则使用配置中的默认值

        Returns:
            检索结果列表
        """
        start_time = time.time()

        if top_k is None:
            top_k = self.config.search_config.default_top_k

        try:
            # 使用向量存储进行相似度搜索
            vector_chunks = self.vector_store.search_similar(query, top_k)

            # 转换为SearchResult对象
            results = []
            for chunk in vector_chunks:
                # 从元数据中提取相似度分数
                similarity_score = chunk.metadata.get("similarity", 0.0)

                # 创建SearchResult对象
                result = SearchResult(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    metadata=chunk.metadata,
                    similarity_score=similarity_score,
                    embedding_model=chunk.embedding_model,
                    created_at=chunk.created_at,
                    keywords=chunk.metadata.get("keywords", [])
                )
                results.append(result)

            search_time = time.time() - start_time
            self.logger.info(f"向量检索完成: 查询='{query}', 结果数={len(results)}, 耗时={search_time:.3f}s")

            return results

        except Exception as e:
            self.logger.error(f"向量检索失败: {e}")
            raise

    def get_search_stats(self, query: str, results: List[SearchResult],
                        search_time: float, reranker_time: Optional[float] = None) -> SearchStats:
        """
        获取检索统计信息

        Args:
            query: 查询文本
            results: 检索结果
            search_time: 检索耗时
            reranker_time: 重排序耗时（如果有）

        Returns:
            检索统计信息
        """
        if not results:
            return SearchStats(
                query=query,
                total_results=0,
                search_time=search_time,
                reranker_time=reranker_time,
                average_similarity=0.0
            )

        # 计算平均相似度
        avg_similarity = sum(r.similarity_score for r in results) / len(results)

        return SearchStats(
            query=query,
            total_results=len(results),
            search_time=search_time,
            reranker_time=reranker_time,
            average_similarity=avg_similarity
        )

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            db_connected = self.vector_store.connect()

            # 检查表是否存在
            health_status = self.vector_store.health_check()

            # 添加检索器特定的健康信息
            health_status.update({
                "retriever_ready": db_connected and health_status["table_exists"],
                "default_top_k": self.config.search_config.default_top_k
            })

            return health_status

        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                "database": False,
                "embedding_service": False,
                "table_exists": False,
                "retriever_ready": False,
                "default_top_k": self.config.search_config.default_top_k
            }