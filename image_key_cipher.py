"""Image Key Cipher module.

Converts any image file into a cryptographic code and deterministic key
that substitutes lowercase and uppercase alphabet, numbers, and symbols.
"""

import hashlib
import os
import random
import string
import struct
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# Complete printable character set:
# - Lowercase letters (a-z: 26)
# - Uppercase letters (A-Z: 26)
# - Numbers (0-9: 10)
# - Symbols & punctuation (32 symbols + space = 33)
# Total: 95 distinct printable characters
ALPHABET_LOWER: str = string.ascii_lowercase
ALPHABET_UPPER: str = string.ascii_uppercase
NUMBERS: str = string.digits
SYMBOLS: str = string.punctuation + " "
FULL_CHARSET: list[str] = list(ALPHABET_LOWER + ALPHABET_UPPER + NUMBERS + SYMBOLS)


def read_image_bytes(image_path: str) -> bytes:
    """Reads raw binary content of an image file.
    
    Supports any image format (PNG, JPG, BMP, WEBP, GIF, etc.).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    with open(image_path, "rb") as img_file:
        return img_file.read()


def image_to_code(image_bytes: bytes) -> dict[str, str]:
    """Converts image binary data into cryptographic codes and fingerprints."""
    sha256_hash = hashlib.sha256(image_bytes).hexdigest()
    sha512_hash = hashlib.sha512(image_bytes).hexdigest()
    short_code = sha256_hash[:16].upper()
    return {
        "sha256": sha256_hash,
        "sha512": sha512_hash,
        "short_code": short_code,
        "byte_size": str(len(image_bytes)),
    }


def generate_key_from_image(image_bytes: bytes) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Derives a deterministic substitution key and inverse key from image bytes.
    
    Returns:
        (substitution_key, inverse_key, code_info)
    """
    code_info = image_to_code(image_bytes)
    # Convert SHA-256 digest into an integer seed
    seed_int = int.from_bytes(hashlib.sha256(image_bytes).digest(), "big")
    
    rng = random.Random(seed_int)
    shuffled_charset = FULL_CHARSET.copy()
    rng.shuffle(shuffled_charset)

    # 1-to-1 bijective mapping for all 95 characters
    substitution_key = {
        orig: subst for orig, subst in zip(FULL_CHARSET, shuffled_charset)
    }
    inverse_key = {
        subst: orig for orig, subst in substitution_key.items()
    }

    return substitution_key, inverse_key, code_info


