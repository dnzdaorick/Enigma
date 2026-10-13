from rich.console import Console
from utilities_module import (
    delay_and_clear_screen,
    clear_screen,
    progress_bar,
    prompt_delay,
)
from key_module import show_all_keys, select_key
from monoalphabetic_cipher import MonoalphabeticCipher

console = Console()


class Menu:
    """A class to represent a menu option."""

    def __init__(self, menu_code: str, menu_name: str, style: str):
        self.menu_code = menu_code
        self.menu_name = menu_name
        self.style = style

    def __str__(self):
        return f"[{self.menu_code}] - {self.menu_name}"

    def add_option(self):
        """Adds the menu option to the list of menu options."""
        menu_options.append(self)

    @staticmethod
    def show_all_options():
        """Displays all the menu options."""
        for menu_option in menu_options:
            console.print(menu_option, style=menu_option.style)

    @staticmethod
    def get_user_code() -> str:
        """Gets the user's input for the menu option code."""
        user_code: str = input(
            "Enter the code of the option you want to select: "
        ).upper()

        verified_user_code: str = Menu.verify_user_code(user_code)

        if verified_user_code == "code not found":
            console.print(
                "Code not found! Please enter a valid code.", style="bold red"
            )
            delay_and_clear_screen()
        return verified_user_code

    @staticmethod
    def verify_user_code(user_code: str) -> str:
        """Verifies the user's input for the menu option code."""
        for option in menu_options:
            if user_code == option.menu_code:
                return user_code
        return "code not found"


def encrypt_menu() -> None:
    """Displays the encryption menu."""
    clear_screen()
    message: str = input("Enter the message to encrypt: ")
    perform_cipher_operation(message, "encrypt")
    return


def decrypt_menu() -> None:
    """Displays the decryption menu."""
    clear_screen()
    encrypted_message: str = input("Enter the encrypted message to decrypt: ")
    perform_cipher_operation(encrypted_message, "decrypt")
    return


def perform_cipher_operation(message: str, operation: str) -> None:
    """Performs the cipher operation (encrypt or decrypt) on the given message."""
    key_number, key = key_selection_menu()
    if key is None:
        return None

    progress_bar()
    console.print()

    if operation == "encrypt":
        encryption: MonoalphabeticCipher = MonoalphabeticCipher(message, key)
        encryption_result: str = encryption.encrypt()
        encryption.save_encryption_to_file(key_number, encryption_result)
    elif operation == "decrypt":
        decryption_cipher: MonoalphabeticCipher = MonoalphabeticCipher(message, key)
        decryption_result: str = decryption_cipher.decrypt()
        decryption_cipher.save_decryption_to_file(key_number, decryption_result)

    console.print(f"\n{operation.capitalize()} saved to file!", style="bold green")
    prompt_delay()
    clear_screen()
    return


def save_message_to_file(message: str, operation: str) -> None:
    """Saves the message to a file."""
    file_name = f"{operation.lower()}_message.txt"
    with open(file_name, "w") as file:
        file.write(message)
    """Displays the decryption menu."""
    clear_screen()

    encrypted_message: str = input("Enter the encrypted message to decrypt: ")

    key = key_selection_menu()
    if key == None:
        return None

    progress_bar()
    console.print()

    decrypt_message = MonoalphabeticCipher.decrypt(encrypted_message, key)
    decrypt_message.save_decryption_to_file(encrypted_message)
    console.print("\nDecryption saved to file!", style="bold green")
    prompt_delay()
    clear_screen()


def key_selection_menu() -> str | None:
    """Displays the key selection menu."""
    show_all_keys()
    select_key_number: str = input("Enter the key number: ")
    key_number, selected_key = select_key(select_key_number)
    if selected_key == None:
        return None
    return key_number, selected_key


def show_available_keys() -> None:
    """Displays all the available keys."""
    clear_screen()
    show_all_keys()
    prompt_delay()
    clear_screen()

menu_options: list[Menu] = []