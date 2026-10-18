# Enigma Machine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![UI](https://img.shields.io/badge/Terminal_UI-Rich-magenta.svg?logo=terminal&logoColor=white)](https://github.com/Textualize/rich)
[![Testing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?logo=pytest&logoColor=white)](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/test_enigma.py)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A modular, extensible terminal cryptography application implemented in Python. The program features an interactive, styled command-line interface powered by the [Rich](https://github.com/Textualize/rich) library, complete with persistent JSON key management, disk file encryption/decryption, an image-derived cryptographic key engine that replaces all alphabets, numbers, and symbols, and automated test coverage.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
  - [Workflow Diagram](#workflow-diagram)
  - [Repository Structure](#repository-structure)
  - [Module Breakdown](#module-breakdown)
- [Cryptographic Mechanics & Algorithmic Complexity](#cryptographic-mechanics--algorithmic-complexity)
  - [Image to Code & Key Derivation](#image-to-code--key-derivation)
  - [95-Character Substitution Table](#95-character-substitution-table)
  - [Instant $O(1)$ Decryption Optimization](#instant-o1-decryption-optimization)
  - [Formatting & Multiline Preservation](#formatting--multiline-preservation)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage & Interactive CLI Walkthrough](#usage--interactive-cli-walkthrough)
  - [Starting the Application](#starting-the-application)
  - [Main Menu Navigation](#main-menu-navigation)
  - [Option A: Encrypt Message](#option-a-encrypt-message)
  - [Option B: Decrypt Message](#option-b-decrypt-message)
  - [Option C: Load / Generate Image Key](#option-c-load--generate-image-key)
  - [Option D: Manage & Inspect Image Keys](#option-d-manage--inspect-image-keys)
  - [Option E: File Cryptography (.txt Documents)](#option-e-file-cryptography-txt-documents)
  - [Option X: Clean Exit](#option-x-clean-exit)
- [Key Storage & JSON Persistence](#key-storage--json-persistence)
- [Audit Logging System](#audit-logging-system)
- [Automated Unit Testing](#automated-unit-testing)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Security Notice](#security-notice)

---

## Overview

**Enigma Machine** is a command-line cryptography suite built for encrypting, decrypting, inspecting, and managing text and files directly in the terminal using **image-derived cryptographic keys**. Any image file (PNG, JPG, BMP, WEBP, etc.) can be loaded or generated, turned into cryptographic code, and used as a substitution key that scrambles the entire alphabet (lowercase and uppercase), numbers, and symbols.

Designed with user experience and reliability at its core, the application features input validation, crash recovery, cancellation prompts, and persistent storage across sessions.

---

## Key Features

- **Image-to-Code Key Derivation**: Turns any image file into a cryptographic SHA-256 fingerprint and deterministic seed to create unique substitution keys.
- **Full-Spectrum Character Substitution (95 characters)**: Completely scrambles lowercase letters (`a-z`), uppercase letters (`A-Z`), digits (`0-9`), and all symbols & punctuation (`!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ `).
- **Built-in Key Image Generator**: Creates colorful, valid 24-bit uncompressed `.bmp` key images on demand with zero external dependencies.
- **Persistent Key Store (`keys.json`)**: Image paths, cryptographic codes, timestamps, and substitution mappings are saved to disk and reloaded on startup.
- **Optimized $O(1)$ Inverted Lookup**: Precomputes an inverted substitution dictionary upon cipher initialization, turning decryption from an $O(N)$ linear scan into an instantaneous $O(1)$ hash map lookup.
- **File Cryptography**: Encrypt and decrypt arbitrary `.txt` files directly on disk with automatic destination naming (`_encrypted.txt` and `_decrypted.txt`) and confirmation panels.
- **Detailed Key Inspector**: Renders side-by-side [Rich Tables](https://rich.readthedocs.io/) showing image metadata, SHA-256 fingerprints, and character mappings for letters, numbers, and symbols.
- **Crash & Edge-Case Protection**:
  - Handles empty key stores gracefully with on-the-spot generation/loading prompts.
  - Safe cancellation options (`'c'`, `'cancel'`, `'q'`, or empty input) return cleanly without throwing exceptions.
  - Safe pass-through for non-ASCII characters and multiline linebreaks (`\n`).
  - Handles `Ctrl+C` (`KeyboardInterrupt`) cleanly without traceback dumps.
- **Styled Terminal UI**: Animated progress bars, spinner columns, styled cards, colored tables, and cross-platform terminal clearing (`cls` / `clear`).
- **Comprehensive Unit Testing**: Built-in test suite covering image-to-code generation, BMP generation, roundtrip encryption/decryption across letters, numbers, and symbols, persistence, and menu dispatching.
- **Audit Logs**: Automatically logs all operations to `Encryption.txt` and `Decryption.txt` with formatted timestamps, key IDs, image codes, and result strings.

---

## System Architecture

### Workflow Diagram

```mermaid
flowchart TD
    User([User Terminal]) -->|Launch| Main[[main.py: CLI Entry Point]]
    Main --> MenuModule[[menu_module.py: Interactive Menus]]
    
    MenuModule -->|Option A: Encrypt| EncryptFlow[Message Encryption]
    MenuModule -->|Option B: Decrypt| DecryptFlow[Message Decryption]
    MenuModule -->|Option C: Load/Gen Key| KeyGen[key_module.py: Image Key Generator/Loader]
    MenuModule -->|Option D: Inspect/Delete| KeyMgmt[key_module.py: Key Inspector & Storage]
    MenuModule -->|Option E: File Cipher| FileFlow[File Cryptography]
    MenuModule -->|Option X: Exit| ExitApp([Clean Exit])

    EncryptFlow --> KeySelect{Select Key / Image Path}
    DecryptFlow --> KeySelect
    FileFlow --> KeySelect

    KeySelect -->|Key Store| KeyStore[(keys.json)]
    KeySelect -->|Raw Image File| ImageReader[image_key_cipher.py: read_image_bytes & image_to_code]
    KeySelect --> CipherEngine[[image_key_cipher.py: ImageKeyCipher]]
    
    CipherEngine -->|O(1) Forward / Inverse Map| Results[Rich UI Card Display]
    CipherEngine -->|Append Audit Entry| Logs[(Encryption.txt / Decryption.txt)]
```

### Repository Structure

```
Enigma Machine/
├── main.py                   # Main CLI entry point and menu router
├── menu_module.py            # Menu UI flows, input validation, and dispatchers
├── key_module.py             # Image key registration, JSON persistence, inspection tables
├── image_key_cipher.py       # Image-to-code cryptographic cipher engine (alphabet, numbers, symbols)
├── utilities_module.py       # Cross-platform terminal helpers, progress animations
├── mesage_encryptor.py       # Cryptographic message data model with image metadata
├── test_enigma.py            # Unit test suite (unittest)
├── keys.json                 # Persistent key storage file (auto-generated)
├── key_images/               # Directory for generated sample key images (auto-generated)
├── Encryption.txt            # Audit log for encryption operations (auto-generated)
├── Decryption.txt            # Audit log for decryption operations (auto-generated)
├── requirements.txt          # Python dependencies (rich)
├── .gitignore                # Ignored cache, logs, and persistent data
└── README.md                 # Project documentation
```

### Module Breakdown

| Module | Primary Symbol / Class | Description |
|---|---|---|
| [main.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/main.py) | `main()`, `main_menu()` | Registers main menu options, dispatches user actions, and manages clean exit routines. |
| [menu_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/menu_module.py) | [Menu](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/menu_module.py#L38-L82), `encrypt_menu()`, `decrypt_menu()`, `file_cipher_menu()`, `key_management_menu()` | Renders styled menus, coordinates user prompts, validates input, and controls workflow transitions. |
| [key_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/key_module.py) | `register_image_file()`, `generate_key()`, `load_keys()`, `save_keys()`, `show_all_keys()`, `inspect_key()`, `delete_key()` | Converts image files to keys, generates sample key images, persists keys in `keys.json`, and renders formatted Rich tables. |
| [image_key_cipher.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/image_key_cipher.py) | [ImageKeyCipher](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/image_key_cipher.py#L98-L195), `generate_key_from_image()`, `image_to_code()` | Converts image bytes into code fingerprints, generates 95-char substitution maps, executes $O(1)$ operations, and logs results. |
| [utilities_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/utilities_module.py) | `clear_screen()`, `progress_bar()`, `display_header()`, `prompt_delay()` | Provides cross-platform terminal clearing, animated spinner progress bars, and standardized visual banners. |
| [mesage_encryptor.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/mesage_encryptor.py) | [Message](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/mesage_encryptor.py#L7-L18) | Clean dataclass model wrapping message text, operation modes, and associated key metadata. |
| [test_enigma.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/test_enigma.py) | `TestImageKeyCipher`, `TestKeyModule`, `TestMenuModule` | Full unit test suite validating image-to-code generation, roundtrips, symbol & number substitution, persistence, and key selection. |

---

## Cryptographic Mechanics & Algorithmic Complexity

### Image to Code & Key Derivation

Instead of relying on basic letter shuffling, keys are derived from **image files** (PNG, JPG, BMP, WEBP, GIF, etc.):
1. The image is read as a raw binary byte sequence.
2. A cryptographic **SHA-256 hash** (64 hex characters) and short fingerprint (16 characters) are generated:
   $$\text{Seed} = \text{SHA-256}(\text{ImageBytes})$$
3. The cryptographic digest is converted into an integer seed to initialize a deterministic pseudo-random generator.
4. The 95-character set is scrambled deterministically:
   - Identical image files will always produce the exact same substitution key.
   - Any single-bit change in an image produces an entirely different key (avalanche effect).

### 95-Character Substitution Table

The cipher operates over all 95 printable ASCII characters:
- **Lowercase alphabet**: `a` through `z` (26 characters)
- **Uppercase alphabet**: `A` through `Z` (26 characters)
- **Numbers**: `0` through `9` (10 characters)
- **Symbols & whitespace**: `!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ` (32 punctuation characters + space = 33 characters)

Each key is a bijective permutation across all 95 characters:
$$\text{Keyspace} = 95! \approx 1.0329 \times 10^{148}$$

This ensures that letters, numbers, punctuation, and spaces are completely substituted and encrypted.

### Instant $O(1)$ Decryption Optimization

In naive implementations, decrypting a character requires searching the entire substitution dictionary ($O(K)$ where $K = 95$ per character).

[ImageKeyCipher](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/image_key_cipher.py#L98-L195) precomputes an inverted hash map once during initialization:

```python
self.inverse_key: dict[str, str] = {v: k for k, v in self.key.items()}
```

- **Encryption Complexity**: $O(N)$ total time, with $O(1)$ lookup per character via `self.key.get(char, char)`.
- **Decryption Complexity**: $O(N)$ total time, with $O(1)$ lookup per character via `self.inverse_key.get(char, char)`.
- **Space Complexity**: $O(K)$ where $K = 95$ entries in memory.

### Formatting & Multiline Preservation

Characters outside the 95-character printable set (such as line breaks `\n` and tabs `\t`) pass through unmodified, preserving multi-line file structure while thoroughly scrambling the entire body text.

---

## Prerequisites

- **Python**: Version `3.10` or higher.
- **Operating System**: Windows 10/11, macOS, or Linux.
- **Terminal**: Modern terminal with ANSI color and UTF-8 support (PowerShell, Windows Terminal, Bash, Zsh).

---

## Installation & Setup

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/your-username/enigma-machine.git
   cd "Enigma Machine"
   ```

2. **Set Up a Virtual Environment (Recommended)**:
   - **Windows (PowerShell)**:
     ```powershell
     py -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage & Interactive CLI Walkthrough

### Starting the Application

Launch the program using Python:

```bash
# Windows
py main.py

# macOS / Linux
python3 main.py
```

### Main Menu Navigation

Upon launch, you are greeted with the styled main navigation panel:

```text
╭──────────────────────────────────────────────────╮
│                  ENIGMA MACHINE                  │
│ Image Key Cryptography (Alphabet, Numbers & Sym) │
╰──────────────────────────────────────────────────╯

[A] - Encrypt Message
[B] - Decrypt Message
[C] - Load / Generate Image Key
[D] - Manage & Inspect Image Keys
[E] - File Cryptography (Encrypt/Decrypt .txt)
[X] - Exit Program

Enter the code of the option you want to select:
```

---

### Option A: Encrypt Message

1. Select option **`A`**.
2. Input the plain text message when prompted (including letters, numbers, and symbols).
3. A table of available keys is displayed. Enter the key number (e.g., `1`), or provide an image file path directly (e.g., `my_photo.png`), or press `'c'` to cancel.
4. An animated progress bar simulates cipher execution.
5. A stylized **ENCRYPTION RESULT** card appears, displaying:
   - The original input string.
   - The encrypted ciphertext.
   - Source Image File and Image Code (SHA-256 fingerprint).
   - Sample preview showing substituted alphabet, numbers, and symbols.
6. The operation is logged to `Encryption.txt`.

---

### Option B: Decrypt Message

1. Select option **`B`**.
2. Enter or paste the ciphertext.
3. Select the key number or image file used for the original encryption.
4. The cipher executes an instantaneous $O(1)$ inverse lookup.
5. The decrypted original text is displayed and logged to `Decryption.txt`.

---

### Option C: Load / Generate Image Key

Select option **`C`** to either:
1. **Generate New Sample Key Image**: Creates a colorful 24-bit `.bmp` image in `key_images/key_image_<id>.bmp`, generates its cryptographic code, derives the substitution key, and registers it.
2. **Load & Register Existing Image File**: Enter the path to any `.png`, `.jpg`, `.bmp`, or other image file to convert it into an Image Key.

---

### Option D: Manage & Inspect Image Keys

Select option **`D`** to enter the Image Key Management Sub-Menu:

```text
[1] Show All Keys Overview
[2] Inspect Detailed Character Mapping & Image Code
[3] Load & Register Image File
[4] Generate Sample Key Image (.bmp)
[5] Delete an Image Key
[6] Return to Main Menu
```

#### 1. Show All Keys Overview
Displays a summary table of all stored keys:
- **Key #**: Identifier.
- **Image File**: Filename of the source image.
- **Image Code (SHA-256)**: Cryptographic fingerprint preview.
- **Size**: Image file size in bytes.
- **Created At**: Timestamp (`YYYY-MM-DD HH:MM:SS`).
- **Mapped**: Total substituted characters (95 chars).

#### 2. Detailed Character Mapping Inspector
Prompts for a key ID and displays:
- Complete image metadata (path, file size, timestamp, full 64-character SHA-256 hash).
- **Alphabet Substitution Table**: Lowercase (`a-z`) and Uppercase (`A-Z`).
- **Numbers & Symbols Table**: Digits (`0-9`), space, and punctuation mappings.

#### 3. Delete an Image Key
Permanently deletes a key from active memory and updates `keys.json`.

---

### Option E: File Cryptography (.txt Documents)

Encrypt or decrypt text files without copying and pasting:

1. Select option **`E`**.
2. Choose operation: `encrypt`, `decrypt`, or `back`.
3. Provide the path to your source file (e.g., `report.txt`).
4. Accept the default destination file name (e.g., `report_encrypted.txt`) or type a custom destination.
5. Select the key number to process with.
6. The file is processed and written to disk with an operational confirmation card.

---

### Option X: Clean Exit

Select **`X`** or press `Ctrl+C` at any prompt to exit cleanly without runtime warnings or unhandled exceptions.

---

## Key Storage & JSON Persistence

All substitution keys are saved locally in [keys.json](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/keys.json). The schema supports metadata tracking:

```json
{
  "1": {
    "created_at": "2026-10-14 02:51:24",
    "mapping": {
      "a": "V",
      "b": "A",
      "c": "N",
      "A": "o",
      "B": "w",
      "C": "k"
    }
  }
}
```

- **Backward Compatibility**: If legacy raw dictionary keys are detected in `keys.json`, they are automatically imported with a fallback timestamp.
- **Automatic Reload**: On module import, [key_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/key_module.py) loads existing keys into memory so they are immediately available for use.

---

## Audit Logging System

Every message encryption and decryption is automatically appended to persistent audit log files with full operational metadata.

### Example `Encryption.txt` Entry

```text
------------------------------------------------------------------------------------------------------------------------
Wednesday, October 14 2026 at 03:02 AM

Original Message: Confidential Mission 2026!
Key Number: 1

Original Alphabet: a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
Substitute Alphabet: V A N T g D u m i d Y c a S e U O H v F E I B M q C o w k n p j r G b J y R Q x X P Z W h z l t s L K f

Encryption Result: NeoDitsSFeac AvvseS 2026!
------------------------------------------------------------------------------------------------------------------------
```

### Example `Decryption.txt` Entry

```text
------------------------------------------------------------------------------------------------------------------------
Wednesday, October 14 2026 at 03:03 AM

Original Message: NeoDitsSFeac AvvseS 2026!
Key Number: 1

Original Alphabet: a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
Substitute Alphabet: V A N T g D u m i d Y c a S e U O H v F E I B M q C o w k n p j r G b J y R Q x X P Z W h z l t s L K f

Decryption Result: Confidential Mission 2026!
------------------------------------------------------------------------------------------------------------------------
```

---

## Automated Unit Testing

The project includes unit test coverage in [test_enigma.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/test_enigma.py) utilizing Python's built-in `unittest` framework.

### Running the Test Suite

```bash
# Windows
py -m unittest test_enigma.py -v

# macOS / Linux
python3 -m unittest test_enigma.py -v
```

### Test Coverage Highlights

- `test_encrypt_and_decrypt_roundtrip`: Verifies that encrypting and subsequently decrypting a message restores the exact original text.
- `test_preserves_punctuation_and_spaces`: Validates that spaces, digits, and special characters remain unmodified in place.
- `test_strict_mode_strips_spaces`: Tests non-formatting mode (`preserve_formatting=False`).
- `test_generate_key_structure`: Confirms generated keys contain 52 unique mapping pairs for all lowercase and uppercase letters.
- `test_key_persistence_json`: Verifies saving, reloading, and clearing key stores via temporary JSON files.
- `test_delete_key`: Verifies deletion from active memory and JSON persistence.
- `test_select_key`: Ensures valid key retrieval and graceful `None` handling for invalid keys.
- `test_menu_add_option_chaining`: Checks builder pattern method chaining for menu items.
- `test_verify_user_code`: Validates user menu option code verification logic.

---

## Troubleshooting & FAQ

### 1. `Python was not found` on Windows
If running `python` prompts the Microsoft Store, use the official Python launcher:
```powershell
py main.py
```
Alternatively, disable Microsoft Store execution aliases in:
*Windows Settings > Apps > Advanced app settings > App execution aliases*.

### 2. PowerShell Script Execution Error (`Activate.ps1`)
If activating the virtual environment raises an `ExecutionPolicy` error:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

### 3. Terminal Formatting & Colors
For the best visual experience with Rich tables and spinners, run the program in:
- **Windows Terminal** (recommended for Windows 10/11)
- **PowerShell 7+**
- **iTerm2 / Alacritty / GNOME Terminal** (macOS / Linux)

---

## Security Notice

This application implements an **Image Key Substitution Cipher**, a custom cryptographic cipher created for educational, demonstration, and text processing purposes.

> [!NOTE]
> While the image-derived key space covers 95 printable characters ($95! \approx 10^{148}$) and hashes images with SHA-256, mono-character substitution ciphers remain susceptible to advanced frequency analysis if large texts are encrypted. For production-grade secrets, consider modern block ciphers like AES-GCM or ChaCha20-Poly1305.

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
