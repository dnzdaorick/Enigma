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
from key_module import show_all_keys, select_key, generate_key, inspect_key, delete_key, keys
from monoalphabetic_cipher import MonoalphabeticCipher

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


def key_selection_menu() -> tuple[str, dict[str, str]] | None:
    """Displays available keys and safely prompts user for a valid key selection."""
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No keys available yet![/bold yellow]\n"
                "Please generate a key first before performing cryptographic operations.",
                border_style="yellow",
                title="Notice",
            )
        )
        create_now = Prompt.ask("Would you like to generate a new key now? (y/n)", default="y")
        if create_now.lower() == "y":
            generate_key()
            return key_selection_menu()
        prompt_delay()
        return None

    show_all_keys()
    select_key_number = input("\nEnter the key number (or 'c' to cancel): ").strip()
    if select_key_number.lower() in ("c", "cancel", "q", "quit", ""):
        console.print("[dim]Operation cancelled.[/dim]")
        prompt_delay()
        return None

    selection = select_key(select_key_number)
    if selection is None:
        prompt_delay()
        return None
    return selection


def encrypt_menu() -> None:
    """Displays the interactive message encryption interface."""
    display_header("Message Encryption", "Monoalphabetic Substitution Cipher")
    message = input("Enter the message to encrypt: ")
    if not message:
        console.print("[yellow]Empty message entered. Returning to menu.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(message, "encrypt")


def decrypt_menu() -> None:
    """Displays the interactive message decryption interface."""
    display_header("Message Decryption", "Monoalphabetic Substitution Cipher")
    encrypted_message = input("Enter the encrypted message to decrypt: ")
    if not encrypted_message:
        console.print("[yellow]Empty message entered. Returning to menu.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(encrypted_message, "decrypt")


def perform_cipher_operation(message: str, operation: str) -> None:
    """Executes encryption or decryption safely with visual feedback and audit logging."""
    selection = key_selection_menu()
    if selection is None:
        clear_screen()
        return

    key_number, key = selection

    progress_bar(message=f"{operation.capitalize()}ing message...", total=5, step_delay=0.03)
    console.print()

    cipher = MonoalphabeticCipher(message, key, preserve_formatting=True)
    if operation == "encrypt":
        result = cipher.encrypt()
        cipher.save_encryption_to_file(key_number, result)
    else:
        result = cipher.decrypt()
        cipher.save_decryption_to_file(key_number, result)

    console.print(f"\n[bold green]{operation.capitalize()} result logged to {operation.capitalize()}.txt![/bold green]")
    prompt_delay()
    clear_screen()


def key_management_menu() -> None:
    """Sub-menu for key inspection, table overview, and deletion."""
    while True:
        display_header("Key Management & Inspector", "View, inspect, or manage substitution keys")
        console.print("[1] Show All Keys Overview", style="bold cyan")
        console.print("[2] Inspect Detailed Character Mapping for a Key", style="bold yellow")
        console.print("[3] Delete a Key", style="bold red")
        console.print("[4] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask("Choose an action", choices=["1", "2", "3", "4"], default="1")

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


def file_cipher_menu() -> None:
    """Encrypts or decrypts text files on disk."""
    display_header("File Cryptography", "Encrypt or decrypt text documents")
    action = Prompt.ask("Select file operation", choices=["encrypt", "decrypt", "back"], default="encrypt")
    if action == "back":
        return

    source_path = input("Enter path to source text file: ").strip().strip('"')
    if not os.path.exists(source_path):
        console.print(f"[bold red]Error: Source file '{source_path}' does not exist![/bold red]")
        prompt_delay()
        return

    default_dest = f"{os.path.splitext(source_path)[0]}_{action}ed.txt"
    dest_path = input(f"Enter destination file path [{default_dest}]: ").strip().strip('"')
    if not dest_path:
        dest_path = default_dest

    selection = key_selection_menu()
    if selection is None:
        return

    key_number, key = selection

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        progress_bar(message=f"{action.capitalize()}ing file content...", total=6, step_delay=0.03)

        cipher = MonoalphabeticCipher(content, key, preserve_formatting=True)
        result = cipher.encrypt() if action == "encrypt" else cipher.decrypt()

        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(result)

        console.print(
            Panel(
                f"[bold green]Operation complete![/bold green]\n"
                f"Source: [cyan]{source_path}[/cyan]\n"
                f"Destination: [cyan]{dest_path}[/cyan]\n"
                f"Key Used: [yellow]Key #{key_number}[/yellow]",
                title="File Cryptography Result",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[bold red]An error occurred during file processing: {e}[/bold red]")

    prompt_delay()
    clear_screen()


def show_available_keys() -> None:
    """Displays all available keys from the key store."""
    clear_screen()
    show_all_keys()
    prompt_delay()
    clear_screen()


menu_options: list[Menu] = []