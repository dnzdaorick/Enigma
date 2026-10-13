from datetime import datetime
from rich.console import Console

console = Console()


class MonoalphabeticCipher:
    """Encrypts and decrypts a message using the monoalphabetic cipher."""

    def __init__(self, message: str, key: dict[str, str]):
        self.message = message
        self.key = key

    def encrypt(self) -> str:
        """Encrypts the message using the key."""
        message = list("".join(self.message.split()))

        for letter in range(len(message)):
            selected_letter = message[letter]
            message[letter] = self.key[selected_letter]
        encrypted_text = "".join(message)
        console.print(f"Message: {self.message}", style="bold white")
        console.print(f"Original Text: {' '.join(self.key.keys())}", style="blue")
        console.print(f"Replaced With: {' '.join(self.key.values())}", style="yellow")
        console.print(f"Encrypted Message: {encrypted_text}", style="bold white")
        return encrypted_text

    def decrypt(self) -> str:
        """Decrypts the message using the key."""
        encrypted_message = list("".join(self.message.split()))
        string_encrypted_message = "".join(encrypted_message)

        for letter in range(len(encrypted_message)):
            selected_letter = encrypted_message[letter]
            encrypted_message[letter] = list(self.key.keys())[
                list(self.key.values()).index(selected_letter)
            ]
        decrypted_message = "".join(encrypted_message)

        console.print(
            f"Encrypted Message: {string_encrypted_message}", style="bold white"
        )
        console.print(f"Original Text: {' '.join(self.key.keys())}", style="blue")
        console.print(f"Replaced Text: {' '.join(self.key.values())}", style="yellow")
        console.print(f"Decrypted Message: {decrypted_message}", style="bold white")
        return decrypted_message

    def save_encryption_to_file(self, key_number: str, encrypted_message: str) -> None:
        """Saves the encryption to a file."""
        self._save_to_file("Encryption", key_number, encrypted_message)

    def save_decryption_to_file(self, key_number: str, decrypted_message: str) -> None:
        """Saves the decryption to a file."""
        self._save_to_file("Decryption", key_number, decrypted_message)

    def _save_to_file(self, mode: str, key_number: str, result: str) -> None:
        """Saves the encryption/decryption to a file."""
        with open(f"{mode}.txt", "a") as file:
            file.write(
                f"{'-' * 120}\n"
                f"{datetime.now():%A, %B %d %Y at %I:%M %p}\n\n"
                f"Message: {self.message}\n"
                f"Key Number: {key_number}\n\n"
                f"Original Text: {' '.join(self.key.keys())}\n"
                f"Replaced With: {' '.join(self.key.values())}\n\n"
                f"{mode} Message: {result}\n"
                f"{'-' * 120}\n"
            )
