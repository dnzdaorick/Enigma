"""Key module for Enigma.

Manages image and music cryptographic keys, SHA-256 fingerprints, and persistence in keys.json.
"""

import json
import os
import re
import sys
import tempfile
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from utilities_module import clear_screen, delay_screen, prompt_delay

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
from media_cipher import (
    read_media_bytes,
    media_to_code,
    detect_media_type,
    generate_key_from_bytes,
    IMAGE_EXTENSIONS,
    AUDIO_EXTENSIONS,
)
from cipher_module import (
    generate_monoalphabetic_key,
    generate_vigenere_key,
    generate_xor_key,
    vigenere_classical_encrypt,
    vigenere_encrypt,
    vigenere_decrypt,
    xor_encrypt,
    xor_decrypt,
    ALPHABET_LOWER,
    ALPHABET_UPPER,
    NUMBERS,
    SYMBOLS,
    FULL_CHARSET,
)

console = Console()
KEYS_FILE = "keys.json"
KEYS_DIR = "key_media"
MEDIA_DIR = "media"

# In-memory storage of key mappings and their metadata
keys: dict[str, dict[str, str]] = {}
keys_metadata: dict[str, dict[str, str]] = {}


def scan_media_folder(base_dir: str = MEDIA_DIR) -> list[str]:
    """Scans media directory (including audio/ and images/) for media files.
    
    Always ensures media/audio and media/images exist, and that a default audio
    file is available in media/audio if no audio files exist yet.
    Returns a sorted list of discovered file paths with audio files first.
    """
    audio_dir = os.path.join(base_dir, "audio")
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # Check for audio files in media/audio
    audio_files = [
        f for f in os.listdir(audio_dir)
        if os.path.splitext(f.lower())[1] in AUDIO_EXTENSIONS
    ]
    # If no audio files exist, ensure default_audio.wav is created
    if not audio_files:
        default_wav = os.path.join(audio_dir, "default_audio.wav")
        if not os.path.exists(default_wav):
            from media_cipher import create_sample_wav_music
            create_sample_wav_music(default_wav, duration_sec=2.0)

    # Collect all valid media files from base_dir and its subdirectories
    discovered: list[str] = []
    if os.path.exists(base_dir):
        for root, _, files in os.walk(base_dir):
            for f in files:
                ext = os.path.splitext(f.lower())[1]
                if ext in IMAGE_EXTENSIONS or ext in AUDIO_EXTENSIONS:
                    discovered.append(os.path.normpath(os.path.join(root, f)))

    # Sort: audio first (default audio accessible as #1), then images
    def sort_key(p: str):
        is_audio = 0 if detect_media_type(p) == "music" else 1
        return (is_audio, os.path.basename(p).lower())

    discovered.sort(key=sort_key)
    return discovered


def display_media_folder_table(files: list[str]) -> None:
    """Renders a clean, numbered table of discovered media files in media/."""
    if not files:
        console.print("[yellow]No media files found in media folder.[/yellow]")
        return

    table = Table(title="Available Media Files", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("#", style="bold yellow", justify="center", width=5)
    table.add_column("Type", style="magenta", justify="center", width=10)
    table.add_column("File Name", style="bold green", justify="left")
    table.add_column("Folder", style="dim", justify="left")
    table.add_column("Size", style="cyan", justify="right")

    for idx, path in enumerate(files, start=1):
        m_type = detect_media_type(path)
        icon = "🎵 Audio" if m_type == "music" else ("🖼️ Image" if m_type == "image" else "📁 Media")
        fname = os.path.basename(path)
        rel_dir = os.path.relpath(os.path.dirname(path), start=".")
        size_bytes = os.path.getsize(path) if os.path.exists(path) else 0
        if size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        elif size_bytes >= 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes} B"

        table.add_row(str(idx), icon, fname, rel_dir, size_str)

    console.print(table)


