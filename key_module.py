"""Key module for Image Key Cipher.

Manages image-derived cryptographic keys, image code fingerprints, and persistence.
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from utilities_module import clear_screen, delay_screen, prompt_delay
from image_key_cipher import (
    read_image_bytes,
    image_to_code,
    generate_key_from_image,
    create_sample_bmp_image,
    ALPHABET_LOWER,
    ALPHABET_UPPER,
    NUMBERS,
    SYMBOLS,
    FULL_CHARSET,
)

console = Console()
KEYS_FILE = "keys.json"
KEYS_DIR = "key_images"

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
                    "image_path": info.get("image_path", "Generated/Custom Image"),
                    "image_code": info.get("image_code", "N/A"),
                    "byte_size": str(info.get("byte_size", "N/A")),
                }
            elif isinstance(info, dict):
                # Legacy raw mapping fallback
                keys[str(key_id)] = info
                keys_metadata[str(key_id)] = {
                    "created_at": "Earlier session",
                    "image_path": "Legacy Key",
                    "image_code": "N/A",
                    "byte_size": "N/A",
                }
    except Exception as e:
        console.print(f"[bold red]Warning: Failed to load keys from {KEYS_FILE}: {e}[/bold red]")


def save_keys() -> None:
    """Persists all current keys and metadata to keys.json."""
    data = {}
    for key_id, mapping in keys.items():
        meta = keys_metadata.get(key_id, {})
        data[key_id] = {
            "created_at": meta.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "image_path": meta.get("image_path", "N/A"),
            "image_code": meta.get("image_code", "N/A"),
            "byte_size": meta.get("byte_size", "N/A"),
            "mapping": mapping,
        }
    try:
        with open(KEYS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        console.print(f"[bold red]Error saving keys: {e}[/bold red]")


def register_image_file(image_path: str, interactive: bool = True) -> tuple[str, dict[str, str]] | None:
    """Converts an image file into cryptographic code, derives a substitution key, and registers it."""
    image_path = os.path.normpath(image_path.strip().strip('"').strip("'"))
    if not os.path.exists(image_path):
        if interactive:
            console.print(f"[bold red]Error: Image file '{image_path}' not found![/bold red]")
            prompt_delay()
        return None

    try:
        img_bytes = read_image_bytes(image_path)
    except Exception as e:
        if interactive:
            console.print(f"[bold red]Error reading image file: {e}[/bold red]")
            prompt_delay()
        return None

    subst_key, _, code_info = generate_key_from_image(img_bytes)

    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_id = str(max(existing_numeric_ids) + 1 if existing_numeric_ids else 1)

    keys[next_id] = subst_key
    keys_metadata[next_id] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_path": image_path,
        "image_code": code_info["sha256"],
        "byte_size": code_info["byte_size"],
    }

    save_keys()

    if interactive:
        panel_content = (
            f"[bold green]Image Key successfully created and registered![/bold green]\n\n"
            f"[cyan]Key ID:[/cyan] [bold white]#{next_id}[/bold white]\n"
            f"[cyan]Source Image:[/cyan] {image_path}\n"
            f"[cyan]File Size:[/cyan] {code_info['byte_size']} bytes\n"
            f"[cyan]Image Code (SHA-256):[/cyan] [dim]{code_info['sha256']}[/dim]\n"
            f"[cyan]Short Fingerprint:[/cyan] [bold yellow]{code_info['short_code']}[/bold yellow]\n"
            f"[cyan]Substituted Characters:[/cyan] 95 (Alphabet: 52, Numbers: 10, Symbols: 33)"
        )
        console.print(Panel(panel_content, title="Image Key Registered", border_style="green"))
        prompt_delay()
        clear_screen()

    return next_id, subst_key


def generate_key(interactive: bool = True) -> dict[str, str]:
    """Generates a sample cryptographic key image (.bmp) and registers it."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_num = max(existing_numeric_ids) + 1 if existing_numeric_ids else 1
    image_filename = f"key_image_{next_num}.bmp"
    image_path = os.path.join(KEYS_DIR, image_filename)

    create_sample_bmp_image(image_path, width=128, height=128)
    res = register_image_file(image_path, interactive=interactive)
    if res is not None:
        return res[1]
    return {}


