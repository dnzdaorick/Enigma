"""Menu module for Image Key Cipher operations.

Provides interactive command-line interfaces for message encryption, decryption,
file cryptography, and image key management.
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
    generate_key,
    inspect_key,
    delete_key,
    register_image_file,
    get_key_meta,
    keys,
    keys_metadata,
)
from image_key_cipher import (
    ImageKeyCipher,
    read_image_bytes,
    generate_key_from_image,
)

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


def key_selection_menu() -> tuple[str, dict[str, str], dict[str, str]] | None:
    """Prompts the user to select an existing key ID or provide an image file directly.
    
    Returns:
        (key_identifier, key_mapping, metadata_dict) or None
    """
    if not keys:
        console.print(
            Panel(
                "[bold yellow]No image keys registered yet![/bold yellow]\n"
                "You can generate a sample key image now or specify an image file path.",
                border_style="yellow",
                title="Notice",
            )
        )
        choice = Prompt.ask(
            "Choose an option: [G]enerate sample key image, [L]oad existing image, [C]ancel",
            choices=["g", "l", "c"],
            default="g",
        ).lower()

        if choice == "g":
            generate_key()
            return key_selection_menu()
        elif choice == "l":
            img_path = input("Enter path to image file: ").strip().strip('"').strip("'")
            if not img_path:
                return None
            reg_res = register_image_file(img_path)
            if reg_res:
                key_id, mapping = reg_res
                return key_id, mapping, get_key_meta(key_id)
            return None
        else:
            return None

    show_all_keys()
    console.print(
        "\n[dim]Tip: Enter a Key # (e.g. 1), or directly type an image path (e.g. photo.png), or 'c' to cancel.[/dim]"
    )
    user_input = input("Enter Key Number or Image Path: ").strip().strip('"').strip("'")

    if user_input.lower() in ("c", "cancel", "q", "quit", ""):
        console.print("[dim]Operation cancelled.[/dim]")
        prompt_delay()
        return None

    # Check if entered as an existing key ID
    if user_input in keys:
        selection = select_key(user_input)
        if selection is None:
            prompt_delay()
            return None
        key_id, mapping = selection
        return key_id, mapping, get_key_meta(key_id)

    # Check if entered as an image file on disk
    if os.path.exists(user_input):
        try:
            img_bytes = read_image_bytes(user_input)
            mapping, _, code_info = generate_key_from_image(img_bytes)
            console.print(f"[bold green]Successfully derived key from '{os.path.basename(user_input)}'![/bold green]")
            save_prompt = Prompt.ask("Register this image into key store for future use? (y/n)", default="y")
            if save_prompt.lower() == "y":
                reg = register_image_file(user_input, interactive=False)
                key_id = reg[0] if reg else "Custom Image"
            else:
                key_id = f"Direct Image ({os.path.basename(user_input)})"

            meta = {
                "image_path": user_input,
                "image_code": code_info["sha256"],
                "byte_size": code_info["byte_size"],
            }
            return key_id, mapping, meta
        except Exception as e:
            console.print(f"[bold red]Failed to process image file: {e}[/bold red]")
            prompt_delay()
            return None

    console.print(f"[bold red]Key #{user_input} not found and file '{user_input}' does not exist![/bold red]")
    prompt_delay()
    return None


def encrypt_menu() -> None:
    """Displays the interactive message encryption interface."""
    display_header("Message Encryption", "Image Key Cipher (Alphabet + Numbers + Symbols)")
    message = input("Enter the message to encrypt: ")
    if not message:
        console.print("[yellow]Empty message entered. Returning to menu.[/yellow]")
        prompt_delay()
        return

    perform_cipher_operation(message, "encrypt")


def decrypt_menu() -> None:
    """Displays the interactive message decryption interface."""
    display_header("Message Decryption", "Image Key Cipher (Alphabet + Numbers + Symbols)")
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

    key_identifier, key, meta = selection

    progress_bar(message=f"{operation.capitalize()}ing with Image Key...", total=5, step_delay=0.03)
    console.print()

    cipher = ImageKeyCipher(
        message=message,
        key=key,
        image_code=meta.get("image_code", ""),
        image_path=meta.get("image_path", ""),
        show_ui=True,
    )
    if operation == "encrypt":
        result = cipher.encrypt()
        cipher.save_encryption_to_file(key_identifier, result)
    else:
        result = cipher.decrypt()
        cipher.save_decryption_to_file(key_identifier, result)

    console.print(f"\n[bold green]{operation.capitalize()} result logged to {operation.capitalize()}.txt![/bold green]")
    prompt_delay()
    clear_screen()


def load_or_generate_image_key_menu() -> None:
    """Interface to either load an existing image file or generate a new sample key image."""
    while True:
        display_header("Load / Generate Image Key", "Create cryptographic substitution keys from images")
        console.print("[1] Generate New Sample Key Image (.bmp)", style="bold cyan")
        console.print("[2] Load & Register Existing Image File (PNG, JPG, BMP, etc.)", style="bold yellow")
        console.print("[3] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask("Choose an action", choices=["1", "2", "3"], default="1")

        if choice == "1":
            clear_screen()
            generate_key(interactive=True)
            break
        elif choice == "2":
            clear_screen()
            image_path = input("Enter path to image file: ").strip().strip('"').strip("'")
            if image_path:
                register_image_file(image_path, interactive=True)
            break
        elif choice == "3":
            clear_screen()
            break


def key_management_menu() -> None:
    """Sub-menu for image key inspection, table overview, and deletion."""
    while True:
        display_header("Key Management & Inspector", "View, inspect, or manage image-based keys")
        console.print("[1] Show All Keys Overview", style="bold cyan")
        console.print("[2] Inspect Detailed Character Mapping & Image Code", style="bold yellow")
        console.print("[3] Load & Register Image File", style="bold green")
        console.print("[4] Generate Sample Key Image (.bmp)", style="bold blue")
        console.print("[5] Delete an Image Key", style="bold red")
        console.print("[6] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask("Choose an action", choices=["1", "2", "3", "4", "5", "6"], default="1")

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
            img_path = input("Enter path to image file: ").strip().strip('"').strip("'")
            if img_path:
                register_image_file(img_path, interactive=True)
        elif choice == "4":
            clear_screen()
            generate_key(interactive=True)
        elif choice == "5":
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
        elif choice == "6":
            clear_screen()
            break


def file_cipher_menu() -> None:
    """Encrypts or decrypts text files on disk using Image Key Cipher."""
    display_header("File Cryptography", "Encrypt or decrypt text documents with Image Key")
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
    if selection is None:
        return

    key_identifier, key, meta = selection

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        progress_bar(message=f"{action.capitalize()}ing file content with Image Key...", total=6, step_delay=0.03)

        cipher = ImageKeyCipher(
            message=content,
            key=key,
            image_code=meta.get("image_code", ""),
            image_path=meta.get("image_path", ""),
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
                f"Key Used: [yellow]{key_identifier}[/yellow]\n"
                f"Image Code (SHA-256): [dim]{meta.get('image_code', 'N/A')[:24]}...[/dim]",
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