def resolve_media_input(user_input: str, available_files: list[str]) -> list[str] | None:
    """Resolves numbers (e.g. '1', '1, 2') against available_files OR accepts custom file path(s)."""
    raw_tokens = [tok.strip().strip('"').strip("'") for tok in re.split(r"[,+\s]+", user_input.strip()) if tok.strip()]
    if not raw_tokens:
        return None

    resolved_paths: list[str] = []
    for token in raw_tokens:
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(available_files):
                resolved_paths.append(available_files[idx])
            else:
                console.print(f"[bold red]Selection #{token} out of range (1 to {len(available_files)}).[/bold red]")
                return None
        elif os.path.exists(token):
            resolved_paths.append(token)
        else:
            console.print(f"[bold red]Invalid selection or file '{token}' not found.[/bold red]")
            return None

    return resolved_paths


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
                file_path = info.get("file_path", info.get("image_path", "Custom Media"))
                m_type = info.get("media_type", detect_media_type(file_path))
                c_type = info.get("cipher_type", m_type)
                keys_metadata[str(key_id)] = {
                    "created_at": info.get("created_at", "Unknown"),
                    "file_path": file_path,
                    "image_path": file_path,
                    "code": info.get("code", info.get("image_code", "N/A")),
                    "image_code": info.get("code", info.get("image_code", "N/A")),
                    "byte_size": str(info.get("byte_size", "N/A")),
                    "media_type": m_type,
                    "cipher_type": c_type,
                    "key_value": info.get("key_value", ""),
                    "variant": info.get("variant", "classical"),
                }
            elif isinstance(info, dict):
                keys[str(key_id)] = info
                keys_metadata[str(key_id)] = {
                    "created_at": "Earlier session",
                    "file_path": "Legacy Key",
                    "image_path": "Legacy Key",
                    "code": "N/A",
                    "image_code": "N/A",
                    "byte_size": "N/A",
                    "media_type": "media",
                    "cipher_type": "media",
                    "key_value": "",
                    "variant": "classical",
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
        m_type = meta.get("media_type", detect_media_type(file_path))
        c_type = meta.get("cipher_type", m_type)
        data[key_id] = {
            "created_at": meta.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "file_path": file_path,
            "image_path": file_path,
            "code": code,
            "image_code": code,
            "byte_size": meta.get("byte_size", "N/A"),
            "media_type": m_type,
            "cipher_type": c_type,
            "key_value": meta.get("key_value", ""),
            "variant": meta.get("variant", "classical"),
            "mapping": mapping,
        }
    try:
        with open(KEYS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        console.print(f"[bold red]Error saving keys: {e}[/bold red]")


def register_media_file(file_path: str, interactive: bool = True) -> tuple[str, dict[str, str]] | None:
    """Converts any image or music file into cryptographic code and registers the key."""
    file_path = os.path.normpath(file_path.strip().strip('"').strip("'"))
    if not os.path.exists(file_path):
        if interactive:
            console.print(f"[bold red]Error: File '{file_path}' not found.[/bold red]")
            prompt_delay()
        return None

    try:
        media_bytes = read_media_bytes(file_path)
    except Exception as e:
        if interactive:
            console.print(f"[bold red]Error reading file: {e}[/bold red]")
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
            f"[bold green]{icon} Key Generated Successfully[/bold green]\n\n"
            f"[cyan]Key ID:[/cyan] [bold white]#{next_id}[/bold white]  |  [cyan]Type:[/cyan] {icon}  |  [cyan]Size:[/cyan] {code_info['byte_size']} B\n"
            f"[cyan]Source File:[/cyan] {file_path}\n"
            f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{code_info['sha256']}[/bold yellow]\n\n"
            f"[dim]95 characters substituted (Alphabet, Numbers, Symbols & Space)[/dim]"
        )
        console.print(Panel(panel_content, title="Key Ready", border_style="green"))
        prompt_delay()
        clear_screen()

    return next_id, subst_key


# Aliases and test helper functions
register_image_file = register_media_file


def register_monoalphabetic_key(
    interactive: bool = True, *args, **kwargs
) -> tuple[str, dict[str, str]]:
    """Generates and persists a classical random alphabet monoalphabetic substitution key."""
    subst_key, _, code_info = generate_monoalphabetic_key()

    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_id = str(max(existing_numeric_ids) + 1 if existing_numeric_ids else 1)

    keys[next_id] = subst_key
    keys_metadata[next_id] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": code_info["label"],
        "image_path": code_info["label"],
        "code": code_info["sha256"],
        "image_code": code_info["sha256"],
        "byte_size": code_info["byte_size"],
        "media_type": "monoalphabetic",
        "cipher_type": "monoalphabetic",
        "key_value": code_info["key_value"],
        "variant": "classical",
    }

    save_keys()

    if interactive:
        panel_content = (
            f"[bold green]🔤 Monoalphabetic Key Generated Successfully[/bold green]\n\n"
            f"[cyan]Key ID:[/cyan] [bold white]#{next_id}[/bold white]  |  [cyan]Type:[/cyan] 🔤 Monoalphabetic Cipher\n"
            f"[cyan]Method:[/cyan] Random Alphabet (A-Z / a-z permuted)\n"
            f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{code_info['sha256']}[/bold yellow]\n\n"
            f"[dim]Deterministic 1-to-1 letter substitution (numbers & symbols preserved)[/dim]"
        )
        console.print(Panel(panel_content, title="Key Ready", border_style="green"))
        prompt_delay()
        clear_screen()

    return next_id, subst_key