def show_all_keys() -> None:
    """Displays all available image keys in a formatted Rich Table."""
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No image keys available.[/bold yellow]\n"
                "Please generate a key image or load an image file first using option [bold cyan][C][/bold cyan].",
                title="Key Store Status",
                border_style="yellow",
            )
        )
        return

    key_table = Table(title="Available Image Substitution Keys", style="bold magenta", box=box.ROUNDED)
    key_table.add_column("Key #", style="bold cyan", justify="center", width=8)
    key_table.add_column("Image File", style="green", justify="left")
    key_table.add_column("Image Code (SHA-256)", style="yellow", justify="left")
    key_table.add_column("Size", style="cyan", justify="center")
    key_table.add_column("Created At", style="dim", justify="center")
    key_table.add_column("Mapped", style="blue", justify="center")

    for key_number, mapping in sorted(keys.items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
        meta = keys_metadata.get(key_number, {})
        created_time = meta.get("created_at", "N/A")
        img_path = os.path.basename(meta.get("image_path", "N/A"))
        img_code = meta.get("image_code", "N/A")
        short_code = img_code[:16] + "..." if len(img_code) > 16 else img_code
        file_size = meta.get("byte_size", "N/A")
        if file_size != "N/A":
            file_size += " B"

        key_table.add_row(
            key_number,
            img_path,
            short_code,
            file_size,
            created_time,
            f"{len(mapping)} chars",
        )

    console.print(key_table)


def inspect_key(key_number: str) -> None:
    """Displays the image code metadata and comprehensive character substitution mapping."""
    if key_number not in keys:
        console.print(f"[bold red]Key #{key_number} not found![/bold red]")
        prompt_delay()
        return

    mapping = keys[key_number]
    meta = keys_metadata.get(key_number, {})

    clear_screen()
    # Metadata Overview
    meta_panel = (
        f"[cyan]Key Number:[/cyan] [bold white]#{key_number}[/bold white]\n"
        f"[cyan]Image Source:[/cyan] {meta.get('image_path', 'N/A')}\n"
        f"[cyan]File Size:[/cyan] {meta.get('byte_size', 'N/A')} bytes\n"
        f"[cyan]Created:[/cyan] {meta.get('created_at', 'N/A')}\n"
        f"[cyan]Full Image Code (SHA-256):[/cyan]\n[bold yellow]{meta.get('image_code', 'N/A')}[/bold yellow]\n"
        f"[dim]Total Substituted Characters: {len(mapping)} (Alphabet, Numbers, Symbols & Space)[/dim]"
    )
    console.print(Panel(meta_panel, title=f"Image Key #{key_number} Details", border_style="bright_blue"))

    # Table for Letters
    letters_table = Table(title="Alphabet Substitution (a-z, A-Z)", box=box.SIMPLE_HEAD, header_style="bold cyan")
    letters_table.add_column("Lower", justify="center", style="green")
    letters_table.add_column("→", justify="center", style="dim")
    letters_table.add_column("Mapped", justify="center", style="yellow")
    letters_table.add_column("|", justify="center", style="dim")
    letters_table.add_column("Upper", justify="center", style="cyan")
    letters_table.add_column("→", justify="center", style="dim")
    letters_table.add_column("Mapped", justify="center", style="magenta")

    for i in range(26):
        low = ALPHABET_LOWER[i]
        upp = ALPHABET_UPPER[i]
        letters_table.add_row(low, "→", mapping.get(low, "?"), "|", upp, "→", mapping.get(upp, "?"))

    console.print(letters_table)

    # Table for Numbers & Symbols
    num_sym_table = Table(title="Numbers (0-9) & Symbols Mapping", box=box.SIMPLE_HEAD, header_style="bold cyan")
    num_sym_table.add_column("Number", justify="center", style="cyan")
    num_sym_table.add_column("→", justify="center", style="dim")
    num_sym_table.add_column("Mapped", justify="center", style="yellow")
    num_sym_table.add_column("|", justify="center", style="dim")
    num_sym_table.add_column("Symbol", justify="center", style="magenta")
    num_sym_table.add_column("→", justify="center", style="dim")
    num_sym_table.add_column("Mapped", justify="center", style="green")

    # Symbols include space as well
    sample_symbols = list(SYMBOLS)
    for i in range(10):
        digit = NUMBERS[i]
        sym = sample_symbols[i] if i < len(sample_symbols) else ""
        sym_disp = "' '" if sym == " " else sym
        mapped_sym = mapping.get(sym, "?")
        mapped_sym_disp = "' '" if mapped_sym == " " else mapped_sym

        num_sym_table.add_row(
            digit,
            "→",
            mapping.get(digit, "?"),
            "|",
            sym_disp,
            "→",
            mapped_sym_disp,
        )

    console.print(num_sym_table)
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


def get_key_meta(key_number: str) -> dict[str, str]:
    """Retrieves metadata dictionary for a given key number."""
    return keys_metadata.get(key_number, {})


# Automatically load keys upon module import
load_keys()
