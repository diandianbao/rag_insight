#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGRetriever 测试
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import yaml
from rich.console import Console
from rich.panel import Panel

from rag_cli.core.retriever import RAGRetriever
from rag_cli.models.config import RetrieverConfig, VectorStoreConfig, SearchConfig


console = Console()


def load_test_config() -> RetrieverConfig:
    """加载测试配置"""
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        console.print(f"[red]❌ 配置文件不存在: {config_path}[/red]")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # 创建配置对象
        vector_store_config = VectorStoreConfig(
            database_url=config_data['vector_store']['database_url'],
            table_name=config_data['vector_store']['table_name'],
            embedding_model=config_data['vector_store']['embedding_model'],
            embedding_endpoint=config_data['vector_store']['embedding_endpoint']
        )

        search_config = SearchConfig(
            default_top_k=config_data.get('search', {}).get('default_top_k', 10)
        )

        return RetrieverConfig(
            vector_store_config=vector_store_config,
            search_config=search_config
        )

    except Exception as e:
        console.print(f"[red]❌ 配置文件加载失败: {e}[/red]")
        sys.exit(1)


def test_connection():
    """测试数据库连接"""
    console.print("[bold cyan]🧪 测试数据库连接...[/bold cyan]")

    config = load_test_config()
    retriever = RAGRetriever(config)

    try:
        connected = retriever.connect()
        if connected:
            console.print("[green]✓ 数据库连接成功[/green]")
        else:
            console.print("[red]❌ 数据库连接失败[/red]")
            return False

        # 健康检查
        health = retriever.health_check()
        console.print(f"[dim]健康检查结果: {health}[/dim]")

        retriever.disconnect()
        return True

    except Exception as e:
        console.print(f"[red]❌ 连接测试失败: {e}[/red]")
        return False


def test_search():
    """测试检索功能"""
    console.print("\n[bold cyan]🧪 测试检索功能...[/bold cyan]")

    config = load_test_config()
    retriever = RAGRetriever(config)

    try:
        # 连接数据库
        if not retriever.connect():
            console.print("[red]❌ 数据库连接失败，无法测试检索[/red]")
            return False

        # 测试查询
        test_queries = [
            "记忆管理",
            "上下文工程",
            "向量数据库",
            "开发框架"
        ]

        for query in test_queries:
            console.print(f"\n[bold]查询:[/bold] '{query}'")

            try:
                # 向量检索
                results = retriever.search(query, top_k=5)
                console.print(f"  [green]✓ 向量检索: {len(results)} 个结果[/green]")

                # 显示前3个结果
                for i, result in enumerate(results[:3], 1):
                    console.print(f"    {i}. {result.title} (相似度: {result.similarity_score:.3f})")

            except Exception as e:
                console.print(f"  [red]❌ 检索失败: {e}[/red]")

        retriever.disconnect()
        return True

    except Exception as e:
        console.print(f"[red]❌ 检索测试失败: {e}[/red]")
        return False


def test_validation():
    """测试参数验证"""
    console.print("\n[bold cyan]🧪 测试参数验证...[/bold cyan]")

    from rag_cli.utils.validation import validate_query, validate_top_k

    # 测试查询验证
    test_cases = [
        ("", False),  # 空查询
        ("a", False),  # 太短
        ("正常查询", True),  # 正常查询
        ("x" * 1001, False),  # 太长
    ]

    for query, should_pass in test_cases:
        try:
            validate_query(query)
            if should_pass:
                console.print(f"  [green]✓ 查询验证通过: '{query}'[/green]")
            else:
                console.print(f"  [red]❌ 查询验证应该失败但通过了: '{query}'[/red]")
        except ValueError as e:
            if not should_pass:
                console.print(f"  [green]✓ 查询验证正确失败: '{query}' - {e}[/green]")
            else:
                console.print(f"  [red]❌ 查询验证应该通过但失败了: '{query}' - {e}[/red]")

    # 测试top_k验证
    top_k_cases = [
        (0, False),  # 0
        (5, True),   # 正常
        (101, False),  # 超过限制
    ]

    for top_k, should_pass in top_k_cases:
        try:
            validate_top_k(top_k, max_limit=100)
            if should_pass:
                console.print(f"  [green]✓ top_k验证通过: {top_k}[/green]")
            else:
                console.print(f"  [red]❌ top_k验证应该失败但通过了: {top_k}[/red]")
        except ValueError as e:
            if not should_pass:
                console.print(f"  [green]✓ top_k验证正确失败: {top_k} - {e}[/green]")
            else:
                console.print(f"  [red]❌ top_k验证应该通过但失败了: {top_k} - {e}[/red]")


def main():
    """主测试函数"""
    console.print(Panel(
        "RAGRetriever 测试套件",
        title="测试开始",
        border_style="cyan"
    ))

    # 运行测试
    tests = [
        ("数据库连接", test_connection),
        ("检索功能", test_search),
        ("参数验证", test_validation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            console.print(f"[red]❌ {test_name} 测试异常: {e}[/red]")
            results.append((test_name, False))

    # 显示测试结果
    console.print("\n[bold cyan]📊 测试结果汇总[/bold cyan]")
    passed = 0
    for test_name, success in results:
        if success:
            console.print(f"  [green]✓ {test_name}: 通过[/green]")
            passed += 1
        else:
            console.print(f"  [red]❌ {test_name}: 失败[/red]")

    total = len(tests)
    console.print(f"\n[bold]{passed}/{total} 个测试通过[/bold]")

    if passed == total:
        console.print("[green]🎉 所有测试通过！[/green]")
    else:
        console.print("[yellow]⚠️  部分测试失败，请检查配置和数据库连接[/yellow]")


if __name__ == "__main__":
    main()