def register_vigenere_key(
    keyword: str = "", interactive: bool = True, *args, **kwargs
) -> tuple[str, dict[str, str]]:
    """Generates and persists a classical Vigenère cipher key."""
    kw, code_info = generate_vigenere_key(keyword=keyword, variant="classical")

    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_id = str(max(existing_numeric_ids) + 1 if existing_numeric_ids else 1)

    keys[next_id] = {}
    keys_metadata[next_id] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": code_info["label"],
        "image_path": code_info["label"],
        "code": code_info["sha256"],
        "image_code": code_info["sha256"],
        "byte_size": code_info["byte_size"],
        "media_type": "vigenere",
        "cipher_type": "vigenere",
        "key_value": kw,
        "variant": "classical",
    }

    save_keys()

    if interactive:
        panel_content = (
            f"[bold green]🗝️ Vigenère Cipher Key Generated Successfully[/bold green]\n\n"
            f"[cyan]Key ID:[/cyan] [bold white]#{next_id}[/bold white]  |  [cyan]Type:[/cyan] 🗝️ Vigenère Cipher (A-Z modulo 26)\n"
            f"[cyan]Keyword / Passphrase:[/cyan] [bold yellow]{kw}[/bold yellow] ({len(kw)} chars)\n"
            f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{code_info['sha256']}[/bold yellow]\n\n"
            f"[dim]Polyalphabetic keystream substitution active[/dim]"
        )
        console.print(Panel(panel_content, title="Key Ready", border_style="green"))
        prompt_delay()
        clear_screen()

    return next_id, keys[next_id]


