"""Cipher module for Enigma Machine.

Implements classical algorithmic ciphers (single classical variant per cipher):
- Monoalphabetic Substitution Cipher (Classical Random Alphabet)
- Vigenère Polyalphabetic Cipher (Classical A-Z modulo 26 shift)
- XOR Cipher (Classical repeating keystream bitwise XOR)
"""

import hashlib
import random
import string

# Complete printable character set (95 characters)
ALPHABET_LOWER: str = string.ascii_lowercase
ALPHABET_UPPER: str = string.ascii_uppercase
NUMBERS: str = string.digits
SYMBOLS: str = string.punctuation + " "
FULL_CHARSET: list[str] = list(ALPHABET_LOWER + ALPHABET_UPPER + NUMBERS + SYMBOLS)


# -----------------------------------------------------------------------------
# Monoalphabetic Substitution Cipher (Classical Random Alphabet)
# -----------------------------------------------------------------------------

def generate_monoalphabetic_key(
    *args, **kwargs
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Derives a classical monoalphabetic random alphabet substitution key.

    Randomly permutes lowercase (a-z) and uppercase (A-Z) letters while preserving
    digits, spaces, and punctuation symbols.

    Returns:
        (substitution_key, inverse_key, code_info)
    """
    shuffled_lower = list(ALPHABET_LOWER)
    random.shuffle(shuffled_lower)
    shuffled_upper = [c.upper() for c in shuffled_lower]

    substitution_key: dict[str, str] = {}
    for orig, subst in zip(ALPHABET_LOWER, shuffled_lower):
        substitution_key[orig] = subst
    for orig, subst in zip(ALPHABET_UPPER, shuffled_upper):
        substitution_key[orig] = subst
    for ch in NUMBERS + SYMBOLS:
        substitution_key[ch] = ch

    inverse_key = {subst: orig for orig, subst in substitution_key.items()}
    serialized = "".join(f"{k}->{v}" for k, v in sorted(substitution_key.items()))
    sha256_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    label = "Monoalphabetic Key"
    code_info = {
        "sha256": sha256_hash,
        "sha512": hashlib.sha512(serialized.encode("utf-8")).hexdigest(),
        "short_code": sha256_hash[:16].upper(),
        "byte_size": str(len(substitution_key)),
        "media_type": "monoalphabetic",
        "cipher_type": "monoalphabetic",
        "variant": "classical",
        "label": label,
        "key_value": "random_alphabet",
    }
    return substitution_key, inverse_key, code_info


# -----------------------------------------------------------------------------
# Vigenère Cipher (Classical A-Z Modulo 26)
# -----------------------------------------------------------------------------

def vigenere_encrypt(text: str, key: str, variant: str = "classical") -> str:
    """Standard classical Vigenère encryption shifting A-Z and a-z modulo 26.

    Preserves spaces, numbers, and punctuation marks.
    """
    clean_key = [c for c in key if c.isalpha()]
    if not clean_key:
        clean_key = list("KEY")
    k_len = len(clean_key)
    result: list[str] = []
    k_idx = 0
    for c in text:
        if "a" <= c <= "z":
            shift = ord(clean_key[k_idx % k_len].lower()) - ord("a")
            result.append(chr((ord(c) - ord("a") + shift) % 26 + ord("a")))
            k_idx += 1
        elif "A" <= c <= "Z":
            shift = ord(clean_key[k_idx % k_len].upper()) - ord("A")
            result.append(chr((ord(c) - ord("A") + shift) % 26 + ord("A")))
            k_idx += 1
        else:
            result.append(c)
    return "".join(result)


def vigenere_decrypt(text: str, key: str, variant: str = "classical") -> str:
    """Standard classical Vigenère decryption reversing shifts modulo 26."""
    clean_key = [c for c in key if c.isalpha()]
    if not clean_key:
        clean_key = list("KEY")
    k_len = len(clean_key)
    result: list[str] = []
    k_idx = 0
    for c in text:
        if "a" <= c <= "z":
            shift = ord(clean_key[k_idx % k_len].lower()) - ord("a")
            result.append(chr((ord(c) - ord("a") - shift) % 26 + ord("a")))
            k_idx += 1
        elif "A" <= c <= "Z":
            shift = ord(clean_key[k_idx % k_len].upper()) - ord("A")
            result.append(chr((ord(c) - ord("A") - shift) % 26 + ord("A")))
            k_idx += 1
        else:
            result.append(c)
    return "".join(result)


# Aliases for backward compatibility
vigenere_classical_encrypt = vigenere_encrypt
vigenere_classical_decrypt = vigenere_decrypt


def generate_vigenere_key(keyword: str = "", variant: str = "classical") -> tuple[str, dict[str, str]]:
    """Generates a classical Vigenère keyword and associated metadata."""
    if not keyword:
        keyword = "".join(random.choices(ALPHABET_UPPER, k=12))
    sha256_hash = hashlib.sha256(keyword.encode("utf-8")).hexdigest()
    code_info = {
        "sha256": sha256_hash,
        "sha512": hashlib.sha512(keyword.encode("utf-8")).hexdigest(),
        "short_code": sha256_hash[:16].upper(),
        "byte_size": str(len(keyword.encode("utf-8"))),
        "media_type": "vigenere",
        "cipher_type": "vigenere",
        "variant": "classical",
        "key_value": keyword,
        "label": f"Vigenère Key [{keyword}]",
    }
    return keyword, code_info


# -----------------------------------------------------------------------------
# XOR Cipher (Classical Repeating Keystream Bitwise XOR)
# -----------------------------------------------------------------------------

def xor_encrypt(text: str, key: str) -> str:
    """Encrypts text using classical repeating key bitwise XOR, returning hexadecimal string."""
    if not key:
        return text
    text_bytes = text.encode("utf-8")
    key_bytes = key.encode("utf-8")
    k_len = len(key_bytes)
    xor_bytes = bytes([b ^ key_bytes[i % k_len] for i, b in enumerate(text_bytes)])
    return xor_bytes.hex()


def xor_decrypt(ciphertext: str, key: str) -> str:
    """Decrypts hexadecimal ciphertext using classical repeating key bitwise XOR back to text."""
    if not key:
        return ciphertext
    key_bytes = key.encode("utf-8")
    k_len = len(key_bytes)
    try:
        cipher_bytes = bytes.fromhex(ciphertext.strip())
    except (ValueError, TypeError):
        cipher_bytes = ciphertext.encode("utf-8")
    decrypted_bytes = bytes([b ^ key_bytes[i % k_len] for i, b in enumerate(cipher_bytes)])
    return decrypted_bytes.decode("utf-8", errors="replace")


def generate_xor_key(key_string: str = "", length: int = 16) -> tuple[str, dict[str, str]]:
    """Generates a classical XOR key string and associated metadata."""
    if not key_string:
        chars = string.ascii_letters + string.digits
        key_string = "".join(random.choices(chars, k=length))
    sha256_hash = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
    code_info = {
        "sha256": sha256_hash,
        "sha512": hashlib.sha512(key_string.encode("utf-8")).hexdigest(),
        "short_code": sha256_hash[:16].upper(),
        "byte_size": str(len(key_string.encode("utf-8"))),
        "media_type": "xor",
        "cipher_type": "xor",
        "variant": "classical",
        "key_value": key_string,
        "label": f"XOR Key [{key_string[:12]}...] ({len(key_string)} B)",
    }
    return key_string, code_info
