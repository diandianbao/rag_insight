"""
交互式提示工具
"""

from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.text import Text


console = Console()


def get_query_prompt() -> str:
    """
    获取查询输入提示

    Returns:
        用户输入的查询文本
    """
    return Prompt.ask(
        "[bold cyan]请输入查询内容[/bold cyan]",
        default=""
    ).strip()


def get_command_prompt() -> str:
    """
    获取命令输入提示

    Returns:
        用户输入的命令
    """
    return Prompt.ask(
        "[bold cyan]>[/bold cyan]",
        default=""
    ).strip()


def get_choice_prompt(question: str, choices: list, default: str = None) -> str:
    """
    获取选择提示

    Args:
        question: 问题文本
        choices: 选项列表
        default: 默认选项

    Returns:
        用户选择的选项
    """
    return Prompt.ask(
        f"[bold cyan]{question}[/bold cyan]",
        choices=choices,
        default=default
    )


def confirm_action(message: str) -> bool:
    """
    确认操作

    Args:
        message: 确认消息

    Returns:
        用户是否确认
    """
    return Confirm.ask(f"[yellow]{message}[/yellow]")


def get_number_prompt(message: str, min_value: int = 1, max_value: int = 100) -> int:
    """
    获取数字输入提示

    Args:
        message: 提示消息
        min_value: 最小值
        max_value: 最大值

    Returns:
        用户输入的数字
    """
    while True:
        try:
            value = Prompt.ask(f"[bold cyan]{message}[/bold cyan]")
            number = int(value)
            if min_value <= number <= max_value:
                return number
            else:
                console.print(f"[red]❌ 请输入 {min_value}-{max_value} 之间的数字[/red]")
        except ValueError:
            console.print("[red]❌ 请输入有效的数字[/red]")


def get_multiline_input(prompt: str) -> str:
    """
    获取多行输入

    Args:
        prompt: 提示消息

    Returns:
        用户输入的多行文本
    """
    console.print(f"[bold cyan]{prompt}[/bold cyan]")
    console.print("[dim]输入空行结束输入[/dim]")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    return "\n".join(lines)