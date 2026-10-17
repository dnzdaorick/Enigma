# Enigma Machine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![UI](https://img.shields.io/badge/Terminal_UI-Rich-magenta.svg?logo=terminal&logoColor=white)](https://github.com/Textualize/rich)
[![Testing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?logo=pytest&logoColor=white)](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/test_enigma.py)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A modular, extensible terminal cryptography application implemented in Python. The program features an interactive, styled command-line interface powered by the [Rich](https://github.com/Textualize/rich) library, complete with persistent JSON key management, disk file encryption/decryption, an optimized $O(1)$ substitution cipher engine, and automated test coverage.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
  - [Workflow Diagram](#workflow-diagram)
  - [Repository Structure](#repository-structure)
  - [Module Breakdown](#module-breakdown)
- [Cryptographic Mechanics & Algorithmic Complexity](#cryptographic-mechanics--algorithmic-complexity)
  - [52-Character Substitution Table](#52-character-substitution-table)
  - [Instant $O(1)$ Decryption Optimization](#instant-o1-decryption-optimization)
  - [Formatting & Non-Alphabetic Preservation](#formatting--non-alphabetic-preservation)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage & Interactive CLI Walkthrough](#usage--interactive-cli-walkthrough)
  - [Starting the Application](#starting-the-application)
  - [Main Menu Navigation](#main-menu-navigation)
  - [Option A: Encrypt Message](#option-a-encrypt-message)
  - [Option B: Decrypt Message](#option-b-decrypt-message)
  - [Option C: Generate Substitution Key](#option-c-generate-substitution-key)
  - [Option D: Manage & Inspect Keys](#option-d-manage--inspect-keys)
  - [Option E: File Cryptography (.txt Documents)](#option-e-file-cryptography-txt-documents)
  - [Option X: Clean Exit](#option-x-clean-exit)
- [Key Storage & JSON Persistence](#key-storage--json-persistence)
- [Audit Logging System](#audit-logging-system)
- [Automated Unit Testing](#automated-unit-testing)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Security Notice](#security-notice)

---

## Overview

**Enigma Machine** is a command-line cryptography suite built for encrypting, decrypting, inspecting, and managing text and files directly in the terminal. The architecture is organized into decoupled modules (menus, key store, cipher engine, terminal utilities), making it straightforward to maintain, test, and expand with additional ciphers in the future.

Designed with user experience and reliability at its core, the application features input validation, crash recovery, cancellation prompts, and persistent storage across sessions.

---

## Key Features

- **Persistent Key Store (`keys.json`)**: Keys are automatically saved to disk and reloaded on startup, maintaining timestamps and mappings across sessions.
- **Optimized $O(1)$ Inverted Lookup**: Precomputes an inverted substitution dictionary upon cipher initialization, turning decryption from an $O(N)$ linear scan into an instantaneous $O(1)$ hash map lookup.
- **File Cryptography**: Encrypt and decrypt arbitrary `.txt` files directly on disk with automatic destination naming (`_encrypted.txt` and `_decrypted.txt`) and confirmation panels.
- **Detailed Key Inspector**: Renders side-by-side [Rich Tables](https://rich.readthedocs.io/) showing all 52 character mappings (lowercase and uppercase parallel layout) with timestamps and key stats.
- **Crash & Edge-Case Protection**:
  - Handles empty key stores gracefully with on-the-spot generation prompts.
  - Safe cancellation options (`'c'`, `'cancel'`, `'q'`, or empty input) return cleanly without throwing exceptions.
  - Non-destructive processing of spaces, numbers, and punctuation without `KeyError` crashes.
  - Handles `Ctrl+C` (`KeyboardInterrupt`) cleanly without traceback dumps.
- **Styled Terminal UI**: Animated progress bars, spinner columns, styled cards, colored tables, and cross-platform terminal clearing (`cls` / `clear`).
- **Comprehensive Unit Testing**: Built-in test suite covering encryption/decryption roundtrips, symbol preservation, JSON persistence, key deletion, and menu dispatching.
- **Audit Logs**: Automatically logs all operations to `Encryption.txt` and `Decryption.txt` with formatted timestamps, key IDs, and alphabet snapshots.

---

## System Architecture

### Workflow Diagram

```mermaid
flowchart TD
    User([User Terminal]) -->|Launch| Main[[main.py: CLI Entry Point]]
    Main --> MenuModule[[menu_module.py: Interactive Menus]]
    
    MenuModule -->|Option A: Encrypt| EncryptFlow[Message Encryption]
    MenuModule -->|Option B: Decrypt| DecryptFlow[Message Decryption]
    MenuModule -->|Option C: Generate| KeyGen[key_module.py: generate_key]
    MenuModule -->|Option D: Inspect/Delete| KeyMgmt[key_module.py: Key Inspector & Storage]
    MenuModule -->|Option E: File Cipher| FileFlow[File Cryptography]
    MenuModule -->|Option X: Exit| ExitApp([Clean Exit])

    EncryptFlow --> KeySelect{Select Key}
    DecryptFlow --> KeySelect
    FileFlow --> KeySelect

    KeySelect -->|Key Store| KeyStore[(keys.json)]
    KeySelect --> CipherEngine[[monoalphabetic_cipher.py: MonoalphabeticCipher]]
    
    CipherEngine -->|O(1) Forward / Inverse Map| Results[Rich UI Card Display]
    CipherEngine -->|Append Audit Entry| Logs[(Encryption.txt / Decryption.txt)]
```

### Repository Structure

```
Enigma Machine/
├── main.py                   # Main CLI entry point and menu router
├── menu_module.py            # Menu UI flows, input validation, and dispatchers
├── key_module.py             # Key generation, JSON persistence, inspection tables
├── monoalphabetic_cipher.py  # O(1) Monoalphabetic substitution engine & file logger
├── utilities_module.py       # Cross-platform terminal helpers, progress animations
├── mesage_encryptor.py       # Cryptographic message data model
├── test_enigma.py            # Unit test suite (unittest)
├── keys.json                 # Persistent key storage file (auto-generated)
├── Encryption.txt            # Audit log for encryption operations (auto-generated)
├── Decryption.txt            # Audit log for decryption operations (auto-generated)
├── requirements.txt          # Python dependencies
├── .gitignore                # Ignored cache, logs, and persistent data
└── README.md                 # Project documentation
```

### Module Breakdown

| Module | Primary Symbol / Class | Description |
|---|---|---|
| [main.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/main.py) | `main()`, `main_menu()` | Registers main menu options, dispatches user actions, and manages clean exit routines. |
| [menu_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/menu_module.py) | [Menu](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/menu_module.py#L18-L62), `encrypt_menu()`, `decrypt_menu()`, `file_cipher_menu()`, `key_management_menu()` | Renders styled menus, coordinates user prompts, validates input, and controls workflow transitions. |
| [key_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/key_module.py) | `generate_key()`, `load_keys()`, `save_keys()`, `show_all_keys()`, `inspect_key()`, `delete_key()` | Generates random 52-character pairs, persists keys in `keys.json`, and renders formatted Rich tables. |
| [monoalphabetic_cipher.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/monoalphabetic_cipher.py) | [MonoalphabeticCipher](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/monoalphabetic_cipher.py#L9-L86) | Executes $O(1)$ character substitution, preserves formatting, displays UI result panels, and appends audit logs. |
| [utilities_module.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/utilities_module.py) | `clear_screen()`, `progress_bar()`, `display_header()`, `prompt_delay()` | Provides cross-platform terminal clearing, animated spinner progress bars, and standardized visual banners. |
| [mesage_encryptor.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/mesage_encryptor.py) | [Message](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/mesage_encryptor.py#L7-L18) | Clean dataclass model wrapping message text, operation modes, and associated key metadata. |
| [test_enigma.py](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/test_enigma.py) | `TestMonoalphabeticCipher`, `TestKeyModule`, `TestMenuModule` | Full unit test suite validating encryption roundtrips, persistence, symbol handling, and key selection. |

---

## Cryptographic Mechanics & Algorithmic Complexity

### 52-Character Substitution Table

The cipher operates over all 52 English alphabetic characters:
- Lowercase: `a` through `z` (ASCII 97–122)
- Uppercase: `A` through `Z` (ASCII 65–90)

Each key is a bijective permutation of these 52 characters. The total keyspace is:
$$52! \approx 8.0658 \times 10^{67}$$

This ensures that each letter has an independent substitution mapping for both lowercase and uppercase variations.

### Instant $O(1)$ Decryption Optimization

In naive monoalphabetic implementations, decrypting a character requires searching the entire dictionary values to locate the corresponding plain character ($O(K)$ where $K = 52$ for each character in an $N$-length text, yielding $O(N \cdot K)$ total time).

[MonoalphabeticCipher](file:///d:/dnzdaorick/OneDrive%20-%20Malayan%20Colleges%20Laguna/Programming/Python/Program%20Projects/Enigma%20Machine/monoalphabetic_cipher.py#L9-L86) resolves this by precomputing an inverted hash map once on initialization:

```python
self.inverse_key: dict[str, str] = {v: k for k, v in self.key.items()}
```

- **Encryption Complexity**: $O(N)$ total time, with $O(1)$ lookup per character via `self.key.get(char, char)`.
- **Decryption Complexity**: $O(N)$ total time, with $O(1)$ lookup per character via `self.inverse_key.get(char, char)`.
- **Space Complexity**: $O(K)$ where $K = 52$ entries in memory.

### Formatting & Non-Alphabetic Preservation

By default, `preserve_formatting=True` is enabled. Any character outside the 52-letter alphabet (such as spaces, digits `0-9`, punctuation `!?,.-:;`, and special symbols) is passed through unmodified:

```python
encrypted_chars = [self.key.get(char, char) for char in source_text]
```

This prevents runtime exceptions (`KeyError`) and preserves the structure, indentation, and readability of encrypted documents.

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
│     Cryptographic Operations & Key Management    │
╰──────────────────────────────────────────────────╯

[A] - Encrypt Message
[B] - Decrypt Message
[C] - Generate Substitution Key
[D] - Manage & Inspect Keys
[E] - File Cryptography (Encrypt/Decrypt .txt)
[X] - Exit Program

Enter the code of the option you want to select:
```

---

### Option A: Encrypt Message

1. Select option **`A`**.
2. Input the plain text message when prompted:
   ```text
   Enter the message to encrypt: Confidential Report 2026: Mission Successful!
   ```
3. A table of available keys is displayed. Enter the key number (e.g., `1`), or press `'c'` to cancel.
4. An animated progress bar simulates cipher execution:
   ```text
   Encrypting message... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0.2s
   ```
5. A stylized **ENCRYPTION RESULT** card appears, displaying:
   - The original input string.
   - The encrypted ciphertext.
   - A 15-character preview of the substitution mapping.
6. The operation is logged to `Encryption.txt`.

---

### Option B: Decrypt Message

1. Select option **`B`**.
2. Enter or paste the ciphertext.
3. Select the key number used for original encryption.
4. The cipher executes an instantaneous $O(1)$ inverse lookup.
5. The decrypted original text is displayed and logged to `Decryption.txt`.

---

### Option C: Generate Substitution Key

1. Select option **`C`**.
2. A new 52-character bi-directional key is generated automatically by shuffling letters `a-z` and `A-Z`.
3. The key is assigned the next sequential integer identifier (e.g., `Key #3`) and persisted to `keys.json` with a timestamp:
   ```text
   Key 3 generated and saved to keys.json successfully!
   ```

---

### Option D: Manage & Inspect Keys

Select option **`D`** to enter the Key Management Sub-Menu:

```text
[1] Show All Keys Overview
[2] Inspect Detailed Character Mapping for a Key
[3] Delete a Key
[4] Return to Main Menu
```

#### 1. Show All Keys Overview
Displays a summary table of all stored keys:
- **Key #**: Identifier.
- **Created At**: Timestamp (`YYYY-MM-DD HH:MM:SS`).
- **Sample Mapping (a-f)**: Quick glance at initial letter substitutions (`a→V, b→A, ...`).
- **Total Characters**: Mapped count (52 characters).

#### 2. Detailed Character Mapping Inspector
Prompts for a key ID and prints a complete side-by-side table displaying all 52 substitutions:

| Lower | → | Mapped | \| | Upper | → | Mapped |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `a` | → | `V` | \| | `A` | → | `o` |
| `b` | → | `A` | \| | `B` | → | `w` |
| `c` | → | `N` | \| | `C` | → | `k` |
| ... | → | ... | \| | ... | → | ... |
| `z` | → | `C` | \| | `Z` | → | `f` |

#### 3. Delete a Key
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

This application implements a **Monoalphabetic Substitution Cipher**, a classical cryptographic cipher created for educational, demonstration, and text processing purposes.

> [!NOTE]
> Monoalphabetic substitution ciphers preserve letter frequency characteristics and are vulnerable to frequency analysis attacks. They should not be used for securing sensitive real-world secrets or high-security production data. For production cryptographic needs, use modern standards such as AES-256 (e.g., via Python's `cryptography` library).

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
