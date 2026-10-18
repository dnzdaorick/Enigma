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
    # 1. Compute SHA-256 (64 hex characters) as the primary unique file fingerprint
    sha256_hash = hashlib.sha256(media_bytes).hexdigest()
    # 2. Compute SHA-512 (128 hex characters) for extended verification
    sha512_hash = hashlib.sha512(media_bytes).hexdigest()
    # 3. Take the first 16 characters as a short display code for terminal UI & tables
    short_code = sha256_hash[:16].upper()
    # 4. Identify media type ('image', 'music', or 'media') based on file extension
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
    # 1. Get metadata and cryptographic hash fingerprint
    code_info = media_to_code(media_bytes, file_path)
    # 2. Convert 32-byte (256-bit) raw SHA-256 digest into an integer seed
    seed_int = int.from_bytes(hashlib.sha256(media_bytes).digest(), "big")
    
    # 3. Initialize an isolated random generator (same file always produces identical shuffle)
    rng = random.Random(seed_int)
    # 4. Deterministically shuffle all 95 printable ASCII characters
    shuffled_charset = FULL_CHARSET.copy()
    rng.shuffle(shuffled_charset)

    # 5. Build 1-to-1 encryption mapping: original char -> substitute char
    substitution_key = {
        orig: subst for orig, subst in zip(FULL_CHARSET, shuffled_charset)
    }
    # 6. Build reverse decryption mapping: substitute char -> original char (O(1) lookup)
    inverse_key = {
        subst: orig for orig, subst in substitution_key.items()
    }

    return substitution_key, inverse_key, code_info


# Backward-compatible aliases for legacy image-only calls
generate_key_from_image = generate_key_from_bytes
read_image_bytes = read_media_bytes
image_to_code = media_to_code

