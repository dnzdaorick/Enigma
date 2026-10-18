"""Key module for Media Key Cipher.

Manages image and music cryptographic keys, SHA-256 fingerprints, and persistence in keys.json.
"""

import json
import os
import re
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from utilities_module import clear_screen, delay_screen, prompt_delay
from media_cipher import (
    read_media_bytes,
    media_to_code,
    detect_media_type,
    generate_key_from_bytes,
    create_sample_bmp_image,
    create_sample_wav_music,
    ALPHABET_LOWER,
    ALPHABET_UPPER,
    NUMBERS,
    SYMBOLS,
    FULL_CHARSET,
)

console = Console()
KEYS_FILE = "keys.json"
KEYS_DIR = "key_media"

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
                file_path = info.get("file_path", info.get("image_path", "Generated/Custom Media"))
                m_type = info.get("media_type", detect_media_type(file_path))
                keys_metadata[str(key_id)] = {
                    "created_at": info.get("created_at", "Unknown"),
                    "file_path": file_path,
                    "image_path": file_path,  # backward compatibility alias
                    "code": info.get("code", info.get("image_code", "N/A")),
                    "image_code": info.get("code", info.get("image_code", "N/A")),
                    "byte_size": str(info.get("byte_size", "N/A")),
                    "media_type": m_type,
                }
            elif isinstance(info, dict):
                # Legacy raw mapping fallback
                keys[str(key_id)] = info
                keys_metadata[str(key_id)] = {
                    "created_at": "Earlier session",
                    "file_path": "Legacy Key",
                    "image_path": "Legacy Key",
                    "code": "N/A",
                    "image_code": "N/A",
                    "byte_size": "N/A",
                    "media_type": "media",
                }
    except Exception as e:
        console.print(f"[bold red]Warning: Failed to load keys from {KEYS_FILE}: {e}[/bold red]")


def save_keys() -> None:
    """Persists all current keys and metadata to keys.json."""
    data = {}
    for key_id, mapping in keys.items():
        meta = keys_metadata.get(key_id, {})
        file_path = meta.get("file_path", meta.get("image_path", "N/A"))
        code = meta.get("code", meta.get("image_code", "N/A"))
        data[key_id] = {
            "created_at": meta.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "file_path": file_path,
            "image_path": file_path,
            "code": code,
            "image_code": code,
            "byte_size": meta.get("byte_size", "N/A"),
            "media_type": meta.get("media_type", detect_media_type(file_path)),
            "mapping": mapping,
        }
    try:
        with open(KEYS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        console.print(f"[bold red]Error saving keys: {e}[/bold red]")


def register_media_file(file_path: str, interactive: bool = True) -> tuple[str, dict[str, str]] | None:
    """Converts any image or music file into cryptographic code, derives a substitution key, and registers it."""
    file_path = os.path.normpath(file_path.strip().strip('"').strip("'"))
    if not os.path.exists(file_path):
        if interactive:
            console.print(f"[bold red]Error: Media file '{file_path}' not found![/bold red]")
            prompt_delay()
        return None

    try:
        media_bytes = read_media_bytes(file_path)
    except Exception as e:
        if interactive:
            console.print(f"[bold red]Error reading media file: {e}[/bold red]")
            prompt_delay()
        return None

    subst_key, _, code_info = generate_key_from_bytes(media_bytes, file_path)
    media_type = code_info["media_type"]

    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_id = str(max(existing_numeric_ids) + 1 if existing_numeric_ids else 1)

    keys[next_id] = subst_key
    keys_metadata[next_id] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": file_path,
        "image_path": file_path,
        "code": code_info["sha256"],
        "image_code": code_info["sha256"],
        "byte_size": code_info["byte_size"],
        "media_type": media_type,
    }

    save_keys()

    if interactive:
        icon = "🖼️ Image" if media_type == "image" else ("🎵 Music" if media_type == "music" else "📁 Media")
        panel_content = (
            f"[bold green]{icon} Key successfully created and registered![/bold green]\n\n"
            f"[cyan]Key ID:[/cyan] [bold white]#{next_id}[/bold white]\n"
            f"[cyan]Media Type:[/cyan] {icon}\n"
            f"[cyan]Source File:[/cyan] {file_path}\n"
            f"[cyan]File Size:[/cyan] {code_info['byte_size']} bytes\n"
            f"[cyan]Code Fingerprint (SHA-256):[/cyan]\n[bold yellow]{code_info['sha256']}[/bold yellow]\n"
            f"[cyan]Short Token:[/cyan] [bold cyan]{code_info['short_code']}[/bold cyan]\n"
            f"[dim]Scrambles 95 characters: Alphabet (52), Numbers (10), Symbols (33)[/dim]"
        )
        console.print(Panel(panel_content, title="Key Registered", border_style="green"))
        prompt_delay()
        clear_screen()

    return next_id, subst_key


# Aliases for backward compatibility
register_image_file = register_media_file


def generate_sample_image(interactive: bool = True) -> tuple[str, dict[str, str]] | None:
    """Generates a sample cryptographic key image (.bmp) and registers it."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_num = max(existing_numeric_ids) + 1 if existing_numeric_ids else 1
    image_filename = f"key_image_{next_num}.bmp"
    image_path = os.path.join(KEYS_DIR, image_filename)

    create_sample_bmp_image(image_path, width=128, height=128)
    return register_media_file(image_path, interactive=interactive)


def generate_sample_music(interactive: bool = True) -> tuple[str, dict[str, str]] | None:
    """Generates a sample cryptographic key audio file (.wav) and registers it."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_num = max(existing_numeric_ids) + 1 if existing_numeric_ids else 1
    music_filename = f"key_music_{next_num}.wav"
    music_path = os.path.join(KEYS_DIR, music_filename)

    create_sample_wav_music(music_path, duration_sec=2.0)
    return register_media_file(music_path, interactive=interactive)