def register_xor_key(
    key_string: str = "", length: int = 16, interactive: bool = True, *args, **kwargs
) -> tuple[str, dict[str, str]]:
    """Generates and persists a classical XOR cipher key."""
    k_str, code_info = generate_xor_key(key_string=key_string, length=length)

    existing_numeric_ids = [int(k) for k in keys.keys() if k.isdigit()]
    next_id = str(max(existing_numeric_ids) + 1 if existing_numeric_ids else 1)

    keys[next_id] = {}
    keys_metadata[next_id] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": code_info["label"],
        "image_path": code_info["label"],
        "code": code_info["sha256"],
        "image_code": code_info["sha256"],
        "byte_size": code_info["byte_size"],
        "media_type": "xor",
        "cipher_type": "xor",
        "key_value": k_str,
        "variant": "classical",
    }

    save_keys()

    if interactive:
        hex_preview = k_str.encode("utf-8").hex()
        panel_content = (
            f"[bold green]⚡ XOR Cipher Key Generated Successfully[/bold green]\n\n"
            f"[cyan]Key ID:[/cyan] [bold white]#{next_id}[/bold white]  |  [cyan]Type:[/cyan] ⚡ XOR Cipher  |  [cyan]Length:[/cyan] {len(k_str)} bytes\n"
            f"[cyan]Key String:[/cyan] [bold yellow]{k_str}[/bold yellow]\n"
            f"[cyan]Hex Bytes:[/cyan] [dim]{hex_preview}[/dim]\n"
            f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{code_info['sha256']}[/bold yellow]\n\n"
            f"[dim]Repeating bitwise XOR keystream[/dim]"
        )
        console.print(Panel(panel_content, title="Key Ready", border_style="green"))
        prompt_delay()
        clear_screen()

    return next_id, keys[next_id]


def generate_sample_image(interactive: bool = False) -> tuple[str, dict[str, str]] | None:
    """Helper for testing: creates sample BMP image key."""
    from media_cipher import create_sample_bmp_image
    test_path = os.path.join(tempfile.gettempdir() if "tempfile" in globals() else ".", "test_sample.bmp")
    create_sample_bmp_image(test_path, width=32, height=32)
    return register_media_file(test_path, interactive=interactive)


def generate_sample_music(interactive: bool = False) -> tuple[str, dict[str, str]] | None:
    """Helper for testing: creates sample WAV music key."""
    from media_cipher import create_sample_wav_music
    test_path = os.path.join(tempfile.gettempdir() if "tempfile" in globals() else ".", "test_sample.wav")
    create_sample_wav_music(test_path, duration_sec=0.5)
    return register_media_file(test_path, interactive=interactive)


def show_all_keys() -> None:
    """Displays all available keys in a formatted table."""
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No keys available.[/bold yellow]\n"
                "Use option [bold cyan][C] Generate Key[/bold cyan] from the main menu.",
                title="Keys",
                border_style="yellow",
            )
        )
        return

    key_table = Table(title="Available Keys", style="bold magenta", box=box.ROUNDED)
    key_table.add_column("Key #", style="bold cyan", justify="center", width=7)
    key_table.add_column("Type", style="magenta", justify="center", width=12)
    key_table.add_column("Source / Key", style="green", justify="left")
    key_table.add_column("SHA-256 Code", style="yellow", justify="left")
    key_table.add_column("Size", style="cyan", justify="center")
    key_table.add_column("Created", style="dim", justify="center")

    for key_number, mapping in sorted(keys.items(), key=lambda x: int(x[0]) if x[0].isdigit() else str(x[0])):
        meta = keys_metadata.get(key_number, {})
        created_time = meta.get("created_at", "N/A")
        code = meta.get("code", meta.get("image_code", "N/A"))
        short_code = code[:16] + "..." if len(code) > 16 else code
        file_size = meta.get("byte_size", "N/A")
        if file_size != "N/A":
            file_size += " B"

        m_type = meta.get("media_type", "media").lower()
        if m_type == "image":
            type_badge = "🖼️ Image"
            source_display = os.path.basename(meta.get("file_path", meta.get("image_path", "N/A")))
        elif m_type == "music":
            type_badge = "🎵 Music"
            source_display = os.path.basename(meta.get("file_path", meta.get("image_path", "N/A")))
        elif m_type == "monoalphabetic":
            type_badge = "🔤 Mono"
            source_display = meta.get("file_path", "Monoalphabetic Key")
        elif m_type == "vigenere":
            type_badge = "🗝️ Vigenère"
            kw = meta.get("key_value", "")
            source_display = f"Key: '{kw}'"
        elif m_type == "xor":
            type_badge = "⚡ XOR"
            kw = meta.get("key_value", "")
            source_display = f"Key: '{kw[:10]}...' ({len(kw)} B)" if len(kw) > 10 else f"Key: '{kw}'"
        else:
            type_badge = "📁 Media"
            source_display = os.path.basename(meta.get("file_path", "N/A"))

        key_table.add_row(
            key_number,
            type_badge,
            source_display,
            short_code,
            file_size,
            created_time,
        )

    console.print(key_table)