# Import classical ciphers from dedicated cipher_module
from cipher_module import (
    generate_monoalphabetic_key,
    generate_vigenere_key,
    generate_xor_key,
    vigenere_classical_encrypt,
    vigenere_classical_decrypt,
    vigenere_encrypt,
    vigenere_decrypt,
    xor_encrypt,
    xor_decrypt,
)


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
            cipher_type = meta.get("cipher_type", meta.get("media_type", "media")).lower()
            if cipher_type == "vigenere":
                key_val = meta.get("key_value", "")
                variant = meta.get("variant", "classical")
                substituted = vigenere_encrypt(current_text, key_val, variant)
            elif cipher_type == "xor":
                key_val = meta.get("key_value", "")
                substituted = xor_encrypt(current_text, key_val)
            else:
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

    def _unwind_cascade(
        self, layers: list[tuple[str, dict[str, str], dict[str, str]]]
    ) -> tuple[str, list[dict[str, str]], bool]:
        """Performs a single pass of unwinding through the given layer sequence."""
        current_text = self.message
        layer_logs: list[dict[str, str]] = []
        total_layers = len(layers)
        xor_hex_valid = True

        for step_idx, (key_id, mapping, meta) in enumerate(layers, start=1):
            layer_num = total_layers - step_idx + 1
            cipher_type = meta.get("cipher_type", meta.get("media_type", "media")).lower()
            if cipher_type == "vigenere":
                key_val = meta.get("key_value", "")
                variant = meta.get("variant", "classical")
                restored = vigenere_decrypt(current_text, key_val, variant)
            elif cipher_type == "xor":
                key_val = meta.get("key_value", "")
                try:
                    bytes.fromhex(current_text.strip())
                except (ValueError, TypeError):
                    xor_hex_valid = False
                restored = xor_decrypt(current_text, key_val)
            else:
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

        return current_text, layer_logs, xor_hex_valid

    @staticmethod
    def _score_candidate_plaintext(text: str, xor_hex_valid: bool) -> float:
        """Scores candidate decrypted text based on printable characters and language plausibility."""
        if not text:
            return -9999.0
        score = 100.0 if xor_hex_valid else -100.0
        common_bigrams = {
            "th", "he", "in", "er", "an", "re", "ed", "on", "es", "st",
            "en", "at", "to", "nt", "ha", "nd", "ou", "ea", "ng", "as",
            "or", "ti", "is", "et", "it", "ar", "te", "se", "hi", "of",
            "al", "le", "lo", "ow", "wo", "rl", "ld", "me", "sa", "ag",
            "ge", "ec", "cr", "et"
        }
        for c in text:
            if c in string.ascii_letters or c == " ":
                score += 2.0
            elif c in string.digits or c in ".,!?'\"-:;()[]{}":
                score += 1.0
            elif c in string.printable:
                score += 0.2
            else:
                score -= 30.0

        clean_text = "".join(c.lower() for c in text if c.isalpha())
        if len(clean_text) >= 2:
            bigram_matches = sum(
                1 for i in range(len(clean_text) - 1) if clean_text[i : i + 2] in common_bigrams
            )
            score += bigram_matches * 15.0

        return score

    @classmethod
    def determine_unwind_sequence(
        cls,
        key_layers: list[tuple[str, dict[str, str], dict[str, str]]],
        ciphertext: str,
    ) -> list[tuple[str, dict[str, str], dict[str, str]]]:
        """Determines the correct physical layer sequence to unwind during decryption.
        
        Seamlessly handles both:
        - User entered forward encryption sequence (1, 2, 3) -> returns [3, 2, 1]
        - User entered reverse unwinding sequence (3, 2, 1) -> returns [3, 2, 1]
        """
        if len(key_layers) <= 1:
            return list(key_layers)

        rev_layers = list(reversed(key_layers))
        fwd_layers = list(key_layers)

        # 1. Deterministic XOR hex check:
        # If XOR is in the cascade, the ciphertext is in hex. The first layer to unwind must be XOR.
        first_fwd_type = fwd_layers[0][2].get("cipher_type", fwd_layers[0][2].get("media_type", "")).lower()
        first_rev_type = rev_layers[0][2].get("cipher_type", rev_layers[0][2].get("media_type", "")).lower()

        if first_fwd_type == "xor" and first_rev_type != "xor":
            return fwd_layers
        if first_rev_type == "xor" and first_fwd_type != "xor":
            return rev_layers

        # 2. Both or neither have XOR first: simulate unwinding both candidates and score readability
        inst_rev = cls(ciphertext, rev_layers, show_ui=False)
        text_rev, _, hex_ok_rev = inst_rev._unwind_cascade(rev_layers)
        score_rev = cls._score_candidate_plaintext(text_rev, hex_ok_rev)

        inst_fwd = cls(ciphertext, fwd_layers, show_ui=False)
        text_fwd, _, hex_ok_fwd = inst_fwd._unwind_cascade(fwd_layers)
        score_fwd = cls._score_candidate_plaintext(text_fwd, hex_ok_fwd)

        if score_fwd > score_rev:
            return fwd_layers
        return rev_layers

    def decrypt(self) -> str:
        """Decrypts message through key layers with smart bidirectional unwinding support.
        
        Seamlessly supports both:
        1. Original encryption sequence (e.g. 1, 2, 3, 4, 5) -> auto-reverses to 5, 4, 3, 2, 1
        2. Manual reverse sequence (e.g. 5, 4, 3, 2, 1) -> unwinds directly 5, 4, 3, 2, 1
        """
        unwind_sequence = self.determine_unwind_sequence(self.key_layers, self.message)
        self.actual_unwind_layers = unwind_sequence
        current_text, layer_logs, _ = self._unwind_cascade(unwind_sequence)

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
        pipeline_table.add_column("Type", style="cyan", justify="center", width=12)
        pipeline_table.add_column("Source / Key", style="green", justify="left")
        pipeline_table.add_column("SHA-256 Code", style="dim", justify="left")

        for log in layer_logs:
            m_type = log["media_type"].lower()
            if m_type == "image":
                icon = "🖼️ Image"
            elif m_type == "music":
                icon = "🎵 Music"
            elif m_type == "monoalphabetic":
                icon = "🔤 Mono"
            elif m_type == "vigenere":
                icon = "🗝️ Vigenère"
            elif m_type == "xor":
                icon = "⚡ XOR"
            else:
                icon = "📁 Media"
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