def generate_key(interactive: bool = True) -> dict[str, str]:
    """Default key generation: creates a sample image key."""
    res = generate_sample_image(interactive=interactive)
    return res[1] if res else {}


def show_all_keys() -> None:
    """Displays all available image and music keys in a formatted Rich Table."""
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No media keys available.[/bold yellow]\n"
                "Please generate a key image/music or load a file first using option [bold cyan][C][/bold cyan].",
                title="Key Store Status",
                border_style="yellow",
            )
        )
        return

    key_table = Table(title="Available Media Substitution Keys", style="bold magenta", box=box.ROUNDED)
    key_table.add_column("Key #", style="bold cyan", justify="center", width=7)
    key_table.add_column("Type", style="magenta", justify="center", width=10)
    key_table.add_column("Media File", style="green", justify="left")
    key_table.add_column("Code Fingerprint (SHA-256)", style="yellow", justify="left")
    key_table.add_column("Size", style="cyan", justify="center")
    key_table.add_column("Created At", style="dim", justify="center")

    for key_number, mapping in sorted(keys.items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
        meta = keys_metadata.get(key_number, {})
        created_time = meta.get("created_at", "N/A")
        file_path = os.path.basename(meta.get("file_path", meta.get("image_path", "N/A")))
        code = meta.get("code", meta.get("image_code", "N/A"))
        short_code = code[:16] + "..." if len(code) > 16 else code
        file_size = meta.get("byte_size", "N/A")
        if file_size != "N/A":
            file_size += " B"

        m_type = meta.get("media_type", "media").lower()
        type_badge = "🖼️ Image" if m_type == "image" else ("🎵 Music" if m_type == "music" else "📁 Media")

        key_table.add_row(
            key_number,
            type_badge,
            file_path,
            short_code,
            file_size,
            created_time,
        )

    console.print(key_table)


def inspect_key(key_number: str) -> None:
    """Displays the media code metadata and comprehensive character substitution mapping."""
    if key_number not in keys:
        console.print(f"[bold red]Key #{key_number} not found![/bold red]")
        prompt_delay()
        return

    mapping = keys[key_number]
    meta = keys_metadata.get(key_number, {})
    m_type = meta.get("media_type", "media").lower()
    icon = "🖼️ Image" if m_type == "image" else ("🎵 Music" if m_type == "music" else "📁 Media")

    clear_screen()
    # Metadata Overview
    meta_panel = (
        f"[cyan]Key Number:[/cyan] [bold white]#{key_number}[/bold white]\n"
        f"[cyan]Key Type:[/cyan] {icon}\n"
        f"[cyan]Source File:[/cyan] {meta.get('file_path', meta.get('image_path', 'N/A'))}\n"
        f"[cyan]File Size:[/cyan] {meta.get('byte_size', 'N/A')} bytes\n"
        f"[cyan]Created:[/cyan] {meta.get('created_at', 'N/A')}\n"
        f"[cyan]Full Code (SHA-256):[/cyan]\n[bold yellow]{meta.get('code', meta.get('image_code', 'N/A'))}[/bold yellow]\n"
        f"[dim]Total Substituted Characters: {len(mapping)} (Alphabet, Numbers, Symbols & Space)[/dim]"
    )
    console.print(Panel(meta_panel, title=f"Media Key #{key_number} Details", border_style="bright_blue"))

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
    """Selects a single key from the keys dictionary. Returns (key_number, key_mapping) or None."""
    if key_number not in keys:
        console.print(
            "[bold red]Key not found! Please enter a valid key number.[/bold red]"
        )
        delay_screen(1.0)
        return None
    return key_number, keys[key_number]


def parse_and_resolve_keys(
    input_str: str,
) -> list[tuple[str, dict[str, str], dict[str, str]]] | None:
    """Parses user input string containing 1, 2, or more key IDs or file paths.
    
    Examples of valid input:
      - '1' (Single Key #1)
      - '1, 2' or '1,2' (Combine Key 1 and Key 2)
      - '1 + 2 + 3' (Combine 3 keys)
      - 'photo.png, song.mp3' (Direct file paths)
    
    Returns:
        List of (key_identifier, mapping, metadata_dict) in order, or None if invalid.
    """
    raw_tokens = [tok.strip().strip('"').strip("'") for tok in re.split(r"[,+\s]+", input_str.strip()) if tok.strip()]
    if not raw_tokens:
        return None

    resolved: list[tuple[str, dict[str, str], dict[str, str]]] = []

    for token in raw_tokens:
        # Check enrolled key ID
        if token in keys:
            mapping = keys[token]
            meta = keys_metadata.get(token, {})
            resolved.append((token, mapping, meta))
        # Check direct media file on disk
        elif os.path.exists(token):
            try:
                b = read_media_bytes(token)
                mapping, _, code_info = generate_key_from_bytes(b, token)
                meta = {
                    "file_path": token,
                    "image_path": token,
                    "code": code_info["sha256"],
                    "image_code": code_info["sha256"],
                    "byte_size": code_info["byte_size"],
                    "media_type": code_info["media_type"],
                }
                resolved.append((f"File ({os.path.basename(token)})", mapping, meta))
            except Exception as e:
                console.print(f"[bold red]Error reading '{token}': {e}[/bold red]")
                return None
        else:
            console.print(f"[bold red]Key #{token} not found and file '{token}' does not exist![/bold red]")
            return None

    return resolved


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
