"""Media Cipher module for Enigma Machine.

Supports converting Image files (PNG, JPG, BMP, etc.) and Music/Audio files (MP3, WAV, OGG, FLAC, etc.)
into cryptographic code fingerprints and deterministic keys that substitute lowercase & uppercase
alphabet, numbers, and symbols. Supports multi-key cascade encryption combining 1, 2, or more keys.
"""

import hashlib
import math
import os
import random
import string
import struct
import wave
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# Complete printable character set (95 characters)
ALPHABET_LOWER: str = string.ascii_lowercase
ALPHABET_UPPER: str = string.ascii_uppercase
NUMBERS: str = string.digits
SYMBOLS: str = string.punctuation + " "
FULL_CHARSET: list[str] = list(ALPHABET_LOWER + ALPHABET_UPPER + NUMBERS + SYMBOLS)

# Recognized media extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".tiff", ".ico", ".svg"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff"}


def detect_media_type(file_path: str) -> str:
    """Detects whether a file is an image, music/audio, or general media based on extension."""
    ext = os.path.splitext(file_path.lower())[1]
    if ext in IMAGE_EXTENSIONS:
        return "image"
    elif ext in AUDIO_EXTENSIONS:
        return "music"
    return "media"


def read_media_bytes(file_path: str) -> bytes:
    """Reads raw binary content of any media file (image, music, etc.)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Media file not found: {file_path}")
    with open(file_path, "rb") as media_file:
        return media_file.read()


def media_to_code(media_bytes: bytes, file_path: str = "") -> dict[str, str]:
    """Converts media binary data into cryptographic codes and fingerprints."""
    sha256_hash = hashlib.sha256(media_bytes).hexdigest()
    sha512_hash = hashlib.sha512(media_bytes).hexdigest()
    short_code = sha256_hash[:16].upper()
    media_type = detect_media_type(file_path) if file_path else "media"
    return {
        "sha256": sha256_hash,
        "sha512": sha512_hash,
        "short_code": short_code,
        "byte_size": str(len(media_bytes)),
        "media_type": media_type,
    }


def generate_key_from_bytes(
    media_bytes: bytes, file_path: str = ""
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Derives a deterministic substitution key and inverse key from media bytes.
    
    Returns:
        (substitution_key, inverse_key, code_info)
    """
    code_info = media_to_code(media_bytes, file_path)
    seed_int = int.from_bytes(hashlib.sha256(media_bytes).digest(), "big")
    
    rng = random.Random(seed_int)
    shuffled_charset = FULL_CHARSET.copy()
    rng.shuffle(shuffled_charset)

    substitution_key = {
        orig: subst for orig, subst in zip(FULL_CHARSET, shuffled_charset)
    }
    inverse_key = {
        subst: orig for orig, subst in substitution_key.items()
    }

    return substitution_key, inverse_key, code_info


# Backward-compatible alias
generate_key_from_image = generate_key_from_bytes
read_image_bytes = read_media_bytes
image_to_code = media_to_code


def create_sample_bmp_image(output_path: str, width: int = 128, height: int = 128) -> str:
    """Generates a valid 24-bit uncompressed BMP image using pure Python standard library."""
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