def create_sample_bmp_image(output_path: str, width: int = 128, height: int = 128) -> str:
    """Generates a valid 24-bit uncompressed BMP image using pure Python standard library.
    
    Creates a colorful geometric cryptographic pattern.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    row_bytes_unpadded = width * 3
    padding_bytes = (4 - (row_bytes_unpadded % 4)) % 4
    row_size = row_bytes_unpadded + padding_bytes
    image_size = row_size * height
    file_size = 54 + image_size

    # BMP File Header (14 bytes)
    file_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54)
    # DIB Header / BITMAPINFOHEADER (40 bytes)
    dib_header = struct.pack(
        "<IiiHHIIiiII",
        40, width, height, 1, 24, 0, image_size, 2835, 2835, 0, 0
    )

    pixel_data = bytearray()
    seed_color_r = random.randint(30, 200)
    seed_color_g = random.randint(30, 200)
    seed_color_b = random.randint(30, 200)

    for y in range(height):
        row = bytearray()
        for x in range(width):
            # Rich colorful generative pattern
            b = (x * 7 + seed_color_b + (x ^ y)) % 256
            g = (y * 5 + seed_color_g + (x * y // 8)) % 256
            r = ((x + y) * 3 + seed_color_r) % 256
            row.extend([b, g, r])
        row.extend(b"\x00" * padding_bytes)
        pixel_data.extend(row)

    with open(output_path, "wb") as bmp_file:
        bmp_file.write(file_header)
        bmp_file.write(dib_header)
        bmp_file.write(pixel_data)

    return output_path


class ImageKeyCipher:
    """Encrypts and decrypts messages using an image-derived substitution key.
    
    Substitutes all letters (a-z, A-Z), numbers (0-9), and symbols (punctuation + space).
    """

    def __init__(
        self,
        message: str,
        key: dict[str, str],
        image_code: str = "",
        image_path: str = "",
        show_ui: bool = True,
    ):
        self.message = message
        self.key = key
        self.image_code = image_code
        self.image_path = image_path
        self.show_ui = show_ui
        # Precompute the inverse mapping for instantaneous O(1) decryption
        self.inverse_key: dict[str, str] = {v: k for k, v in self.key.items()}

    def encrypt(self) -> str:
        """Encrypts the message by substituting every character in the key.
        
        Characters not present in the 95-character set (e.g. newline, tab) are preserved.
        """
        encrypted_chars = [self.key.get(char, char) for char in self.message]
        encrypted_text = "".join(encrypted_chars)

        if self.show_ui:
            self._display_results("Encryption", self.message, encrypted_text)
        return encrypted_text

    def decrypt(self) -> str:
        """Decrypts the message using the inverse key in O(1) time per character."""
        decrypted_chars = [self.inverse_key.get(char, char) for char in self.message]
        decrypted_text = "".join(decrypted_chars)

        if self.show_ui:
            self._display_results("Decryption", self.message, decrypted_text)
        return decrypted_text

    def _display_results(self, operation: str, input_text: str, result_text: str) -> None:
        """Renders styled output cards with cryptographic code and substitution samples."""
        # Sample previews from each character category
        letters_sample = [c for c in ALPHABET_LOWER[:6]]
        numbers_sample = [c for c in NUMBERS[:6]]
        symbols_sample = ["!", "@", "#", "$", "%", "&"]

        table = Table(
            title=f"{operation} Mapping Sample Preview",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
        )
        table.add_column("Category", style="magenta", justify="left")
        table.add_column("Original Characters", style="green", justify="center")
        table.add_column("→", style="dim", justify="center")
        table.add_column("Mapped Characters", style="yellow", justify="center")

        table.add_row(
            "Alphabet",
            " ".join(letters_sample),
            "→",
            " ".join(self.key.get(c, "?") for c in letters_sample),
        )
        table.add_row(
            "Numbers",
            " ".join(numbers_sample),
            "→",
            " ".join(self.key.get(c, "?") for c in numbers_sample),
        )
        table.add_row(
            "Symbols",
            " ".join(symbols_sample),
            "→",
            " ".join(self.key.get(c, "?") for c in symbols_sample),
        )

        code_display = self.image_code if self.image_code else "Derived from Image"
        image_display = os.path.basename(self.image_path) if self.image_path else "Active Key"

        content = (
            f"[bold cyan]Input:[/bold cyan] {input_text}\n"
            f"[bold green]Result:[/bold green] {result_text}\n\n"
            f"[bold magenta]Key Image:[/bold magenta] {image_display}\n"
            f"[bold yellow]Image Code (SHA-256):[/bold yellow] [dim]{code_display}[/dim]\n"
        )
        console.print(
            Panel(
                content,
                title=f"[bold white]{operation.upper()} RESULT (IMAGE KEY CIPHER)[/bold white]",
                border_style="bright_blue",
            )
        )
        console.print(table)

    def save_encryption_to_file(self, key_identifier: str, encrypted_message: str) -> None:
        """Saves the encryption log to Encryption.txt."""
        self._save_to_file("Encryption", key_identifier, encrypted_message)

    def save_decryption_to_file(self, key_identifier: str, decrypted_message: str) -> None:
        """Saves the decryption log to Decryption.txt."""
        self._save_to_file("Decryption", key_identifier, decrypted_message)

    def _save_to_file(self, mode: str, key_identifier: str, result: str) -> None:
        """Appends the formatted cryptographic operation log to a text file."""
        file_path = f"{mode}.txt"
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(
                f"{'-' * 120}\n"
                f"{datetime.now():%A, %B %d %Y at %I:%M %p}\n\n"
                f"Cipher Engine: Image Key Cipher (Alphabet + Numbers + Symbols)\n"
                f"Original Message: {self.message}\n"
                f"Key Identifier: {key_identifier}\n"
                f"Image Code (SHA-256): {self.image_code or 'N/A'}\n"
                f"Image Path: {self.image_path or 'N/A'}\n\n"
                f"{mode} Result: {result}\n"
                f"{'-' * 120}\n"
            )
