# Enigma

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![UI](https://img.shields.io/badge/Terminal_UI-Rich-magenta.svg?logo=terminal&logoColor=white)](https://github.com/Textualize/rich)
[![Testing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?logo=pytest&logoColor=white)](test_enigma.py)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A minimal, multi-layer terminal cryptography suite implemented in Python. The application transforms **Image files** (PNG, JPG, BMP, etc.) and **Music/Audio files** (MP3, WAV, FLAC, etc.) into cryptographic code fingerprints, turning them into substitution keys. Users can encrypt messages using **1 key**, **combine both Image and Music keys**, or chain **2 or more keys in a sequential multi-rotor cascade pipeline**.

---

## Table of Contents

- [Overview](#overview)
- [How the Encryption Works](#how-the-encryption-works)
  - [1. Media-to-Code Transformation](#1-media-to-code-transformation)
  - [2. Deterministic Key Derivation (95 Characters)](#2-deterministic-key-derivation-95-characters)
  - [3. Multi-Key Cascade Encryption (1, 2, or More Keys)](#3-multi-key-cascade-encryption-1-2-or-more-keys)
  - [4. Reversing the Cascade (Decryption)](#4-reversing-the-cascade-decryption)
- [System Architecture](#system-architecture)
  - [Workflow & Pipeline Diagram](#workflow--pipeline-diagram)
  - [Repository Structure](#repository-structure)
  - [Module Breakdown](#module-breakdown)
- [Cryptographic Mechanics & Complexity](#cryptographic-mechanics--complexity)
  - [Full 95-Character Printable Set](#full-95-character-printable-set)
  - [Instant O(1) Hash Map Lookups](#instant-o1-hash-map-lookups)
  - [Keyspace & Compounded Entropy](#keyspace--compounded-entropy)
- [Installation & Quick Start](#installation--quick-start)
- [Interactive CLI Walkthrough](#interactive-cli-walkthrough)
  - [Main Menu Navigation](#main-menu-navigation)
  - [Option A: Encrypt Message](#option-a-encrypt-message)
  - [Option B: Decrypt Message](#option-b-decrypt-message)
  - [Option C: Generate Media Key](#option-c-generate-media-key)
  - [Option D: Manage & Inspect Keys](#option-d-manage--inspect-keys)
- [Key Storage & JSON Persistence](#key-storage--json-persistence)
- [Audit Logging System](#audit-logging-system)
- [Automated Unit Testing](#automated-unit-testing)
- [Security Notice](#security-notice)

---

## Overview

Traditional substitution ciphers rely on manually configured alphabets or pseudo-random letter shuffles. **Enigma** takes inspiration from physical multi-rotor encryption (such as the historic Enigma machine) and combines it with modern media hashing:

1. **Any Media as a Key**: Point the program to any image file or music/sound file.
2. **Turn Media into Code**: The program converts the file's raw binary data into a cryptographic **SHA-256 fingerprint**.
3. **95-Character Scrambling**: Derives a complete substitution map covering lowercase letters (`a-z`), uppercase letters (`A-Z`), digits (`0-9`), and symbols/spaces.
4. **Multi-Key Combination**: Choose 1 key, or combine **Image + Music**, or chain **3 or more keys** together into a layered cascade.

---

## How the Encryption Works

### 1. Media-to-Code Transformation

Every media file is made of thousands or millions of binary bytes. When an image or music file is loaded, the engine hashes its raw bytes using **SHA-256**:

```
┌─────────────────────────────────┐
│ Media File (Image or Music)     │
│   • photo.png (RGB pixels)      │
│   • song.mp3  (Audio samples)   │
└────────────────┬────────────────┘
                 │ Read raw bytes
                 ▼
┌─────────────────────────────────┐
│ Cryptographic SHA-256 Hashing   │
│   SHA-256(MediaBytes)           │
└────────────────┬────────────────┘
                 │ Produces 64-character hex code
                 ▼
┌────────────────────────────────────────────────────────┐
│ Code Fingerprint:                                      │
│   "7d9f2a4b8c1e6035...d4a8" (64 Hex Characters)      │
└────────────────────────────────────────────────────────┘
```

- **Deterministic**: The exact same image or music file always produces the exact same cryptographic code.
- **Avalanche Effect**: If even 1 pixel or 1 audio sample changes, the resulting code changes completely, generating a totally different cipher key.

### 2. Deterministic Key Derivation (95 Characters)

The 64-character SHA-256 code is converted into a 256-bit integer seed that initializes a deterministic pseudo-random generator. This generator shuffles all **95 printable ASCII characters**:

| Category | Character Count | Elements |
|---|:---:|---|
| **Lowercase Alphabet** | 26 | `abcdefghijklmnopqrstuvwxyz` |
| **Uppercase Alphabet** | 26 | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| **Numbers / Digits** | 10 | `0123456789` |
| **Symbols & Space** | 33 | ``!"#$%&'()*+,-./:;<=>?@[\]^_`{&#124;}~ `` *(plus space)* |
| **Total Set** | **95** | Complete printable character space |

Every character in the 95-character set is mapped **1-to-1** (bijective) to a substitute character. No character is ignored or skipped.

### 3. Multi-Key Cascade Encryption (1, 2, or More Keys)

You can choose to encrypt using:
- **1 Key**: Single layer (e.g., Image Key #1).
- **2 Keys (Combined Image + Music)**: Double layer (e.g., Key #1 + Key #2).
- **3 or More Keys**: Triple or N-layer multi-rotor pipeline.

When multiple keys are selected, the message passes through each key sequentially, exactly like electrical signals passing through the rotors of an Enigma machine:

```text
Plaintext:  "Secret 2026: Hello World! #TopSecret"
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 1: Key #1 (🖼️ Image Key - "key_image_1.bmp")   │
│  SHA-256: 24073ca421286a86...                          │
└──────────────────┬─────────────────────────────────────┘
                   │ Intermediate Ciphertext 1
                   ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 2: Key #2 (🎵 Music Key - "key_music_2.wav")   │
│  SHA-256: 8b4e7c1039da5f21...                          │
└──────────────────┬─────────────────────────────────────┘
                   │ Intermediate Ciphertext 2
                   ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 3: Key #3 (📁 Additional Key - optional)        │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
Final Ciphertext:  "w$2a9%K;r!o8fc...5#rFCtt"
```

Each subsequent layer scrambles the output of the previous layer, compounding confusion and diffusion across the entire text.

### 4. Reversing the Cascade (Decryption)

To decrypt a multi-key message, the ciphertext must pass through the **inverse mappings in exact reverse order (LIFO - Last In, First Out)**:

```text
Final Ciphertext:  "w$2a9%K;r!o8fc...5#rFCtt"
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  STEP 1: Invert Layer 2 (🎵 Music Key #2)              │
│  Applies inverse mapping of Key #2                     │
└──────────────────┬─────────────────────────────────────┘
                   │ Restores Intermediate Ciphertext 1
                   ▼
┌────────────────────────────────────────────────────────┐
│  STEP 2: Invert Layer 1 (🖼️ Image Key #1)              │
│  Applies inverse mapping of Key #1                     │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
Original Plaintext: "Secret 2026: Hello World! #TopSecret"
```

The user simply enters the key combination (e.g., `1, 2`), and the program automatically unwinds the layers in reverse order.

---

## System Architecture

### Workflow & Pipeline Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER TERMINAL / CLI                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Launch
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       main.py (Application Entry Point)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Initializes & Routes
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     menu_module.py (Interactive Menus)                      │
├─────────────────┬─────────────────┬───────────────────┬─────────────────────┤
│   [Option A]    │   [Option B]    │    [Option C]     │     [Option D]      │
│     Encrypt     │     Decrypt     │   Generate Key    │  Manage & Inspect   │
│     Message     │     Message     │   (Audio/Image)   │     (keys.json)     │
└────────┬────────┴────────┬────────┴─────────┬─────────┴──────────┬──────────┘
         │                 │                  │                    │
         │  Select 1, 2,   │                  │ Scan / Load        │ Key Mgmt
         │  or N Keys      │                  ▼                    ▼
         │                 │         ┌───────────────────┐ ┌──────────────────┐
         └────────┬────────┘         │   key_module.py   │ │  keys.json Store │
                  ▼                  │ • media/audio/    │ │ • JSON metadata  │
┌──────────────────────────────────┐ │ • media/images/   │ │ • View / Inspect │
│     Multi-Key Selection Flow     │ │ • SHA-256 Hashing │ │ • Delete Key     │
│  (Single, Double, or N-Cascade)  │ └─────────┬─────────┘ └──────────────────┘
└─────────────────┬────────────────┘           │ Saves Key
                  │ Resolved Key Dicts         ▼
                  │                  ┌───────────────────┐
                  ├─────────────────►│     keys.json     │
                  │                  └───────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    media_cipher.py (MultiKeyCipher Engine)                  │
│                                                                             │
│   Input Message (Plaintext)                                                 │
│        │                                                                    │
│        ▼                                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ ROTOR LAYER 1 (Key A)  • 95-Character Bijective Character Mapping   │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │ Intermediate Ciphertext 1            │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ ROTOR LAYER 2 (Key B)  • Compounded Multi-Rotor Scrambling          │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │ Intermediate Ciphertext 2            │
│                                      ▼                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ ROTOR LAYER N (Key N)  • N-th Sequential Ciphertext Scrambling      │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│                           Final Output (Ciphertext)                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Output & Audit Logging
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
        ┌─────────────────────────────┐ ┌─────────────────────────────┐
        │      Rich Terminal UI       │ │     Audit Log Storage       │
        │ • Styled Result Panel Card  │ │ • Encryption.txt            │
        │ • Rotor Pipeline Table View │ │ • Decryption.txt            │
        └─────────────────────────────┘ └─────────────────────────────┘
```

### Repository Structure

```
Enigma Machine/
├── main.py                   # Main CLI entry point and menu router
├── menu_module.py            # Menu UI flows, input validation, and dispatchers
├── key_module.py             # Key store, JSON persistence, image/music key registration
├── media_cipher.py           # Core cryptographic engine (Image + Music + Multi-Key Cascade)
├── image_key_cipher.py       # Backward-compatibility alias re-exporting media_cipher
├── utilities_module.py       # Cross-platform terminal helpers, progress animations
├── mesage_encryptor.py       # Cryptographic message data model with media metadata
├── test_enigma.py            # Automated unit test suite (unittest)
├── keys.json                 # Persistent key storage file (auto-generated)
├── media/                    # Media assets used for key generation
│   ├── audio/                # Audio files (e.g., Howling sound.mp3)
│   └── images/               # Image files (e.g., crazy cat.jpg, orange cat.jpg)
├── key_media/                # Directory for generated sample key images & music (auto-created)
├── Encryption.txt            # Audit log for encryption operations (auto-generated)
├── Decryption.txt            # Audit log for decryption operations (auto-generated)
├── requirements.txt          # Python dependencies (rich)
├── .gitignore                # Ignored cache, logs, and persistent data
└── README.md                 # Complete project documentation
```

### Module Breakdown

| Module | Primary Symbol / Class | Description |
|---|---|---|
| [main.py](main.py) | `main()`, `main_menu()` | Registers main menu options, dispatches user actions, and manages clean exit routines. |
| [menu_module.py](menu_module.py) | [`Menu`](menu_module.py), `encrypt_menu()`, `decrypt_menu()`, `key_selection_menu()` | Coordinates user prompts, validates single and multi-key inputs, and runs animated progress bars. |
| [key_module.py](key_module.py) | `register_media_file()`, `generate_sample_image()`, `generate_sample_music()`, `parse_and_resolve_keys()` | Manages Image and Music keys, persists metadata in `keys.json`, and parses multi-key arguments. |
| [media_cipher.py](media_cipher.py) | [`MultiKeyCipher`](media_cipher.py), `create_sample_bmp_image()`, `create_sample_wav_music()` | Converts image and audio files into cryptographic codes, executes multi-layer cascade substitution, and logs results. |
| [utilities_module.py](utilities_module.py) | `clear_screen()`, `progress_bar()`, `display_header()`, `prompt_delay()` | Terminal clearing, animated progress bars, and standardized visual banners. |
| [test_enigma.py](test_enigma.py) | `TestMediaCipher`, `TestKeyModule`, `TestMenuModule` | 14 automated unit tests validating single-key, double-key (image + music), triple-key roundtrips, and persistence. |

---

## Cryptographic Mechanics & Complexity

### Full 95-Character Printable Set

The cipher maps every printable ASCII character (codes 32 to 126 inclusive):
- **Alphabet**: `a-z` (26) and `A-Z` (26)
- **Numbers**: `0-9` (10)
- **Symbols & Space**: ``!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ `` (33 characters including space)

Characters outside this set (such as multiline newlines `\n` and tabs `\t`) are preserved, ensuring formatted files and paragraphs retain their structure while all text content is thoroughly scrambled.

### Instant O(1) Hash Map Lookups

Every key layer precomputes an inverse dictionary mapping upon initialization:

```python
self.inverse_key = {v: k for k, v in self.key.items()}
```

- **Per-Character Lookup**: `O(1)` time complexity.
- **Single-Layer Execution**: `O(N)` where `N` is the message length.
- **M-Layer Multi-Key Cascade**: `O(M × N)` total time across `M` keys.

### Keyspace & Compounded Entropy

For a single key layer over 95 characters:
```math
\text{Keyspace}_1 = 95! \approx 1.0329 \times 10^{148}
```

When combining $M$ independent media keys in a cascade:
```math
\text{Compounded Permutation States} \approx (95!)^M
```

For a 2-key combination (Image + Music):
```math
(95!)^2 \approx 1.067 \times 10^{296}
```

---

## Installation & Quick Start

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/dnzdaorick/Enigma-Machine.git
   cd "Enigma-Machine"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Only requires `rich` for terminal UI styling; all image and audio generators use Python's built-in standard library with zero third-party dependencies).*

3. **Launch Application**:
   ```bash
   py main.py          # Windows
   python3 main.py     # macOS / Linux
   ```

---

## Interactive CLI Walkthrough

### Main Menu Navigation

```text
╭──────────────────────────────────────────────────╮
│                      ENIGMA                      │
│            Cryptographic Media Engine            │
╰──────────────────────────────────────────────────╯

[A] - Encrypt Message
[B] - Decrypt Message
[C] - Generate Media Key
[D] - Manage & Inspect Keys
[X] - Exit Program

Enter option:
```

---

### Option A: Encrypt Message

1. Select option **`A`**.
2. Type the message to encrypt:
   ```text
   Enter message to encrypt: Top Secret 2026: Project Enigma [Launch Code #99!]
   ```
3. A table of available keys is displayed. You can:
   - **Use 1 key**: Type `1`
   - **Combine 2 keys**: Type `1, 2` (e.g. 1, 2 to combine keys)
   - **Combine 3 or more keys**: Type `1, 2, 3`
   - **Use direct files**: Type `photo.png, song.mp3`
4. An animated progress bar simulates cipher execution:
   ```text
   Encrypting (#1 + #2)... ━━━━━━━━━━ 100% 0.2s
   ```
5. A stylized **ENCRYPTION RESULT** card appears, displaying:
   - The input string.
   - The final encrypted ciphertext.
   - A clean **Pipeline Table** showing each key stage, media icon, file name, and SHA-256 fingerprint.
6. The operation is logged to `Encryption.txt`.

---

### Option B: Decrypt Message

1. Select option **`B`**.
2. Enter or paste the ciphertext.
3. Select the same key or key combination used during encryption (e.g. `1, 2`).
4. The cipher executes the inverse decryption pipeline in reverse order.
5. The original plaintext is restored and logged to `Decryption.txt`.

---

### Option C: Generate Media Key

Select option **`C`** to generate a key from your media folder (`media/audio` and `media/images`):

1. Scans `media/` and automatically lists all available media files:
   ```text
   ╭───────────────────────── Available Media Files ─────────────────────────╮
   │  #   │   Type   │ File Name         │ Folder        │        Size       │
   ├──────┼──────────┼───────────────────┼───────────────┼───────────────────┤
   │  1   │ 🎵 Audio │ Howling sound.mp3 │ media/audio   │         396.6 KB  │
   │  2   │ 🖼️ Image │ crazy cat.jpg     │ media/images  │           3.5 KB  │
   │  3   │ 🖼️ Image │ orange cat.jpg    │ media/images  │          13.5 KB  │
   ╰──────┴──────────┴───────────────────┴───────────────┴───────────────────╯
   ```
2. Enter a number to select a file (e.g. `1` for default audio, `2` for an image, or `1, 2` for multiple), OR type a custom file path directly.
3. Automatically computes the SHA-256 fingerprint, derives the 95-character substitution key, and registers it in `keys.json`.

---

### Option D: Manage & Inspect Keys

Select option **`D`** to manage stored keys:

```text
[1] Show All Keys
[2] Inspect Key Mapping
[3] Delete a Key
[4] Return to Main Menu
```

- **Show All Keys**: Lists all enrolled keys with icons (🖼️ Image / 🎵 Music), filenames, SHA-256 codes, and timestamps.
- **Inspect Key Mapping**: Displays full 64-character SHA-256 code, file size, and complete character substitution tables (Alphabet, Numbers, Symbols).
- **Delete Key**: Permanently deletes a key from active memory and updates `keys.json`.

---

## Key Storage & JSON Persistence

All keys and metadata are saved automatically to `keys.json`:

```json
{
  "1": {
    "created_at": "2026-10-18 20:14:00",
    "file_path": "key_media/key_image_1.bmp",
    "media_type": "image",
    "code": "24073ca421286a863641629cc32f909d637d7627737da1e7aa387f44d7731302",
    "byte_size": "49206",
    "mapping": {
      "a": "x",
      "0": "%",
      "!": "K"
    }
  },
  "2": {
    "created_at": "2026-10-18 20:14:05",
    "file_path": "key_media/key_music_2.wav",
    "media_type": "music",
    "code": "8b4e7c1039da5f214f828a476ce1e98d893fae2056d028b1e4c730198aa47b62",
    "byte_size": "88244",
    "mapping": {
      "x": "9",
      "%": "M",
      "K": "b"
    }
  }
}
```

---

## Audit Logging System

Every cryptographic operation appends a detailed entry to `Encryption.txt` or `Decryption.txt`:

```text
------------------------------------------------------------------------------------------------------------------------
Sunday, October 18 2026 at 08:14 PM

Cipher Engine: Multi-Key Media Cipher (2 Layer(s))
Original Message: Top Secret 2026: Project Enigma [Launch Code #99!]
Key Combination: #1 (image) + #2 (music)
  [Layer 1] Key #1 (IMAGE) | File: key_media/key_image_1.bmp | SHA-256: 24073ca421286a86...
  [Layer 2] Key #2 (MUSIC) | File: key_media/key_music_2.wav | SHA-256: 8b4e7c1039da5f21...

Encryption Result: och}c#rac55$Rcr8t8K;r&#c5#rFCtt"r!3J[
------------------------------------------------------------------------------------------------------------------------
```

---

## Automated Unit Testing

Run the built-in test suite:

```bash
# Windows
py -m unittest test_enigma.py -v

# macOS / Linux
python3 -m unittest test_enigma.py -v
```

### Test Coverage Highlights:
- Media type detection (Image vs Music vs Binary Media).
- Deterministic code generation from image bytes and audio bytes.
- Single-key roundtrip encryption/decryption.
- **Two-key cascade roundtrip** (combining Image + Music keys).
- **Three-key cascade roundtrip**.
- Multi-key syntax resolution (`1`, `1, 2`, `1 2`, direct paths).
- Multiline newline preservation.
- JSON storage persistence and key deletion.

---

## Security Notice

This application implements a **Multi-Key Media Substitution Cipher**, designed for educational, demonstration, and personal text processing purposes.

> [!NOTE]
> Combining multiple media keys (Image + Music) significantly increases complexity through multi-rotor cascade layering ((95!)^M states). However, substitution ciphers remain distinguishable under statistical language frequency analysis when encrypting very large texts. For military or high-security production environments, use modern authenticated block ciphers like AES-256-GCM.

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
