from random import shuffle
from rich.console import Console
from rich.table import Table
from rich import box
from utilities_module import clear_screen, delay_and_clear_screen, prompt_delay

console = Console()
keys: dict[int, int] = {}


def generate_key() -> dict[str, str]:
    """Generates a random key for the monoalphabetic cipher."""
    key = [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)]
    shuffle(key)
    generated_key = {chr(small_letter): key.pop(0) for small_letter in range(97, 123)}
    generated_key.update(
        {chr(capital_letter): key.pop(0) for capital_letter in range(65, 91)}
    )
    keys[str(len(keys) + 1)] = generated_key
    console.print(f"Key {len(keys)} generated successfully!", style="bold green")
    prompt_delay()
    clear_screen()
    return generated_key


def show_all_keys() -> None:
    """Displays all the keys in the keys dictionary."""
    key_table = Table(title="Available Keys", style="bold magenta")
    key_table.box = box.ASCII2
    key_table.add_column("Key Number", style="bold blue", justify="center")

    for key_number, key in keys.items():
        key_table.add_row(key_number)
    console.print(key_table)


def select_key(key_number: str) -> str | None:
    """Selects a key from the keys dictionary."""
    if key_number not in keys:
        console.print(
            "Key not found! Please enter a valid key number.", style="bold red"
        )
        delay_and_clear_screen()
        return None
    else:
        return key_number, keys[key_number]
