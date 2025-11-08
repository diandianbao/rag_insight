#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式命令行界面

提供类似REPL的交互体验，支持多种命令和操作
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.panel import Panel

from rag_cli.core import InteractiveSession
from rag_cli.models.config import SessionConfig


class InteractiveCLI:
    """交互式命令行界面"""

    def __init__(self, config: SessionConfig):
        self.config = config
        self.session = InteractiveSession(config)
        self.console = Console()
        self.running = False

        # 在初始化时连接数据库
        if not self.session.retriever.connect():
            self.console.print("[red]❌ 无法连接到数据库[/red]")
            sys.exit(1)

    def start(self):
        """启动交互式会话"""
        self.running = True
        self._show_welcome()

        while self.running:
            try:
                user_input = Prompt.ask(
                    "[bold cyan]>[/bold cyan]"
                ).strip()

                if not user_input:
                    continue

                self._process_command(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]⚠️  输入 Ctrl+D 退出程序[/yellow]")
            except EOFError:
                self.console.print("\n[green]👋 再见！[/green]")
                break
            except Exception as e:
                self.console.print(f"[red]❌ 命令执行错误: {e}[/red]")

    def _show_welcome(self):
        """显示欢迎信息"""
        welcome_text = Text()
        welcome_text.append("RAG 检索交互式命令行\n", style="bold cyan")
        welcome_text.append(f"版本: {__import__('rag_cli').__version__} | ", style="green")
        welcome_text.append("数据库: ", style="green")
        # 在初始化时已经连接过数据库，这里直接显示已连接
        welcome_text.append("已连接", style="green")
        welcome_text.append(" | Reranker: ", style="green")
        welcome_text.append("已启用" if self.config.reranker.enabled else "未启用",
                          style="green" if self.config.reranker.enabled else "yellow")
        welcome_text.append("\n输入 'help' 查看可用命令，'quit' 退出", style="dim")

        self.console.print(Panel(
            welcome_text,
            border_style="cyan",
            padding=(1, 2)
        ))

    def _process_command(self, command: str):
        """处理用户命令"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        command_handlers = {
            "search": self._handle_search,
            "rerank": self._handle_rerank,
            "history": self._handle_history,
            "detail": self._handle_detail,
            "config": self._handle_config,
            "set": self._handle_set,
            "export": self._handle_export,
            "clear": self._handle_clear,
            "help": self._handle_help,
            "quit": self._handle_quit,
            "exit": self._handle_quit,
        }

        handler = command_handlers.get(cmd)
        if handler:
            handler(args)
        else:
            # 如果没有匹配的命令，当作查询处理
            self._handle_search(command)

    def _handle_search(self, query: str):
        """处理搜索命令"""
        if not query:
            self.console.print("[yellow]⚠️  请输入查询内容[/yellow]")
            return

        self.console.print(f"[dim]执行查询: {query}[/dim]")
        success = self.session.process_query(query)

        if success:
            self.console.print(f"[green]✓ 查询完成[/green]")
        else:
            self.console.print(f"[red]❌ 查询失败[/red]")

    def _handle_rerank(self, query: str):
        """处理重排序搜索命令"""
        if not query:
            self.console.print("[yellow]⚠️  请输入查询内容[/yellow]")
            return

        # 临时启用重排序
        original_enabled = self.config.reranker.enabled
        self.config.reranker.enabled = True

        try:
            self.console.print(f"[dim]执行重排序查询: {query}[/dim]")
            success = self.session.process_query(query)

            if success:
                self.console.print(f"[green]✓ 重排序查询完成[/green]")
            else:
                self.console.print(f"[red]❌ 重排序查询失败[/red]")
        finally:
            # 恢复原始设置
            self.config.reranker.enabled = original_enabled

    def _handle_history(self, args: str):
        """处理历史命令"""
        self.session.show_history()

    def _handle_detail(self, args: str):
        """处理详情命令"""
        if not args:
            self.console.print("[yellow]⚠️  请输入文档ID或序号[/yellow]")
            return

        try:
            # 尝试解析为序号
            index = int(args) - 1
            if self.session.current_results:
                self.session.display.show_document_detail_by_index(index, self.session.current_results)
            else:
                self.console.print("[yellow]⚠️  请先执行搜索以获取结果[/yellow]")
        except (ValueError, IndexError):
            # 当作文档ID处理
            self.console.print("[yellow]⚠️  文档ID功能暂未实现，请使用序号[/yellow]")

    def _handle_config(self, args: str):
        """处理配置命令"""
        from rich.table import Table

        table = Table(title="当前配置", show_header=True, header_style="bold magenta")
        table.add_column("配置项", style="cyan", width=20)
        table.add_column("值", style="white")

        # 向量存储配置
        table.add_row("数据库URL", self.config.retriever_config.vector_store_config.database_url)
        table.add_row("表名", self.config.retriever_config.vector_store_config.table_name)
        table.add_row("Embedding模型", self.config.retriever_config.vector_store_config.embedding_model)

        # 重排序配置
        table.add_row("Reranker启用", "是" if self.config.reranker.enabled else "否")
        table.add_row("Reranker端点", self.config.reranker.endpoint)

        # 显示配置
        table.add_row("主题", self.config.display.theme)
        table.add_row("最大结果数", str(self.config.display.max_results))

        self.console.print(table)

    def _handle_set(self, args: str):
        """处理设置命令"""
        if not args:
            self.console.print("[yellow]⚠️  使用方法: set <key> <value>[/yellow]")
            return

        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]⚠️  使用方法: set <key> <value>[/yellow]")
            return

        key = parts[0]
        value = parts[1]

        # 这里可以实现配置的动态修改
        self.console.print(f"[yellow]⚠️  配置修改功能暂未实现[/yellow]")

    def _handle_export(self, args: str):
        """处理导出命令"""
        format = args.strip().lower() or "json"
        if format not in ["json", "markdown", "csv"]:
            self.console.print(f"[red]❌ 不支持的导出格式: {format}[/red]")
            return

        self.session.export_results(format)

    def _handle_clear(self, args: str):
        """处理清屏命令"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def _handle_help(self, args: str):
        """处理帮助命令"""
        help_text = """
[bold]可用命令:[/bold]

  [cyan]search <query>[/cyan]      - 执行检索
  [cyan]rerank <query>[/cyan]      - 检索并重排序
  [cyan]history[/cyan]             - 显示查询历史
  [cyan]detail <id/序号>[/cyan]    - 查看文档详情
  [cyan]config[/cyan]              - 显示当前配置
  [cyan]set <key> <value>[/cyan]   - 修改配置
  [cyan]export <format>[/cyan]     - 导出结果 (json/markdown/csv)
  [cyan]clear[/cyan]               - 清空屏幕
  [cyan]help[/cyan]                - 显示帮助
  [cyan]quit[/cyan]                - 退出程序

[bold]快捷方式:[/bold]
  直接输入查询内容即可执行搜索
        """
        self.console.print(Panel(
            help_text.strip(),
            title="帮助",
            border_style="blue",
            padding=(1, 2)
        ))

    def _handle_quit(self, args: str):
        """处理退出命令"""
        if Confirm.ask("确定要退出吗?"):
            self.console.print("[green]👋 再见！[/green]")
            self.running = False


def main():
    """交互式CLI主函数"""
    try:
        from rag_cli.main import load_config
        config = load_config()
        cli = InteractiveCLI(config)
        cli.start()
    except Exception as e:
        console = Console()
        console.print(f"[red]❌ 启动交互式CLI失败: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()