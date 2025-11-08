"""
检索结果数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class SearchResult:
    """检索结果"""
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    embedding_model: Optional[str] = None
    created_at: Optional[datetime] = None
    keywords: List[str] = field(default_factory=list)

    @property
    def title(self) -> str:
        """获取文档标题"""
        return self.metadata.get('title', '无标题')

    @property
    def source_file(self) -> str:
        """获取源文件路径"""
        return self.metadata.get('source_file', '未知')

    @property
    def has_code(self) -> bool:
        """是否包含代码"""
        return self.metadata.get('has_code', False)

    @property
    def has_list(self) -> bool:
        """是否包含列表"""
        return self.metadata.get('has_list', False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'chunk_id': self.chunk_id,
            'document_id': self.document_id,
            'content': self.content,
            'metadata': self.metadata,
            'similarity_score': self.similarity_score,
            'embedding_model': self.embedding_model,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'keywords': self.keywords
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """从字典创建"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])

        return cls(
            chunk_id=data['chunk_id'],
            document_id=data['document_id'],
            content=data['content'],
            metadata=data['metadata'],
            similarity_score=data['similarity_score'],
            embedding_model=data.get('embedding_model'),
            created_at=created_at,
            keywords=data.get('keywords', [])
        )


@dataclass
class RerankedResult:
    """重排序结果"""
    search_result: SearchResult
    reranker_score: float
    reranker_model: str
    combined_score: Optional[float] = None

    @property
    def chunk_id(self) -> str:
        """文档块ID"""
        return self.search_result.chunk_id

    @property
    def similarity_score(self) -> float:
        """相似度分数"""
        return self.search_result.similarity_score

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'search_result': self.search_result.to_dict(),
            'reranker_score': self.reranker_score,
            'reranker_model': self.reranker_model,
            'combined_score': self.combined_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RerankedResult':
        """从字典创建"""
        search_result = SearchResult.from_dict(data['search_result'])
        return cls(
            search_result=search_result,
            reranker_score=data['reranker_score'],
            reranker_model=data['reranker_model'],
            combined_score=data.get('combined_score')
        )


@dataclass
class QueryHistory:
    """查询历史记录"""
    query: str
    timestamp: datetime
    result_count: int
    search_mode: str = "vector"
    reranker_enabled: bool = False
    search_time: Optional[float] = None
    results: Optional[List[SearchResult]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'query': self.query,
            'timestamp': self.timestamp.isoformat(),
            'result_count': self.result_count,
            'search_mode': self.search_mode,
            'reranker_enabled': self.reranker_enabled,
            'search_time': self.search_time,
            'results': [r.to_dict() for r in self.results] if self.results else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryHistory':
        """从字典创建"""
        timestamp = datetime.fromisoformat(data['timestamp'])
        results = None
        if data.get('results'):
            results = [SearchResult.from_dict(r) for r in data['results']]

        return cls(
            query=data['query'],
            timestamp=timestamp,
            result_count=data['result_count'],
            search_mode=data.get('search_mode', 'vector'),
            reranker_enabled=data.get('reranker_enabled', False),
            search_time=data.get('search_time'),
            results=results
        )


@dataclass
class SearchStats:
    """检索统计信息"""
    query: str
    total_results: int
    search_time: float
    reranker_time: Optional[float] = None
    search_mode: str = "vector"
    reranker_enabled: bool = False
    average_similarity: Optional[float] = None
    average_reranker_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'query': self.query,
            'total_results': self.total_results,
            'search_time': self.search_time,
            'reranker_time': self.reranker_time,
            'search_mode': self.search_mode,
            'reranker_enabled': self.reranker_enabled,
            'average_similarity': self.average_similarity,
            'average_reranker_score': self.average_reranker_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchStats':
        """从字典创建"""
        return cls(**data)