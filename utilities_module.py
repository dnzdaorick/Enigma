import os
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
import random

console = Console()


def delay_and_clear_screen():
    """Delays the screen and then clears it."""
    delay_screen()
    clear_screen()


def clear_screen():
    """Clears the screen."""
    os.system("cls" if os.name == "nt" else "clear")


def delay_screen():
    """Delays the screen for 1.5 seconds."""
    time.sleep(1.5)


def progress_bar():
    """Displays a progress bar."""
    loading_message = "Loading"
    loading_spinner = SpinnerColumn(style="bright_green")
    loading_bar = BarColumn(bar_width=30)
    percentage_text = TextColumn(
        "[progress.percentage] [bright_cyan]{task.percentage:>3.0f}% [bright_cyan]{task.elapsed:.1f}s"
    )

    loading_progress = Progress(
        f"[green] {loading_message}",
        loading_spinner,
        loading_bar,
        percentage_text,
    )

    task_id = loading_progress.add_task("Task", total=8)

    with loading_progress:
        while not loading_progress.finished:
            time.sleep(0.1)
            loading_progress.update(task_id, advance=1)


def prompt_delay():
    """Prompts the user to press any key to exit."""
    input_key = Prompt.ask("\nPress any key to exit")


def color_randomizer() -> str:
    """Randomizes the color for the text."""
    available_colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]
    return random.choice(available_colors)
