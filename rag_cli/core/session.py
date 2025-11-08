"""
交互会话管理
管理交互式会话的状态和历史
"""

import time
from typing import List, Optional
from datetime import datetime

from rag_cli.models.config import SessionConfig
from rag_cli.models.results import SearchResult, RerankedResult, QueryHistory, SearchStats
from rag_cli.core.retriever import RAGRetriever
from rag_cli.core.reranker import Reranker
from rag_cli.core.display import ResultDisplay


class InteractiveSession:
    """交互会话管理器"""

    def __init__(self, config: SessionConfig):
        self.config = config
        self.retriever = RAGRetriever(config.retriever_config)
        self.reranker = Reranker(config.reranker)
        self.display = ResultDisplay(config.display)
        self.history: List[QueryHistory] = []
        self.current_results: Optional[List[SearchResult]] = None

    def connect(self):
        """连接数据库"""
        if not self.retriever.connect():
            self.display.console.print("[red]❌ 无法连接到数据库[/red]")
            return False

        self.display.console.print("[green]✓ 数据库连接成功[/green]")
        return True

    def process_query(self, query: str) -> bool:
        """处理单个查询"""
        start_time = time.time()

        try:
            # 执行检索
            results = self.retriever.search(query, self.config.search.default_top_k)

            search_time = time.time() - start_time

            # 执行重排序（如果启用）
            reranker_time = None
            if self.config.reranker.enabled and results:
                rerank_start = time.time()
                reranked_results = self.reranker.rerank(query, results)
                reranker_time = time.time() - rerank_start

                # 显示对比结果
                self.display.show_comparison(results, reranked_results, query)
                self.current_results = [r.search_result for r in reranked_results]
            else:
                # 显示普通结果
                self.display.show_search_results(results, query)
                self.current_results = results

            # 显示统计信息
            stats = self.retriever.get_search_stats(query, results, search_time, reranker_time)
            self.display.show_search_stats(stats)

            # 记录历史
            if self.config.interactive.enable_history:
                self._add_to_history(query, results, search_time)

            return True

        except Exception as e:
            self.display.console.print(f"[red]❌ 查询处理失败: {e}[/red]")
            return False

    def show_history(self):
        """显示查询历史"""
        if not self.history:
            self.display.console.print("[yellow]⚠️  暂无查询历史[/yellow]")
            return

        from rich.table import Table

        table = Table(title="查询历史")
        table.add_column("序号", style="cyan", width=6)
        table.add_column("查询内容", style="white", width=30)
        table.add_column("时间", style="green", width=20)
        table.add_column("结果数", style="magenta", width=8)

        for i, history in enumerate(self.history[-self.config.interactive.max_history_size:], 1):
            table.add_row(
                str(i),
                history.query[:28] + "..." if len(history.query) > 28 else history.query,
                history.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                str(history.result_count)
            )

        self.display.console.print(table)

    def clear_history(self):
        """清空查询历史"""
        self.history.clear()
        self.display.console.print("[green]✓ 查询历史已清空[/green]")

    def export_results(self, format: str = "json"):
        """导出当前结果"""
        if not self.current_results:
            self.display.console.print("[yellow]⚠️  没有可导出的结果[/yellow]")
            return

        try:
            if format == "json":
                self._export_json()
            elif format == "markdown":
                self._export_markdown()
            elif format == "csv":
                self._export_csv()
            else:
                self.display.console.print(f"[red]❌ 不支持的导出格式: {format}[/red]")

        except Exception as e:
            self.display.console.print(f"[red]❌ 导出失败: {e}[/red]")

    def _add_to_history(self, query: str, results: List[SearchResult], search_time: float):
        """添加查询到历史记录"""
        history = QueryHistory(
            query=query,
            timestamp=datetime.now(),
            result_count=len(results),
            search_mode="vector",
            reranker_enabled=self.config.reranker.enabled,
            search_time=search_time,
            results=results
        )

        self.history.append(history)

        # 限制历史记录大小
        if len(self.history) > self.config.interactive.max_history_size:
            self.history = self.history[-self.config.interactive.max_history_size:]

    def _export_json(self):
        """导出为JSON格式"""
        import json

        export_data = {
            "export_time": datetime.now().isoformat(),
            "total_results": len(self.current_results),
            "results": [result.to_dict() for result in self.current_results]
        }

        filename = f"rag_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.display.console.print(f"[green]✓ 结果已导出到: {filename}[/green]")

    def _export_markdown(self):
        """导出为Markdown格式"""
        filename = f"rag_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# RAG 检索结果\n\n")
            f.write(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**总结果数**: {len(self.current_results)}\n\n")

            for i, result in enumerate(self.current_results, 1):
                f.write(f"## {i}. {result.title}\n\n")
                f.write(f"**文档ID**: {result.chunk_id}\n")
                f.write(f"**相似度**: {result.similarity_score:.3f}\n")
                f.write(f"**来源**: {result.source_file}\n\n")
                f.write(f"**内容**:\n\n{result.content}\n\n")
                f.write("---\n\n")

        self.display.console.print(f"[green]✓ 结果已导出到: {filename}[/green]")

    def _export_csv(self):
        """导出为CSV格式"""
        import csv

        filename = f"rag_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['排名', '文档ID', '标题', '相似度', '来源', '内容预览'])

            for i, result in enumerate(self.current_results, 1):
                content_preview = result.content[:100] + "..." if len(result.content) > 100 else result.content
                writer.writerow([
                    i,
                    result.chunk_id,
                    result.title,
                    f"{result.similarity_score:.3f}",
                    result.source_file,
                    content_preview
                ])

        self.display.console.print(f"[green]✓ 结果已导出到: {filename}[/green]")

    def cleanup(self):
        """清理资源"""
        self.retriever.disconnect()