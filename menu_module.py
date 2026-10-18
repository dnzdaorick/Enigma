"""Menu module for Enigma.

Minimal, polished command-line interface for message encryption, decryption,
and media key management.
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
    inspect_key,
    delete_key,
    register_media_file,
    parse_and_resolve_keys,
    scan_media_folder,
    display_media_folder_table,
    resolve_media_input,
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
            "Enter option: "
        ).strip().upper()

        verified: str = Menu.verify_user_code(user_code)
        if verified == "code not found":
            console.print(
                "[bold red]Option not found. Please enter a valid code.[/bold red]"
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
    """Prompts the user to select 1, 2, or more keys by ID or file path."""
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No keys available yet.[/bold yellow]\n"
                "Select a media file below to generate your first key.",
                border_style="yellow",
                title="Notice",
            )
        )
        available_files = scan_media_folder()
        display_media_folder_table(available_files)
        console.print("\n[dim]Choose by number (e.g. 1, or 1, 2), or enter a custom file path, or 'c' to cancel.[/dim]")
        user_input = input("Select Media: ").strip()
        if user_input.lower() in ("c", "cancel", "q", ""):
            return None

        selected_paths = resolve_media_input(user_input, available_files)
        if not selected_paths:
            prompt_delay()
            return None

        for path in selected_paths:
            register_media_file(path, interactive=False)

        return key_selection_menu()

    show_all_keys()
    console.print("[dim]Enter Key # (e.g. 1, or 1, 2 to combine keys), file path, or 'c' to cancel.[/dim]")
    user_input = input("Select Key(s): ").strip()

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
    """Displays the interactive message encryption interface."""
    display_header("ENIGMA", "Encrypt Message")
    message = input("Enter message to encrypt: ")
    if not message:
        console.print("[yellow]Empty message entered.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(message, "encrypt")


def decrypt_menu() -> None:
    """Displays the interactive message decryption interface."""
    display_header("ENIGMA", "Decrypt Message")
    encrypted_message = input("Enter ciphertext to decrypt: ")
    if not encrypted_message:
        console.print("[yellow]Empty message entered.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(encrypted_message, "decrypt")


def perform_cipher_operation(message: str, operation: str) -> None:
    """Executes multi-key encryption or decryption with visual feedback."""
    selection = key_selection_menu()
    if not selection:
        clear_screen()
        return

    num_layers = len(selection)
    layer_names = [f"#{k_id}" for k_id, _, _ in selection]
    key_desc = " + ".join(layer_names)
    action_label = "Encrypt" if operation == "encrypt" else "Decrypt"

    progress_bar(
        message=f"{action_label}ing ({key_desc})...",
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

    console.print(f"\n[bold green]Result saved to {operation.capitalize()}.txt[/bold green]")
    prompt_delay()
    clear_screen()


def generate_media_key_menu() -> None:
    """Scans media folder (with default audio) and lets user choose by number or enter a custom path."""
    display_header("ENIGMA", "Generate Media Key")
    available_files = scan_media_folder()
    display_media_folder_table(available_files)

    console.print("\n[dim]Choose by number (e.g. 1, or 1, 2), or enter a custom file path, or 'c' to cancel.[/dim]")
    user_input = input("Select Media: ").strip()
    if user_input.lower() in ("c", "cancel", "q", ""):
        clear_screen()
        return

    selected_paths = resolve_media_input(user_input, available_files)
    if not selected_paths:
        prompt_delay()
        clear_screen()
        return

    for path in selected_paths:
        register_media_file(path, interactive=True)

    clear_screen()


def key_management_menu() -> None:
    """Sub-menu for key inspection, table overview, and deletion."""
    while True:
        display_header("ENIGMA", "Key Management")
        console.print("[1] Show All Keys", style="bold cyan")
        console.print("[2] Inspect Key Mapping", style="bold yellow")
        console.print("[3] Delete a Key", style="bold red")
        console.print("[4] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask("Choose action", choices=["1", "2", "3", "4"], default="1")

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
        elif choice == "4":
            clear_screen()
            break


menu_options: list[Menu] = []