"""Menu module for Enigma Machine.

Interactive command-line interface for message encryption, decryption,
file cryptography, and multi-key (image + music) management.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from utilities_module import (
    delay_and_clear_screen,
    clear_screen,
    progress_bar,
    prompt_delay,
    display_header,
)
from key_module import (
    show_all_keys,
    select_key,
    generate_sample_image,
    generate_sample_music,
    generate_key,
    inspect_key,
    delete_key,
    register_media_file,
    parse_and_resolve_keys,
    get_key_meta,
    keys,
    keys_metadata,
)
from media_cipher import MultiKeyCipher

console = Console()


class Menu:
    """A class representing an interactive menu option."""

    def __init__(self, menu_code: str, menu_name: str, style: str):
        self.menu_code = menu_code
        self.menu_name = menu_name
        self.style = style

    def __str__(self) -> str:
        return f"[{self.menu_code}] - {self.menu_name}"

    def add_option(self):
        """Adds this menu option to the registry and returns self for method chaining."""
        menu_options.append(self)
        return self

    @staticmethod
    def show_all_options() -> None:
        """Displays all registered menu options."""
        for menu_option in menu_options:
            console.print(menu_option, style=menu_option.style)

    @staticmethod
    def get_user_code() -> str:
        """Gets and validates user input for menu selection."""
        user_code: str = input(
            "Enter the code of the option you want to select: "
        ).strip().upper()

        verified: str = Menu.verify_user_code(user_code)
        if verified == "code not found":
            console.print(
                "[bold red]Code not found! Please enter a valid code.[/bold red]"
            )
            delay_and_clear_screen()
        return verified

    @staticmethod
    def verify_user_code(user_code: str) -> str:
        """Verifies if the entered code exists among active menu options."""
        for option in menu_options:
            if user_code == option.menu_code:
                return user_code
        return "code not found"


def key_selection_menu() -> list[tuple[str, dict[str, str], dict[str, str]]] | None:
    """Prompts the user to select 1, 2, or more keys (by ID or file paths).
    
    Returns:
        List of (key_identifier, key_mapping, metadata_dict) or None if cancelled.
    """
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No cryptographic keys registered yet![/bold yellow]\n"
                "Please generate a sample key (image or music) or load an existing file.",
                border_style="yellow",
                title="Notice",
            )
        )
        choice = Prompt.ask(
            "Choose an option: [1] Generate Image Key, [2] Generate Music Key, [3] Load File, [C]ancel",
            choices=["1", "2", "3", "c"],
            default="1",
        ).lower()

        if choice == "1":
            generate_sample_image()
            return key_selection_menu()
        elif choice == "2":
            generate_sample_music()
            return key_selection_menu()
        elif choice == "3":
            file_path = input("Enter path to image or music file: ").strip().strip('"').strip("'")
            if not file_path:
                return None
            reg = register_media_file(file_path)
            if reg:
                return key_selection_menu()
            return None
        else:
            return None

    show_all_keys()
    console.print(
        "\n[bold cyan]Key Selection Options:[/bold cyan]\n"
        "  • Single key: Enter one Key # (e.g. [yellow]1[/yellow])\n"
        "  • Combine 2 or more keys: Enter comma-separated IDs (e.g. [yellow]1, 2[/yellow] to combine Image + Music)\n"
        "  • Direct files: Enter paths directly (e.g. [green]my_photo.png, song.mp3[/green])\n"
        "  • Cancel: Type [dim]'c'[/dim] to return\n"
    )
    user_input = input("Enter Key Selection: ").strip()

    if user_input.lower() in ("c", "cancel", "q", "quit", ""):
        console.print("[dim]Operation cancelled.[/dim]")
        prompt_delay()
        return None

    resolved_keys = parse_and_resolve_keys(user_input)
    if not resolved_keys:
        prompt_delay()
        return None

    return resolved_keys


def encrypt_menu() -> None:
    """Displays the interactive message encryption interface (1, 2, or more keys)."""
    display_header("Message Encryption", "Multi-Key Media Cipher (Image + Music + Multi-Layer)")
    message = input("Enter the message to encrypt: ")
    if not message:
        console.print("[yellow]Empty message entered. Returning to menu.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(message, "encrypt")


def decrypt_menu() -> None:
    """Displays the interactive message decryption interface (1, 2, or more keys)."""
    display_header("Message Decryption", "Multi-Key Media Cipher (Image + Music + Multi-Layer)")
    encrypted_message = input("Enter the encrypted message to decrypt: ")
    if not encrypted_message:
        console.print("[yellow]Empty message entered. Returning to menu.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(encrypted_message, "decrypt")


def perform_cipher_operation(message: str, operation: str) -> None:
    """Executes multi-key encryption or decryption with visual pipeline feedback."""
    selection = key_selection_menu()
    if not selection:
        clear_screen()
        return

    num_layers = len(selection)
    layer_names = [f"#{k_id} ({meta.get('media_type', 'media')})" for k_id, _, meta in selection]
    key_desc = " + ".join(layer_names)

    action_label = "Encrypt" if operation == "encrypt" else "Decrypt"
    progress_bar(
        message=f"{action_label}ing through {num_layers} layer{'s' if num_layers > 1 else ''} ({key_desc})...",
        total=5,
        step_delay=0.03,
    )
    console.print()

    cipher = MultiKeyCipher(
        message=message,
        key_layers=selection,
        show_ui=True,
    )

    if operation == "encrypt":
        result = cipher.encrypt()
        cipher.save_encryption_to_file(key_desc, result)
    else:
        result = cipher.decrypt()
        cipher.save_decryption_to_file(key_desc, result)

    console.print(f"\n[bold green]{action_label} result logged to {operation.capitalize()}.txt![/bold green]")
    prompt_delay()
    clear_screen()


def load_or_generate_media_key_menu() -> None:
    """Interface to either generate sample keys or load existing media files."""
    while True:
        display_header("Load / Generate Media Key", "Create keys from Image or Music files")
        console.print("[1] Generate Sample Key Image (.bmp)", style="bold cyan")
        console.print("[2] Generate Sample Key Music (.wav)", style="bold magenta")
        console.print("[3] Load Existing Image File (PNG, JPG, BMP, etc.)", style="bold yellow")
        console.print("[4] Load Existing Music File (MP3, WAV, OGG, FLAC, etc.)", style="bold green")
        console.print("[5] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask("Choose an action", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            clear_screen()
            generate_sample_image(interactive=True)
            break
        elif choice == "2":
            clear_screen()
            generate_sample_music(interactive=True)
            break
        elif choice == "3" or choice == "4":
            clear_screen()
            media_kind = "image" if choice == "3" else "music"
            path = input(f"Enter path to {media_kind} file: ").strip().strip('"').strip("'")
            if path:
                register_media_file(path, interactive=True)
            break
        elif choice == "5":
            clear_screen()
            break


def key_management_menu() -> None:
    """Sub-menu for key inspection, table overview, and deletion."""
    while True:
        display_header("Key Management & Inspector", "View, inspect, or manage media keys")
        console.print("[1] Show All Keys Overview", style="bold cyan")
        console.print("[2] Inspect Detailed Character Mapping & Code", style="bold yellow")
        console.print("[3] Load & Register Media File (Image / Music)", style="bold green")
        console.print("[4] Generate Sample Key Image (.bmp)", style="bold blue")
        console.print("[5] Generate Sample Key Music (.wav)", style="bold magenta")
        console.print("[6] Delete a Key", style="bold red")
        console.print("[7] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask("Choose an action", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")

        if choice == "1":
            clear_screen()
            show_all_keys()
            prompt_delay()
        elif choice == "2":
            clear_screen()
            show_all_keys()
            if not keys:
                prompt_delay()
                continue
            key_id = input("\nEnter key number to inspect: ").strip()
            inspect_key(key_id)
        elif choice == "3":
            clear_screen()
            path = input("Enter path to image or music file: ").strip().strip('"').strip("'")
            if path:
                register_media_file(path, interactive=True)
        elif choice == "4":
            clear_screen()
            generate_sample_image(interactive=True)
        elif choice == "5":
            clear_screen()
            generate_sample_music(interactive=True)
        elif choice == "6":
            clear_screen()
            show_all_keys()
            if not keys:
                prompt_delay()
                continue
            key_id = input("\nEnter key number to delete: ").strip()
            if delete_key(key_id):
                console.print(f"[bold green]Key #{key_id} deleted successfully.[/bold green]")
            else:
                console.print(f"[bold red]Key #{key_id} not found.[/bold red]")
            prompt_delay()
        elif choice == "7":
            clear_screen()
            break


def file_cipher_menu() -> None:
    """Encrypts or decrypts text files on disk using 1 or more media keys."""
    display_header("File Cryptography", "Encrypt or decrypt text documents with Media Keys")
    action = Prompt.ask("Select file operation", choices=["encrypt", "decrypt", "back"], default="encrypt")
    if action == "back":
        return

    source_path = input("Enter path to source text file: ").strip().strip('"').strip("'")
    if not os.path.exists(source_path):
        console.print(f"[bold red]Error: Source file '{source_path}' does not exist![/bold red]")
        prompt_delay()
        return

    default_dest = f"{os.path.splitext(source_path)[0]}_{action}ed.txt"
    dest_path = input(f"Enter destination file path [{default_dest}]: ").strip().strip('"').strip("'")
    if not dest_path:
        dest_path = default_dest

    selection = key_selection_menu()
    if not selection:
        return

    key_desc = " + ".join(f"#{k_id}" for k_id, _, _ in selection)

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        progress_bar(
            message=f"{action.capitalize()}ing file content across {len(selection)} key layer(s)...",
            total=6,
            step_delay=0.03,
        )

        cipher = MultiKeyCipher(
            message=content,
            key_layers=selection,
            show_ui=False,
        )
        result = cipher.encrypt() if action == "encrypt" else cipher.decrypt()

        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(result)

        console.print(
            Panel(
                f"[bold green]Operation complete![/bold green]\n"
                f"Source: [cyan]{source_path}[/cyan]\n"
                f"Destination: [cyan]{dest_path}[/cyan]\n"
                f"Key(s) Used: [yellow]{key_desc}[/yellow] ({len(selection)} layer{'s' if len(selection) > 1 else ''})",
                title="File Cryptography Result",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[bold red]An error occurred during file processing: {e}[/bold red]")

    prompt_delay()
    clear_screen()


menu_options: list[Menu] = []