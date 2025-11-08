#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 检索命令行工具主入口

支持单次检索和交互式会话两种模式
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from rag_cli.core import InteractiveSession
from rag_cli.models.config import SessionConfig
from rag_cli.utils.validation import validate_config

# 创建Typer应用
app = typer.Typer(
    name="rag-cli",
    help="RAG 检索命令行工具",
    rich_markup_mode="rich"
)

console = Console()


def load_config() -> SessionConfig:
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        console.print(f"[red]❌ 配置文件不存在: {config_path}[/red]")
        sys.exit(1)

    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # 验证配置
        validate_config(config_data)

        # 转换为SessionConfig对象
        return SessionConfig.from_dict(config_data)

    except Exception as e:
        console.print(f"[red]❌ 配置文件加载失败: {e}[/red]")
        sys.exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="查询内容"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="返回结果数量"),
    rerank: bool = typer.Option(False, "--rerank", "-r", help="启用重排序"),
    mode: str = typer.Option("vector", "--mode", "-m", help="检索模式: vector/hybrid"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息")
):
    """
    执行单次检索

    Examples:

    rag-cli search "Python异步编程"

    rag-cli search "机器学习算法" --top-k 20 --rerank

    rag-cli search "数据库优化" --mode hybrid --verbose
    """
    try:
        config = load_config()
        session = InteractiveSession(config)

        # 连接数据库
        if not session.connect():
            console.print("[red]❌ 无法连接到数据库[/red]")
            sys.exit(1)

        # 设置检索参数
        session.config.search.default_top_k = top_k
        session.config.reranker.enabled = rerank

        # 执行查询
        success = session.process_query(query)

        # 清理资源
        session.cleanup()

        if not success:
            console.print("[red]❌ 检索失败[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ 检索过程中发生错误: {e}[/red]")
        sys.exit(1)


@app.command()
def interactive():
    """
    启动交互式会话

    进入交互模式后，可以连续执行多个查询，
    查看历史记录，修改配置等。
    """
    try:
        config = load_config()
        session = InteractiveSession(config)

        # 连接数据库
        if not session.connect():
            console.print("[red]❌ 无法启动交互式会话[/red]")
            sys.exit(1)

        # 显示欢迎信息
        welcome_text = Text()
        welcome_text.append("RAG 检索交互式命令行\n", style="bold cyan")
        welcome_text.append(f"版本: {__import__('rag_cli').__version__} | ", style="green")
        welcome_text.append("数据库: ", style="green")
        welcome_text.append("已连接", style="green")
        welcome_text.append(" | Reranker: ", style="green")
        welcome_text.append("已启用" if config.reranker.enabled else "未启用",
                          style="green" if config.reranker.enabled else "yellow")
        welcome_text.append("\n输入 'help' 查看可用命令，'quit' 退出", style="dim")

        console.print(Panel(
            welcome_text,
            border_style="cyan",
            padding=(1, 2)
        ))

        # 启动交互循环
        running = True
        while running:
            try:
                user_input = input("> ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[green]👋 再见！[/green]")
                    break
                elif user_input.lower() == 'help':
                    console.print("""
[bold]可用命令:[/bold]

  [cyan]search <query>[/cyan]      - 执行检索
  [cyan]rerank <query>[/cyan]      - 检索并重排序
  [cyan]history[/cyan]             - 显示查询历史
  [cyan]detail <id/序号>[/cyan]    - 查看文档详情
  [cyan]config[/cyan]              - 显示当前配置
  [cyan]export <format>[/cyan]     - 导出结果 (json/markdown/csv)
  [cyan]clear[/cyan]               - 清空屏幕
  [cyan]help[/cyan]                - 显示帮助
  [cyan]quit[/cyan]                - 退出程序

[bold]快捷方式:[/bold]
  直接输入查询内容即可执行搜索
                    """)
                elif user_input.lower() == 'history':
                    session.show_history()
                elif user_input.lower().startswith('detail'):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) > 1:
                        try:
                            index = int(parts[1]) - 1
                            if session.current_results:
                                session.display.show_document_detail_by_index(index, session.current_results)
                            else:
                                console.print("[yellow]⚠️  请先执行搜索以获取结果[/yellow]")
                        except (ValueError, IndexError):
                            console.print("[yellow]⚠️  请提供有效的文档序号[/yellow]")
                    else:
                        console.print("[yellow]⚠️  使用方法: detail <序号>[/yellow]")
                elif user_input.lower() == 'config':
                    from rich.table import Table
                    table = Table(title="当前配置", show_header=True, header_style="bold magenta")
                    table.add_column("配置项", style="cyan", width=20)
                    table.add_column("值", style="white")
                    table.add_row("数据库URL", config.retriever_config.vector_store_config.database_url)
                    table.add_row("表名", config.retriever_config.vector_store_config.table_name)
                    table.add_row("Embedding模型", config.retriever_config.vector_store_config.embedding_model)
                    table.add_row("Reranker启用", "是" if config.reranker.enabled else "否")
                    table.add_row("Reranker端点", config.reranker.endpoint)
                    table.add_row("主题", config.display.theme)
                    table.add_row("最大结果数", str(config.display.max_results))
                    console.print(table)
                else:
                    # 当作查询处理
                    success = session.process_query(user_input)
                    if success:
                        console.print(f"[green]✓ 查询完成[/green]")
                    else:
                        console.print(f"[red]❌ 查询失败[/red]")

            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️  输入 Ctrl+D 退出程序[/yellow]")
            except EOFError:
                console.print("\n[green]👋 再见！[/green]")
                break
            except Exception as e:
                console.print(f"[red]❌ 命令执行错误: {e}[/red]")

        # 清理资源
        session.cleanup()

    except Exception as e:
        console.print(f"[red]❌ 启动交互式会话失败: {e}[/red]")
        sys.exit(1)


@app.command()
def config():
    """显示当前配置"""
    try:
        config = load_config()

        from rich.table import Table

        table = Table(title="当前配置", show_header=True, header_style="bold magenta")
        table.add_column("配置项", style="cyan", width=20)
        table.add_column("值", style="white")

        # 向量存储配置
        table.add_row("数据库URL", config.retriever_config.vector_store_config.database_url)
        table.add_row("表名", config.retriever_config.vector_store_config.table_name)
        table.add_row("Embedding模型", config.retriever_config.vector_store_config.embedding_model)

        # 重排序配置
        table.add_row("Reranker启用", "是" if config.reranker.enabled else "否")
        table.add_row("Reranker端点", config.reranker.endpoint)

        # 显示配置
        table.add_row("主题", config.display.theme)
        table.add_row("最大结果数", str(config.display.max_results))

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ 显示配置失败: {e}[/red]")
        sys.exit(1)


@app.command()
def version():
    """显示版本信息"""
    console.print(f"[bold cyan]RAG CLI[/bold cyan] 版本: {__import__('rag_cli').__version__}")


if __name__ == "__main__":
    app()