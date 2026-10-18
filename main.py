import sys
import utilities_module
from rich.console import Console
from rich.panel import Panel
from menu_module import (
    Menu,
    menu_options,
    encrypt_menu,
    decrypt_menu,
    generate_media_key_menu,
    key_management_menu,
    file_cipher_menu,
)

console = Console()

ACTION_DISPATCH = {
    "A": encrypt_menu,
    "B": decrypt_menu,
    "C": generate_media_key_menu,
    "D": key_management_menu,
    "E": file_cipher_menu,
}


def main_menu() -> None:
    """Displays the main menu and processes the user's input."""

    def process_option(selected_code: str) -> None:
        """Dispatches verified menu option code to corresponding action."""
        if selected_code == "X":
            console.print(
                Panel(
                    "[bold yellow]Thank you for using Enigma! Goodbye![/bold yellow]",
                    border_style="yellow",
                )
            )
            sys.exit(0)

        action = ACTION_DISPATCH.get(selected_code)
        if action:
            utilities_module.clear_screen()
            action()

    while True:
        try:
            utilities_module.display_header(
                "ENIGMA",
                "Cryptographic Media Engine",
            )
            Menu.show_all_options()
            console.print()
            user_code: str = Menu.get_user_code()
            if user_code != "code not found":
                process_option(user_code)
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Session interrupted. Exiting cleanly...[/bold yellow]")
            sys.exit(0)


def main() -> None:
    """Initializes menu options and launches the main application loop."""
    Menu("A", "Encrypt Message", "bold green").add_option()
    Menu("B", "Decrypt Message", "bold yellow").add_option()
    Menu("C", "Generate Media Key", "bold blue").add_option()
    Menu("D", "Manage & Inspect Keys", "bold magenta").add_option()
    Menu("E", "File Cryptography (.txt)", "bold cyan").add_option()
    Menu("X", "Exit Program", "bold red").add_option()

    main_menu()


if __name__ == "__main__":
    main()
