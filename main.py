import sys
import utilities_module
from rich.console import Console
from menu_module import Menu, menu_options, encrypt_menu, decrypt_menu, show_available_keys
from key_module import generate_key


def main_menu() -> None:
    """Displays the main menu and processes the user's input."""

    def process_option(selected_option: str, menu_options: list[Menu]):
        """Processes the user's input for the menu option code."""
        if selected_option == menu_options[0].menu_code:
            utilities_module.clear_screen()
            utilities_module.progress_bar()
            encrypt_menu()
        if selected_option == menu_options[1].menu_code:
            utilities_module.clear_screen()
            utilities_module.progress_bar()
            decrypt_menu()
        if selected_option == menu_options[2].menu_code:
            utilities_module.clear_screen()
            utilities_module.progress_bar()
            generate_key()
        if selected_option == menu_options[3].menu_code:
            utilities_module.clear_screen()
            utilities_module.progress_bar()
            show_available_keys()
        if selected_option == menu_options[4].menu_code:
            console.print(
                "Thank you for using the program! Goodbye!", style="bold yellow"
            )
            sys.exit()

    while True:
        console.print(f"{'ENIGMA MACHINE':^15}", style="bold white")
        Menu.show_all_options()
        user_code: str = Menu.get_user_code()
        verified_user_code: str = Menu.verify_user_code(user_code)

        process_option(verified_user_code, menu_options)


def main() -> None:
    """The main function."""
    option1: Menu = Menu("A", "Encrypt Message", "bold green").add_option()
    option2: Menu = Menu("B", "Decrypt Message", "bold yellow").add_option()
    option3: Menu = Menu("C", "Generate Key", "bold blue").add_option()
    option4: Menu = Menu("D", "Show Available Keys", "bold magenta").add_option()
    option5: Menu = Menu("X", "Exit", "bold red").add_option()

    main_menu()


if __name__ == "__main__":
    console = Console()
    main()
