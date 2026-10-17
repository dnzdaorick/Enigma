from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class MonoalphabeticCipher:
    """Encrypts and decrypts messages using a monoalphabetic substitution cipher."""

    def __init__(self, message: str, key: dict[str, str], preserve_formatting: bool = True, show_ui: bool = True):
        self.message = message
        self.key = key
        self.preserve_formatting = preserve_formatting
        self.show_ui = show_ui
        # Precompute the inverse mapping for instantaneous O(1) decryption lookups
        self.inverse_key: dict[str, str] = {v: k for k, v in self.key.items()}

    def encrypt(self) -> str:
        """Encrypts the message using the key.
        
        Substitutes alphabetic characters present in the key. Non-alphabetic
        characters (spaces, punctuation, digits) are preserved if preserve_formatting
        is enabled, preventing runtime KeyErrors.
        """
        source_text = self.message if self.preserve_formatting else "".join(self.message.split())
        encrypted_chars = [self.key.get(char, char) for char in source_text]
        encrypted_text = "".join(encrypted_chars)

        if self.show_ui:
            self._display_results("Encryption", self.message, encrypted_text)
        return encrypted_text

    def decrypt(self) -> str:
        """Decrypts the message using the inverse key in O(1) time per character."""
        source_text = self.message if self.preserve_formatting else "".join(self.message.split())
        decrypted_chars = [self.inverse_key.get(char, char) for char in source_text]
        decrypted_text = "".join(decrypted_chars)

        if self.show_ui:
            self._display_results("Decryption", self.message, decrypted_text)
        return decrypted_text

    def _display_results(self, operation: str, input_text: str, result_text: str) -> None:
        """Renders styled output cards with substitution previews."""
        sample_keys = list(self.key.keys())[:15]
        sample_vals = [self.key[k] for k in sample_keys]

        table = Table(title=f"{operation} Details", show_header=True, header_style="bold cyan")
        table.add_column("Original Character", style="green", justify="center")
        table.add_column("Mapped Character", style="yellow", justify="center")
        for orig, mapped in zip(sample_keys, sample_vals):
            table.add_row(orig, mapped)

        content = (
            f"[bold cyan]Input:[/bold cyan] {input_text}\n"
            f"[bold green]Result:[/bold green] {result_text}\n\n"
            f"[dim]Sample Mapping Preview (first 15 pairs):[/dim]\n"
            f"Plain:  {' '.join(sample_keys)}...\n"
            f"Cipher: {' '.join(sample_vals)}..."
        )
        console.print(Panel(content, title=f"[bold white]{operation.upper()} RESULT[/bold white]", border_style="bright_blue"))

    def save_encryption_to_file(self, key_number: str, encrypted_message: str) -> None:
        """Saves the encryption log to Encryption.txt."""
        self._save_to_file("Encryption", key_number, encrypted_message)

    def save_decryption_to_file(self, key_number: str, decrypted_message: str) -> None:
        """Saves the decryption log to Decryption.txt."""
        self._save_to_file("Decryption", key_number, decrypted_message)

    def _save_to_file(self, mode: str, key_number: str, result: str) -> None:
        """Appends the formatted cryptographic operation log to a text file."""
        file_path = f"{mode}.txt"
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(
                f"{'-' * 120}\n"
                f"{datetime.now():%A, %B %d %Y at %I:%M %p}\n\n"
                f"Original Message: {self.message}\n"
                f"Key Number: {key_number}\n\n"
                f"Original Alphabet: {' '.join(self.key.keys())}\n"
                f"Substitute Alphabet: {' '.join(self.key.values())}\n\n"
                f"{mode} Result: {result}\n"
                f"{'-' * 120}\n"
            )
