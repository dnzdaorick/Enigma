import json
import os
from datetime import datetime
from random import shuffle
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from utilities_module import clear_screen, delay_screen, delay_and_clear_screen, prompt_delay

console = Console()
KEYS_FILE = "keys.json"

# In-memory storage of key mappings and their metadata
keys: dict[str, dict[str, str]] = {}
keys_metadata: dict[str, dict[str, str]] = {}


def load_keys() -> None:
    """Loads keys and metadata from keys.json if available."""
    global keys, keys_metadata
    if not os.path.exists(KEYS_FILE):
        return

    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        keys.clear()
        keys_metadata.clear()

        for key_id, info in data.items():
            if isinstance(info, dict) and "mapping" in info:
                keys[str(key_id)] = info["mapping"]
                keys_metadata[str(key_id)] = {
                    "created_at": info.get("created_at", "Unknown"),
                }
            elif isinstance(info, dict):
                # Legacy raw mapping fallback
                keys[str(key_id)] = info
                keys_metadata[str(key_id)] = {"created_at": "Earlier session"}
    except Exception as e:
        console.print(f"[bold red]Warning: Failed to load keys from {KEYS_FILE}: {e}[/bold red]")


def save_keys() -> None:
    """Persists all current keys and metadata to keys.json."""
    data = {}
    for key_id, mapping in keys.items():
        data[key_id] = {
            "created_at": keys_metadata.get(key_id, {}).get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "mapping": mapping,
        }
    try:
        with open(KEYS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        console.print(f"[bold red]Error saving keys: {e}[/bold red]")


def generate_key(interactive: bool = True) -> dict[str, str]:
    """Generates a random 52-character substitution key and persists it to keys.json."""
    letters = [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)]
    shuffled_letters = letters.copy()
    shuffle(shuffled_letters)

    generated_key = {
        orig: subst for orig, subst in zip(letters, shuffled_letters)
    }

    # Determine next available integer key ID
    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_id = str(max(existing_numeric_ids) + 1 if existing_numeric_ids else 1)

    keys[next_id] = generated_key
    keys_metadata[next_id] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_keys()
    if interactive:
        console.print(f"[bold green]Key {next_id} generated and saved to {KEYS_FILE} successfully![/bold green]")
        prompt_delay()
        clear_screen()
    return generated_key


def show_all_keys() -> None:
    """Displays all available keys in a formatted Rich Table."""
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No keys available.[/bold yellow]\n"
                "Please generate a key first using option [bold cyan][C][/bold cyan] in the main menu.",
                title="Key Store Status",
                border_style="yellow",
            )
        )
        return

    key_table = Table(title="Available Substitution Keys", style="bold magenta", box=box.ROUNDED)
    key_table.add_column("Key #", style="bold cyan", justify="center", width=8)
    key_table.add_column("Created At", style="green", justify="center")
    key_table.add_column("Sample Mapping (a-f)", style="yellow", justify="left")
    key_table.add_column("Total Characters", style="blue", justify="center")

    for key_number, mapping in sorted(keys.items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
        created_time = keys_metadata.get(key_number, {}).get("created_at", "N/A")
        sample_chars = ["a", "b", "c", "d", "e", "f"]
        sample_str = ", ".join(f"{c}→{mapping.get(c, '?')}" for c in sample_chars)
        key_table.add_row(key_number, created_time, sample_str, str(len(mapping)))

    console.print(key_table)


def inspect_key(key_number: str) -> None:
    """Displays the complete 52-character mapping for a specific key."""
    if key_number not in keys:
        console.print(f"[bold red]Key #{key_number} not found![/bold red]")
        prompt_delay()
        return

    mapping = keys[key_number]
    created = keys_metadata.get(key_number, {}).get("created_at", "N/A")

    table = Table(
        title=f"Detailed Mapping for Key #{key_number} (Created: {created})",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold cyan",
    )
    table.add_column("Lower", justify="center", style="green")
    table.add_column("→", justify="center", style="dim")
    table.add_column("Mapped", justify="center", style="yellow")
    table.add_column("|", justify="center", style="dim")
    table.add_column("Upper", justify="center", style="cyan")
    table.add_column("→", justify="center", style="dim")
    table.add_column("Mapped", justify="center", style="magenta")

    for i in range(26):
        lower_char = chr(97 + i)
        upper_char = chr(65 + i)
        table.add_row(
            lower_char,
            "→",
            mapping.get(lower_char, "?"),
            "|",
            upper_char,
            "→",
            mapping.get(upper_char, "?"),
        )

    clear_screen()
    console.print(table)
    prompt_delay()
    clear_screen()


def select_key(key_number: str) -> tuple[str, dict[str, str]] | None:
    """Selects a key from the keys dictionary. Returns (key_number, key_mapping) or None."""
    if key_number not in keys:
        console.print(
            "[bold red]Key not found! Please enter a valid key number.[/bold red]"
        )
        delay_screen(1.0)
        return None
    return key_number, keys[key_number]


def delete_key(key_number: str) -> bool:
    """Deletes a key from the store and updates keys.json."""
    if key_number in keys:
        del keys[key_number]
        keys_metadata.pop(key_number, None)
        save_keys()
        return True
    return False


# Automatically load keys upon module import
load_keys()