def create_sample_wav_music(output_path: str, duration_sec: float = 2.0) -> str:
    """Generates a valid 16-bit 44.1kHz musical audio .wav file using pure Python standard library.
    
    Creates a harmonious melodic arpeggio synthesized with mathematical sine waves.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    sample_rate = 44100
    # Harmonious musical notes (C4, E4, G4, B4, C5, G4, E4, C4)
    notes = [261.63, 329.63, 392.00, 493.88, 523.25, 392.00, 329.63, 261.63]
    samples_per_note = int(sample_rate * (duration_sec / len(notes)))

    pcm_data = bytearray()
    for note_idx, freq in enumerate(notes):
        for i in range(samples_per_note):
            t = i / sample_rate
            # Smooth attack and decay envelope to prevent audio clicking
            env = min(1.0, i / 800.0) * min(1.0, (samples_per_note - i) / 800.0)
            # Fundamental frequency + 1st harmonic for rich timbre
            sample_val = int(
                16000 * env * (0.75 * math.sin(2 * math.pi * freq * t) + 0.25 * math.sin(4 * math.pi * freq * t))
            )
            pcm_data.extend(struct.pack("<h", sample_val))

    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)

    return output_path


class MultiKeyCipher:
    """Multi-layer cryptographic cipher executing sequential rotor-style cascade encryption.
    
    Combines 1, 2, or more keys (Image keys, Music keys, or mixed combinations)
    to encrypt or decrypt messages and files across all 95 characters.
    """

    def __init__(
        self,
        message: str,
        key_layers: list[tuple[str, dict[str, str], dict[str, str]]],
        show_ui: bool = True,
    ):
        """
        Args:
            message: Plaintext or ciphertext string.
            key_layers: List of (key_identifier, key_mapping, metadata_dict).
            show_ui: Whether to render Rich terminal output.
        """
        self.message = message
        self.key_layers = key_layers
        self.show_ui = show_ui

    def encrypt(self) -> str:
        """Encrypts message through all key layers sequentially (Layer 1 -> Layer 2 -> ... -> Layer N)."""
        current_text = self.message
        layer_logs: list[dict[str, str]] = []

        for idx, (key_id, mapping, meta) in enumerate(self.key_layers, start=1):
            substituted = "".join(mapping.get(char, char) for char in current_text)
            layer_logs.append({
                "layer": str(idx),
                "key_id": key_id,
                "media_type": meta.get("media_type", "media"),
                "file_path": meta.get("image_path", meta.get("file_path", "N/A")),
                "code": meta.get("image_code", meta.get("code", "N/A")),
                "intermediate": substituted,
            })
            current_text = substituted

        if self.show_ui:
            self._display_results("Encryption", self.message, current_text, layer_logs)

        return current_text

    def decrypt(self) -> str:
        """Decrypts message through all key layers in reverse order (Layer N -> ... -> Layer 2 -> Layer 1)."""
        current_text = self.message
        layer_logs: list[dict[str, str]] = []

        # Reverse key layers for decryption cascade
        reversed_layers = list(reversed(self.key_layers))
        total_layers = len(reversed_layers)

        for step_idx, (key_id, mapping, meta) in enumerate(reversed_layers, start=1):
            layer_num = total_layers - step_idx + 1
            # Precompute inverse mapping
            inverse_map = {v: k for k, v in mapping.items()}
            restored = "".join(inverse_map.get(char, char) for char in current_text)
            layer_logs.append({
                "step": str(step_idx),
                "layer_unwound": str(layer_num),
                "key_id": key_id,
                "media_type": meta.get("media_type", "media"),
                "file_path": meta.get("image_path", meta.get("file_path", "N/A")),
                "code": meta.get("image_code", meta.get("code", "N/A")),
                "intermediate": restored,
            })
            current_text = restored

        if self.show_ui:
            self._display_results("Decryption", self.message, current_text, layer_logs)

        return current_text

    def _display_results(
        self, operation: str, input_text: str, result_text: str, layer_logs: list[dict[str, str]]
    ) -> None:
        """Renders styled pipeline cards and mapping details."""
        num_keys = len(self.key_layers)

        content = (
            f"[bold cyan]Input:[/bold cyan]  {input_text}\n"
            f"[bold green]Result:[/bold green] {result_text}\n"
        )

        pipeline_table = Table(
            title=f"Pipeline ({num_keys} Key{'s' if num_keys > 1 else ''})",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
        )
        pipeline_table.add_column("Stage", style="bold yellow", justify="center", width=7)
        pipeline_table.add_column("Key #", style="bold white", justify="center", width=8)
        pipeline_table.add_column("Type", style="cyan", justify="center", width=10)
        pipeline_table.add_column("Source File", style="green", justify="left")
        pipeline_table.add_column("SHA-256 Code", style="dim", justify="left")

        for log in layer_logs:
            m_type = log["media_type"].lower()
            icon = "🖼️ Image" if m_type == "image" else ("🎵 Music" if m_type == "music" else "📁 Media")
            code_preview = log["code"][:16] + "..." if len(log["code"]) > 16 else log["code"]
            stage_label = f"L{log.get('layer', log.get('layer_unwound', '?'))}"
            pipeline_table.add_row(
                stage_label,
                str(log["key_id"]),
                icon,
                os.path.basename(log["file_path"]),
                code_preview,
            )

        console.print(
            Panel(
                content,
                title=f"[bold white]{operation.upper()} RESULT[/bold white]",
                border_style="bright_blue",
            )
        )
        console.print(pipeline_table)

    def save_encryption_to_file(self, key_identifiers: str, encrypted_message: str) -> None:
        """Saves multi-key encryption log to Encryption.txt."""
        self._save_to_file("Encryption", key_identifiers, encrypted_message)

    def save_decryption_to_file(self, key_identifiers: str, decrypted_message: str) -> None:
        """Saves multi-key decryption log to Decryption.txt."""
        self._save_to_file("Decryption", key_identifiers, decrypted_message)

    def _save_to_file(self, mode: str, key_identifiers: str, result: str) -> None:
        """Appends formatted multi-key audit log to text file."""
        file_path = f"{mode}.txt"
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(
                f"{'-' * 120}\n"
                f"{datetime.now():%A, %B %d %Y at %I:%M %p}\n\n"
                f"Cipher Engine: Multi-Key Media Cipher ({len(self.key_layers)} Layer(s))\n"
                f"Original Message: {self.message}\n"
                f"Key Combination: {key_identifiers}\n"
            )
            for idx, (k_id, _, meta) in enumerate(self.key_layers, start=1):
                m_type = meta.get("media_type", "media").upper()
                file.write(
                    f"  [Layer {idx}] Key #{k_id} ({m_type}) | File: {meta.get('image_path', meta.get('file_path', 'N/A'))} | SHA-256: {meta.get('image_code', 'N/A')}\n"
                )
            file.write(f"\n{mode} Result: {result}\n{'-' * 120}\n\n")


class ImageKeyCipher(MultiKeyCipher):
    """Convenience single-key cipher wrapper maintaining backward compatibility."""

    def __init__(
        self,
        message: str,
        key: dict[str, str],
        image_code: str = "",
        image_path: str = "",
        show_ui: bool = True,
    ):
        meta = {
            "image_path": image_path,
            "image_code": image_code,
            "media_type": detect_media_type(image_path) if image_path else "image",
        }
        super().__init__(
            message=message,
            key_layers=[("1", key, meta)],
            show_ui=show_ui,
        )
        self.key = key
        self.image_code = image_code
        self.image_path = image_path
        self.inverse_key = {v: k for k, v in key.items()}
