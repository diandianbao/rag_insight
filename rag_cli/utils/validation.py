"""
参数验证工具
"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse


def validate_config(config_data: Dict[str, Any]) -> bool:
    """
    验证配置数据

    Args:
        config_data: 配置数据字典

    Returns:
        验证是否通过

    Raises:
        ValueError: 配置验证失败
    """
    # 检查必需字段
    required_fields = ['vector_store', 'reranker', 'display']
    for field in required_fields:
        if field not in config_data:
            raise ValueError(f"缺少必需的配置字段: {field}")

    # 验证向量存储配置
    vector_store = config_data['vector_store']
    if 'database_url' not in vector_store:
        raise ValueError("向量存储配置缺少 database_url 字段")

    # 验证数据库URL格式
    db_url = vector_store['database_url']
    if not _is_valid_database_url(db_url):
        raise ValueError(f"无效的数据库URL格式: {db_url}")

    # 验证重排序配置
    reranker = config_data.get('reranker', {})
    if reranker.get('enabled', False):
        if 'endpoint' not in reranker:
            raise ValueError("重排序已启用但缺少 endpoint 字段")

    # 验证显示配置
    display = config_data.get('display', {})
    if 'max_results' in display:
        max_results = display['max_results']
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("max_results 必须是正整数")

    return True


def validate_query(query: str) -> bool:
    """
    验证查询文本

    Args:
        query: 查询文本

    Returns:
        验证是否通过

    Raises:
        ValueError: 查询验证失败
    """
    if not query or not query.strip():
        raise ValueError("查询内容不能为空")

    if len(query.strip()) < 2:
        raise ValueError("查询内容至少需要2个字符")

    if len(query.strip()) > 1000:
        raise ValueError("查询内容不能超过1000个字符")

    # 检查是否包含特殊字符（可选）
    # 这里可以根据需要添加更多的验证规则

    return True


def validate_top_k(top_k: int, max_limit: int = 100) -> bool:
    """
    验证top_k参数

    Args:
        top_k: 返回结果数量
        max_limit: 最大限制

    Returns:
        验证是否通过

    Raises:
        ValueError: top_k验证失败
    """
    if not isinstance(top_k, int):
        raise ValueError("top_k 必须是整数")

    if top_k <= 0:
        raise ValueError("top_k 必须是正整数")

    if top_k > max_limit:
        raise ValueError(f"top_k 不能超过 {max_limit}")

    return True


def _is_valid_database_url(url: str) -> bool:
    """
    检查数据库URL格式是否有效

    Args:
        url: 数据库URL

    Returns:
        是否有效
    """
    try:
        parsed = urlparse(url)
        # 检查协议
        if parsed.scheme not in ['postgresql', 'postgres']:
            return False

        # 检查主机名
        if not parsed.hostname:
            return False

        # 检查数据库名
        if not parsed.path or len(parsed.path) <= 1:
            return False

        return True
    except Exception:
        return False


def validate_search_mode(mode: str) -> bool:
    """
    验证检索模式

    Args:
        mode: 检索模式

    Returns:
        验证是否通过

    Raises:
        ValueError: 模式验证失败
    """
    valid_modes = ['vector']
    if mode not in valid_modes:
        raise ValueError(f"无效的检索模式: {mode}，有效模式: {valid_modes}")

    return True


def validate_export_format(format: str) -> bool:
    """
    验证导出格式

    Args:
        format: 导出格式

    Returns:
        验证是否通过

    Raises:
        ValueError: 格式验证失败
    """
    valid_formats = ['json', 'markdown', 'csv']
    if format not in valid_formats:
        raise ValueError(f"无效的导出格式: {format}，有效格式: {valid_formats}")

    return True