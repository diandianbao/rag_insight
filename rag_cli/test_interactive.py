#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试交互式功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.prompt import Prompt

console = Console()

console.print("[bold cyan]简单交互测试[/bold cyan]")

try:
    while True:
        user_input = Prompt.ask(
            "[bold cyan]>[/bold cyan]"
        ).strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            console.print("[green]👋 再见！[/green]")
            break

        console.print(f"你输入了: {user_input}")

except KeyboardInterrupt:
    console.print("\n[yellow]⚠️  输入 Ctrl+D 退出程序[/yellow]")
except EOFError:
    console.print("\n[green]👋 再见！[/green]")
except Exception as e:
    console.print(f"[red]❌ 错误: {e}[/red]")