def inspect_key(key_number: str) -> None:
    """Displays the key metadata, character mapping, or cipher details."""
    if key_number not in keys:
        console.print(f"[bold red]Key #{key_number} not found.[/bold red]")
        prompt_delay()
        return

    mapping = keys[key_number]
    meta = keys_metadata.get(key_number, {})
    m_type = meta.get("media_type", "media").lower()

    if m_type == "vigenere":
        clear_screen()
        kw = meta.get("key_value", "")
        meta_panel = (
            f"[cyan]Key Number:[/cyan] [bold white]#{key_number}[/bold white]  |  [cyan]Type:[/cyan] 🗝️ Vigenère Cipher\n"
            f"[cyan]Keyword / Passphrase:[/cyan] [bold yellow]{kw}[/bold yellow]  |  [cyan]Length:[/cyan] {len(kw)} characters\n"
            f"[cyan]Created:[/cyan] {meta.get('created_at', 'N/A')}\n"
            f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{meta.get('code', 'N/A')}[/bold yellow]\n"
            f"[dim]Polyalphabetic shifting keystream[/dim]"
        )
        console.print(Panel(meta_panel, title=f"Key #{key_number} Details (Vigenère)", border_style="bright_blue"))

        shifts_table = Table(title=f"Vigenère Keystream Shifts (Keyword: '{kw}')", box=box.SIMPLE_HEAD, header_style="bold cyan")
        shifts_table.add_column("Pos", justify="center", style="dim")
        shifts_table.add_column("Key Char", justify="center", style="bold yellow")
        shifts_table.add_column("Shift", justify="center", style="bold green")
        shifts_table.add_column("Example ('A' → )", justify="center", style="cyan")
        shifts_table.add_column("Sample Encrypt ('HELLO')", justify="center", style="magenta")

        for idx, ch in enumerate(kw[:12], start=1):
            if ch.isalpha():
                s = ord(ch.upper()) - ord("A")
                enc_a = chr((ord("A") - ord("A") + s) % 26 + ord("A"))
            else:
                s = FULL_CHARSET.index(ch) % 26 if ch in FULL_CHARSET else 0
                enc_a = chr((ord("A") - ord("A") + s) % 26 + ord("A"))
            sample_sub = vigenere_classical_encrypt("HELLO", ch * 5)
            shifts_table.add_row(str(idx), ch, f"+{s}", enc_a, sample_sub)

        console.print(shifts_table)
        prompt_delay()
        clear_screen()
        return

    if m_type == "xor":
        clear_screen()
        k_val = meta.get("key_value", "")
        hex_repr = k_val.encode("utf-8").hex()
        meta_panel = (
            f"[cyan]Key Number:[/cyan] [bold white]#{key_number}[/bold white]  |  [cyan]Type:[/cyan] ⚡ XOR Cipher\n"
            f"[cyan]Key String:[/cyan] [bold yellow]{k_val}[/bold yellow]\n"
            f"[cyan]Hex Bytes:[/cyan] [dim]{hex_repr}[/dim]\n"
            f"[cyan]Key Length:[/cyan] {len(k_val)} bytes  |  [cyan]Created:[/cyan] {meta.get('created_at', 'N/A')}\n"
            f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{meta.get('code', 'N/A')}[/bold yellow]\n"
            f"[dim]Bitwise XOR cipher outputting hex stream[/dim]"
        )
        console.print(Panel(meta_panel, title=f"Key #{key_number} Details (XOR)", border_style="bright_blue"))

        xor_table = Table(title="XOR Keystream Byte Representation", box=box.SIMPLE_HEAD, header_style="bold cyan")
        xor_table.add_column("Byte #", justify="center", style="dim")
        xor_table.add_column("Char", justify="center", style="bold yellow")
        xor_table.add_column("ASCII (Dec)", justify="center", style="green")
        xor_table.add_column("Hex", justify="center", style="cyan")
        xor_table.add_column("Binary", justify="center", style="magenta")

        for idx, ch in enumerate(k_val[:16], start=1):
            dec_val = ord(ch)
            xor_table.add_row(str(idx), ch, str(dec_val), f"0x{dec_val:02X}", f"{dec_val:08b}")

        console.print(xor_table)
        prompt_delay()
        clear_screen()
        return

    clear_screen()
    icon = "🖼️ Image" if m_type == "image" else ("🎵 Music" if m_type == "music" else "🔤 Monoalphabetic")
    meta_panel = (
        f"[cyan]Key Number:[/cyan] [bold white]#{key_number}[/bold white]  |  [cyan]Type:[/cyan] {icon}\n"
        f"[cyan]Source / Info:[/cyan] {meta.get('file_path', meta.get('image_path', 'N/A'))}\n"
        f"[cyan]Size:[/cyan] {meta.get('byte_size', 'N/A')} bytes/chars  |  [cyan]Created:[/cyan] {meta.get('created_at', 'N/A')}\n"
        f"[cyan]Code (SHA-256):[/cyan]\n[bold yellow]{meta.get('code', meta.get('image_code', 'N/A'))}[/bold yellow]\n"
        f"[dim]Substituted Characters: {len(mapping)}[/dim]"
    )
    console.print(Panel(meta_panel, title=f"Key #{key_number} Details", border_style="bright_blue"))

    letters_table = Table(title="Alphabet (a-z, A-Z)", box=box.SIMPLE_HEAD, header_style="bold cyan")
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

    num_sym_table = Table(title="Numbers (0-9) & Symbols", box=box.SIMPLE_HEAD, header_style="bold cyan")
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
    """Selects a single key from the keys dictionary."""
    if key_number not in keys:
        console.print("[bold red]Key not found.[/bold red]")
        delay_screen(1.0)
        return None
    return key_number, keys[key_number]


