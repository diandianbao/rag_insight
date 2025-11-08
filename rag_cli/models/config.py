"""
配置数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class VectorStoreConfig:
    """向量存储配置"""
    database_url: str
    table_name: str = "document_chunks"
    embedding_model: str = "qwen3-embedding:4b"
    embedding_endpoint: str = "http://localhost:11434/api/embeddings"
    vector_dimension: int = 2560
    batch_size: int = 100
    timeout: int = 30

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorStoreConfig':
        """从字典创建配置对象"""
        return cls(**data)


@dataclass
class RerankerConfig:
    """重排序器配置"""
    enabled: bool = True
    endpoint: str = "http://localhost:11435/v1/reranker"
    model: str = "Qwen/Qwen3-Reranker-4B"
    timeout: int = 30

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RerankerConfig':
        """从字典创建配置对象"""
        return cls(**data)


@dataclass
class DisplayConfig:
    """显示配置"""
    theme: str = "dark"
    max_results: int = 10
    show_scores: bool = True
    highlight_keywords: bool = True
    show_progress: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisplayConfig':
        """从字典创建配置对象"""
        return cls(**data)


@dataclass
class SearchConfig:
    """检索配置"""
    default_top_k: int = 10
    similarity_threshold: float = 0.5
    enable_filters: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchConfig':
        """从字典创建配置对象"""
        return cls(**data)


@dataclass
class InteractiveConfig:
    """交互式配置"""
    enable_history: bool = True
    max_history_size: int = 50
    auto_save_session: bool = True
    session_file: str = "~/.rag_cli/session.json"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractiveConfig':
        """从字典创建配置对象"""
        return cls(**data)


@dataclass
class RetrieverConfig:
    """检索器配置"""
    vector_store_config: VectorStoreConfig
    search_config: SearchConfig = field(default_factory=SearchConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetrieverConfig':
        """从字典创建配置对象"""
        vector_store_config = VectorStoreConfig.from_dict(data.get('vector_store', {}))
        search_config = SearchConfig.from_dict(data.get('search', {}))
        return cls(vector_store_config=vector_store_config, search_config=search_config)


@dataclass
class SessionConfig:
    """会话配置"""
    retriever_config: RetrieverConfig
    reranker: RerankerConfig
    display: DisplayConfig
    search: SearchConfig
    interactive: InteractiveConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionConfig':
        """从字典创建配置对象"""
        retriever_config = RetrieverConfig.from_dict(data)
        reranker = RerankerConfig.from_dict(data.get('reranker', {}))
        display = DisplayConfig.from_dict(data.get('display', {}))
        search = SearchConfig.from_dict(data.get('search', {}))
        interactive = InteractiveConfig.from_dict(data.get('interactive', {}))

        return cls(
            retriever_config=retriever_config,
            reranker=reranker,
            display=display,
            search=search,
            interactive=interactive
        )