import os
import sys
import time
import random
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Ensure UTF-8 output encoding for terminals across platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console()


def clear_screen() -> None:
    """Clears the terminal screen across Windows and Unix platforms."""
    os.system("cls" if os.name == "nt" else "clear")


def delay_screen(seconds: float = 1.0) -> None:
    """Delays execution for a specified duration in seconds."""
    time.sleep(seconds)


def delay_and_clear_screen(seconds: float = 1.0) -> None:
    """Delays for a brief moment and then clears the terminal screen."""
    delay_screen(seconds)
    clear_screen()


def progress_bar(message: str = "Processing", total: int = 5, step_delay: float = 0.04) -> None:
    """Displays an animated progress bar with a customizable task description and speed."""
    loading_spinner = SpinnerColumn(style="bright_green")
    loading_bar = BarColumn(bar_width=30)
    percentage_text = TextColumn(
        "[progress.percentage] [bright_cyan]{task.percentage:>3.0f}% [bright_cyan]{task.elapsed:.1f}s"
    )

    loading_progress = Progress(
        f"[green]{message}",
        loading_spinner,
        loading_bar,
        percentage_text,
        console=console,
        transient=True,
    )

    task_id = loading_progress.add_task(message, total=total)

    with loading_progress:
        while not loading_progress.finished:
            time.sleep(step_delay)
            loading_progress.update(task_id, advance=1)


def prompt_delay(message: str = "\nPress Enter to continue...") -> None:
    """Prompts the user to press Enter before proceeding."""
    Prompt.ask(message, default="", show_default=False)


def display_header(title: str, subtitle: str = "") -> None:
    """Displays a stylized banner header."""
    clear_screen()
    content = f"[bold cyan]{title.upper()}[/bold cyan]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    console.print(
        Panel(content, border_style="bright_blue", expand=False, padding=(0, 3)),
        justify="center",
    )
    console.print()


def color_randomizer() -> str:
    """Returns a random bright color name."""
    available_colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]
    return random.choice(available_colors)
