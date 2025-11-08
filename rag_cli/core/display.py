"""
结果显示模块
实现丰富的终端结果显示功能
"""

from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from rag_cli.models.config import DisplayConfig
from rag_cli.models.results import SearchResult, RerankedResult


class ResultDisplay:
    """结果显示器"""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.console = Console()

    def show_search_results(self, results: List[SearchResult], query: str = ""):
        """显示检索结果"""
        if not results:
            self.console.print("[yellow]⚠️  没有找到相关文档[/yellow]")
            return

        # 创建结果表格
        table = Table(title=f"RAG 检索结果 - '{query}'")
        table.add_column("排名", style="cyan", width=6)
        table.add_column("文档ID", style="green", width=15)
        table.add_column("标题", style="white", width=30)
        table.add_column("相似度", style="magenta", width=10)

        if self.config.show_scores:
            table.add_column("关键词分数", style="yellow", width=12)

        # 添加数据行
        for i, result in enumerate(results[:self.config.max_results], 1):
            row = [
                str(i),
                result.chunk_id[:14] + "..." if len(result.chunk_id) > 14 else result.chunk_id,
                result.title[:28] + "..." if len(result.title) > 28 else result.title,
                f"{result.similarity_score:.3f}"
            ]

            if self.config.show_scores:
                keyword_score = result.metadata.get("keyword_score", 0.0)
                row.append(f"{keyword_score:.3f}")

            table.add_row(*row)

        self.console.print(table)

    def show_comparison(self, before: List[SearchResult], after: List[RerankedResult], query: str = ""):
        """显示reranker前后的对比"""
        if not before or not after:
            self.console.print("[yellow]⚠️  对比数据不足[/yellow]")
            return

        # 创建对比表格
        table = Table(title=f"重排序对比 - '{query}'")
        table.add_column("排名", style="cyan", width=6)
        table.add_column("文档ID", style="green", width=15)
        table.add_column("标题", style="white", width=25)
        table.add_column("相似度", style="magenta", width=10)
        table.add_column("Reranker", style="yellow", width=10)
        table.add_column("变化", style="red", width=8)

        # 创建排名映射
        before_ranks = {result.chunk_id: i for i, result in enumerate(before, 1)}

        # 添加数据行
        for i, reranked_result in enumerate(after[:self.config.max_results], 1):
            result = reranked_result.search_result
            before_rank = before_ranks.get(result.chunk_id, "-")

            # 计算排名变化
            if isinstance(before_rank, int):
                rank_change = before_rank - i
                if rank_change > 0:
                    change_text = f"↑{rank_change}"
                    change_style = "green"
                elif rank_change < 0:
                    change_text = f"↓{abs(rank_change)}"
                    change_style = "red"
                else:
                    change_text = "-"
                    change_style = "white"
            else:
                change_text = "新"
                change_style = "blue"

            table.add_row(
                str(i),
                result.chunk_id[:14] + "..." if len(result.chunk_id) > 14 else result.chunk_id,
                result.title[:23] + "..." if len(result.title) > 23 else result.title,
                f"{result.similarity_score:.3f}",
                f"{reranked_result.reranker_score:.3f}",
                change_text,
                style=change_style
            )

        self.console.print(table)

    def show_document_detail(self, document: SearchResult):
        """显示单个文档的详细信息"""
        # 创建详情面板
        detail_text = Text()
        detail_text.append("文档详情\n", style="bold cyan")
        detail_text.append(f"文档ID: {document.chunk_id}\n", style="green")
        detail_text.append(f"标题: {document.title}\n", style="white")
        detail_text.append(f"来源: {document.source_file}\n", style="dim")
        detail_text.append(f"相似度: {document.similarity_score:.3f}", style="magenta")

        if document.metadata.get("keyword_score"):
            detail_text.append(f" | 关键词分数: {document.metadata['keyword_score']:.3f}", style="yellow")

        # 显示元数据
        if document.metadata:
            detail_text.append("\n\n元数据:\n", style="bold")
            for key, value in document.metadata.items():
                if key not in ["similarity", "keyword_score"]:
                    detail_text.append(f"  {key}: {value}\n", style="dim")

        # 显示内容
        content = document.content
        if len(content) > 500:
            content = content[:500] + "..."

        detail_text.append("\n内容:\n", style="bold")
        detail_text.append(content, style="white")

        self.console.print(Panel(
            detail_text,
            title="文档详情",
            border_style="cyan",
            padding=(1, 2)
        ))

    def show_document_detail_by_index(self, index: int, results: List[SearchResult]):
        """根据索引显示文档详情"""
        if index < 0 or index >= len(results):
            self.console.print(f"[red]❌ 无效的文档索引: {index + 1}[/red]")
            return

        self.show_document_detail(results[index])

    def show_search_stats(self, stats):
        """显示检索统计信息"""
        if not stats:
            return

        stats_text = Text()
        stats_text.append("检索统计\n", style="bold cyan")
        stats_text.append(f"查询: {stats.query}\n", style="white")
        stats_text.append(f"总结果数: {stats.total_results}\n", style="green")
        stats_text.append(f"检索时间: {stats.search_time:.3f}s", style="magenta")

        if stats.reranker_time:
            stats_text.append(f" | 重排序时间: {stats.reranker_time:.3f}s", style="yellow")

        if stats.average_similarity:
            stats_text.append(f"\n平均相似度: {stats.average_similarity:.3f}", style="blue")

        self.console.print(Panel(
            stats_text,
            title="统计信息",
            border_style="blue",
            padding=(1, 2)
        ))