def parse_and_resolve_keys(
    input_str: str,
) -> list[tuple[str, dict[str, str], dict[str, str]]] | None:
    """Parses user input containing 1, 2, or more key IDs or file paths.
    
    Supports space-separated ('1 2 3 4 5'), comma-separated ('1, 2, 3, 4, 5'),
    plus-separated ('1 + 2 + 3'), unseparated sequence ('12345'), or quoted paths.
    """
    clean_input = input_str.strip()
    if not clean_input:
        return None

    # If the entire input is an existing path, treat as single file
    unquoted = clean_input.strip('"').strip("'")
    if os.path.exists(unquoted):
        raw_tokens = [unquoted]
    else:
        # Match quoted strings or non-whitespace, non-comma, non-plus tokens
        pattern = r'"([^"]+)"|\'([^\']+)\'|([^,+\s]+)'
        raw_tokens = []
        for match in re.finditer(pattern, clean_input):
            tok = match.group(1) or match.group(2) or match.group(3)
            if tok and tok.strip():
                raw_tokens.append(tok.strip())

    if not raw_tokens:
        return None

    # Check if a single continuous token was entered like "12345" where each digit is an enrolled key
    if len(raw_tokens) == 1 and raw_tokens[0] not in keys and not os.path.exists(raw_tokens[0]):
        single_str = raw_tokens[0]
        if len(single_str) > 1 and all(ch in keys for ch in single_str):
            raw_tokens = list(single_str)

    resolved: list[tuple[str, dict[str, str], dict[str, str]]] = []

    for token in raw_tokens:
        if token in keys:
            mapping = keys[token]
            meta = keys_metadata.get(token, {})
            resolved.append((token, mapping, meta))
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
            console.print(f"[bold red]Key #{token} not found and file '{token}' does not exist.[/bold red]")
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
