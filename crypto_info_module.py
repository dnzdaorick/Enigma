"""Cryptographic Algorithm Information Module for Enigma Machine.

Provides concise, straight-to-the-point cryptographic summaries detailing
origin, use cases, pros, and cons for all algorithms in Enigma, highlighting
our custom-developed Media Key encryption engine.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from utilities_module import clear_screen, prompt_delay, display_header

console = Console()

ALGORITHM_DOSSIERS = {
    "media": {
        "title": "Media Key Cipher (Created by Us)",
        "badge": "★ Original Creation: Media Entropy Rotor",
        "type": "SHA-256 Hash-Seeded 95-Character Permutation",
        "key_space": "95! ≈ 1.03 × 10¹⁴⁸ (Full printable ASCII)",
        "origin": (
            "Created by us for this project. Converts any digital photo (JPG/PNG/BMP) or audio "
            "file (MP3/WAV) into an ultra-high-entropy 95-character rotor via SHA-256 binary fingerprinting."
        ),
        "use": (
            "Passwordless encryption, physical media key tokens, and multi-rotor cascade layering (e.g. Image + Music)."
        ),
        "pros": [
            "Avalanche Effect: Altering a single pixel or audio sample generates a totally different key.",
            "Immense keyspace: 95! (~10¹⁴⁸) states scrambles all letters, digits, spaces, and symbols.",
            "Eliminates guessable passwords by requiring physical possession of the media file.",
        ],
        "cons": [
            "Both communicating parties must possess the exact bit-for-bit identical media file.",
            "Lossy recompression (e.g. social media compression, audio re-encoding) alters bytes and breaks the key.",
        ],
    },
    "monoalphabetic": {
        "title": "Monoalphabetic Substitution Cipher",
        "badge": "🔤 Classical Single-Alphabet Substitution",
        "type": "Fixed Letter Permutation (A-Z)",
        "key_space": "26! ≈ 4.03 × 10²⁶ permutations",
        "origin": (
            "Formalized in the 9th century by Arab scholar Al-Kindi. Represents the classical "
            "foundation of single-alphabet substitution."
        ),
        "use": (
            "Historical military/diplomatic correspondence, puzzle games (cryptograms), and cryptanalysis education."
        ),
        "pros": [
            "Huge theoretical keyspace: 26! (> 400 septillion) defeats brute-force guessing.",
            "Instant O(1) character lookup with zero computational overhead.",
            "Preserves word lengths, spaces, numbers, and punctuation cleanly.",
        ],
        "cons": [
            "Vulnerable to frequency analysis: High-frequency letters (E, T, A) retain distinct patterns.",
            "Trivially cracked on short ciphertexts (25–50 characters) using statistical frequency attacks.",
        ],
    },
    "vigenere": {
        "title": "Vigenère Polyalphabetic Cipher",
        "badge": "🗝️ Polyalphabetic Modular Shift",
        "type": "Periodic Polyalphabetic Shift ((P + K) mod 26)",
        "key_space": "26^K (where K is keyword length)",
        "origin": (
            "Invented in 1553 by Giovan Battista Bellaso (later attributed to Vigenère). "
            "Defeated simple frequency analysis for over 300 years."
        ),
        "use": (
            "19th-century European diplomatic cables, telegraph communications, and the American Civil War."
        ),
        "pros": [
            "Flattens letter frequencies: The same letter encrypts to different characters depending on keyword position.",
            "Human-memorable: Easily keyed using memorable passphrases without needing codebooks.",
            "Preserves uppercase, lowercase, numbers, and symbols naturally.",
        ],
        "cons": [
            "Vulnerable to Kasiski examination and Index of Coincidence to deduce key length K.",
            "Once key length is known, reduces to K separate, easily cracked Caesar shifts.",
        ],
    },
    "xor": {
        "title": "Bitwise XOR Stream Cipher",
        "badge": "⚡ Boolean Vernam Keystream",
        "type": "Bitwise XOR Linear Stream (A ⊕ B)",
        "key_space": "2^(8×K) (Up to 2²⁵⁶+)",
        "origin": (
            "Invented in 1917 by Gilbert Vernam (AT&T); proven by Claude Shannon (1949) as the "
            "mathematical basis for the provably secure One-Time Pad."
        ),
        "use": (
            "Core building block of modern cryptography: ChaCha20, Salsa20, and AES counter mode (CTR/GCM)."
        ),
        "pros": [
            "Involutory symmetry: (A ⊕ B) ⊕ B = A (encryption and decryption are identical).",
            "Hardware speed: Executes in single CPU clock cycles directly on binary bytes.",
            "Unbreakable One-Time Pad if key is truly random, never reused, and as long as the message.",
        ],
        "cons": [
            "Catastrophic Two-Time Pad failure: Reusing a key leaks plaintext directly (C₁ ⊕ C₂ = P₁ ⊕ P₂).",
            "Zero integrity checking: Malleable bits can be flipped without detection.",
        ],
    },
    "cascade": {
        "title": "Multi-Key Cascade (Product Cipher)",
        "badge": "🛡️ Multi-Layer Product Cascade",
        "type": "Heterogeneous Rotor Cascade (Layer 1 → ... → Layer N)",
        "key_space": "Compound Product: KeySpace₁ × KeySpace₂ × ...",
        "origin": (
            "Claude Shannon (1949). Demonstrates that cascading distinct ciphers compounds confusion "
            "and diffusion to eliminate individual weaknesses."
        ),
        "use": (
            "Modern block cipher designs (AES rounds), onion routing (Tor), and defense-in-depth security enclaves."
        ),
        "pros": [
            "Destroys single-cipher weaknesses: Blends alphabet shifts, modular math, XOR bits, and media rotors.",
            "Defense-in-depth: If one key layer is compromised, remaining layers maintain confidentiality.",
        ],
        "cons": [
            "Requires all keys in exact reverse order (LIFO) to unwind.",
            "Processing time scales linearly with each added rotor layer (O(N)).",
        ],
    },
}


def render_algorithm_summary_panel(algo_key: str) -> Panel:
    """Returns a concise, straight-to-the-point Rich Panel summarizing an algorithm."""
    dossier = ALGORITHM_DOSSIERS.get(algo_key)
    if not dossier:
        return Panel(f"[red]Algorithm '{algo_key}' not found.[/red]")

    is_custom = (algo_key == "media")
    border_color = "bright_green" if is_custom else "cyan"

    pros_str = "\n".join(f"  [green]✓[/green] {p}" for p in dossier["pros"])
    cons_str = "\n".join(f"  [red]✗[/red] {c}" for c in dossier["cons"])

    summary_text = (
        f"[bold white]{dossier['badge']}[/bold white]\n"
        f"[dim]{dossier['type']} | Key Space: {dossier['key_space']}[/dim]\n\n"
        f"[bold cyan]Origin:[/bold cyan] {dossier['origin']}\n"
        f"[bold yellow]Use:[/bold yellow]    {dossier['use']}\n\n"
        f"[bold green]Strengths (Pros):[/bold green]\n{pros_str}\n\n"
        f"[bold red]Weaknesses (Cons):[/bold red]\n{cons_str}"
    )

    title_prefix = "★ " if is_custom else ""
    return Panel(
        summary_text,
        title=f"[bold {border_color}]{title_prefix}{dossier['title']}[/bold {border_color}]",
        border_style=border_color,
        padding=(0, 1),
    )


def display_algorithm_summary(algo_key: str) -> None:
    """Prints a concise, straight-to-the-point algorithm summary panel."""
    console.print(render_algorithm_summary_panel(algo_key))
    console.print()


KEY_OVERVIEW_DATA = {
    "media": {
        "name": "Media Keys (Image or Audio)",
        "badge": "★ Created by Us for Enigma",
        "concept": "Original creation for this project.\nSHA-256 hashes image or audio bytes into a 95-character rotor.",
        "pros": "• Extreme Avalanche Effect\n• No guessable passwords\n• Scrambles letters, digits, symbols",
        "cons": "• Requires exact bit-for-bit file\n• Broken by lossy recompression",
        "color": "bright_green",
    },
    "monoalphabetic": {
        "name": "Monoalphabetic Substitution Cipher",
        "badge": "Classical Substitution",
        "concept": "Formalized in the 9th Century.\nRandom 1-to-1 letter permutation across A-Z.",
        "pros": "• Instant O(1) table lookup\n• Preserves casing and spacing",
        "cons": "• Broken by frequency analysis\n• Weak on short texts (25–50 chars)",
        "color": "cyan",
    },
    "vigenere": {
        "name": "Vigenère Polyalphabetic Cipher",
        "badge": "Classical Polyalphabetic",
        "concept": "Invented in 1553.\nKeyword-driven modular alphabet shift ((P + K) mod 26).",
        "pros": "• Flattens letter frequencies\n• Human-memorable passphrase",
        "cons": "• Vulnerable to Kasiski test\n• Key length leakage breaks it",
        "color": "yellow",
    },
    "xor": {
        "name": "Bitwise XOR Stream Cipher",
        "badge": "Classical Boolean Stream",
        "concept": "Patented in 1917 by Gilbert Vernam.\nDirect bitwise Boolean addition (A ⊕ B).",
        "pros": "• Hardware CPU ALU speed\n• Symmetric: (A ⊕ B) ⊕ B = A\n• Unbreakable One-Time Pad potential",
        "cons": "• Two-time pad key reuse leak\n• No message integrity verification",
        "color": "magenta",
    },
}


def display_key_generation_overview(algo_key: str | None = None) -> None:
    """Renders a concise, straight-to-the-point cryptographic overview table for the selected algorithm."""
    if algo_key and algo_key in KEY_OVERVIEW_DATA:
        item = KEY_OVERVIEW_DATA[algo_key]
        table = Table(
            title=f"[bold {item['color']}]Key Generation Cryptographic Overview: {item['name']}[/bold {item['color']}]",
            box=box.ROUNDED,
            header_style="bold bright_blue",
            show_lines=True,
            expand=True,
        )
        table.add_column("Classification", style="bold white", ratio=2)
        table.add_column("Origin & Concept", style="cyan", ratio=5)
        table.add_column("Strengths (Pros)", style="green", ratio=4)
        table.add_column("Weaknesses (Cons)", style="red", ratio=3)

        table.add_row(
            item["badge"],
            item["concept"],
            item["pros"],
            item["cons"],
        )
        console.print(table)
        console.print()
        return

    table = Table(
        title="[bold cyan]Key Generation Cryptographic Overview[/bold cyan]",
        box=box.ROUNDED,
        header_style="bold bright_blue",
        show_lines=True,
        expand=True,
    )
    table.add_column("Option", style="bold white", ratio=2)
    table.add_column("Origin & Concept", style="cyan", ratio=5)
    table.add_column("Strengths (Pros)", style="green", ratio=4)
    table.add_column("Weaknesses (Cons)", style="red", ratio=3)

    for key, item in KEY_OVERVIEW_DATA.items():
        table.add_row(
            f"[bold {item['color']}]{item['badge']}[/bold {item['color']}]",
            item["concept"],
            item["pros"],
            item["cons"],
        )

    console.print(table)
    console.print()


def display_algorithm_dossier(algo_key: str) -> None:
    """Renders a concise, straight-to-the-point cryptographic dossier for a given algorithm."""
    clear_screen()
    display_header("ENIGMA", "Algorithm Dossier")
    display_algorithm_summary(algo_key)
    prompt_delay()
    clear_screen()


def display_comparison_matrix() -> None:
    """Renders a comparative matrix table benchmarking all supported algorithms."""
    clear_screen()
    display_header("ENIGMA", "Algorithm Comparative Benchmark")

    matrix_table = Table(
        title="Cryptographic Architecture Matrix",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    matrix_table.add_column("Algorithm", style="bold white", width=22)
    matrix_table.add_column("Domain / Math", style="cyan", width=16)
    matrix_table.add_column("Key Space", style="yellow", width=18)
    matrix_table.add_column("Freq Analysis", style="magenta", justify="center", width=15)
    matrix_table.add_column("Speed", style="green", justify="center", width=10)
    matrix_table.add_column("Primary Tradeoff", style="red", width=32)

    matrix_table.add_row(
        "🖼️ Media (Created by Us)",
        "SHA-256 + PRNG",
        "95! ≈ 1.0×10¹⁴⁸",
        "Resistant (95 Ch)",
        "Fast",
        "Requires exact uncompressed file",
    )
    matrix_table.add_row(
        "🔤 Monoalphabetic",
        "Permutation",
        "26! ≈ 4.0×10²⁶",
        "Vulnerable",
        "Instant",
        "Single-letter frequency attacks",
    )
    matrix_table.add_row(
        "🗝️ Vigenère",
        "Modulo 26 Arithmetic",
        "26^K (Length K)",
        "Flattened",
        "Instant",
        "Kasiski & Index of Coincidence",
    )
    matrix_table.add_row(
        "⚡ XOR Stream",
        "Bitwise Boolean",
        "2^(8×K) (Up to 2²⁵⁶)",
        "Defeated",
        "Hardware ALU",
        "Two-time pad key reuse & malleability",
    )
    matrix_table.add_row(
        "🛡️ Multi Cascade",
        "Product Cipher",
        "Compound Product",
        "Immune",
        "Linear O(N)",
        "Requires all keys in reverse order",
    )

    console.print(matrix_table)
    console.print()
    prompt_delay()
    clear_screen()


def algorithm_info_menu() -> None:
    """Interactive educational hub allowing users to explore dossiers and comparative benchmarks."""
    while True:
        display_header("ENIGMA", "Cryptographic Knowledge Base")
        console.print("[1] Media Key Cryptography [bold bright_green](Created by Us)[/bold bright_green]", style="bold cyan")
        console.print("[2] Monoalphabetic Substitution Cipher", style="bold green")
        console.print("[3] Vigenère Polyalphabetic Cipher", style="bold yellow")
        console.print("[4] XOR Stream Cipher", style="bold magenta")
        console.print("[5] Multi-Key Cascade Architecture (Product Cipher)", style="bold bright_blue")
        console.print("[6] Comparative Benchmark Matrix", style="bold bright_cyan")
        console.print("[7] Return to Main Menu", style="bold white")
        console.print()

        choice = Prompt.ask(
            "Select algorithm to inspect",
            choices=["1", "2", "3", "4", "5", "6", "7"],
            default="1",
        )

        if choice == "1":
            display_algorithm_dossier("media")
        elif choice == "2":
            display_algorithm_dossier("monoalphabetic")
        elif choice == "3":
            display_algorithm_dossier("vigenere")
        elif choice == "4":
            display_algorithm_dossier("xor")
        elif choice == "5":
            display_algorithm_dossier("cascade")
        elif choice == "6":
            display_comparison_matrix()
        elif choice == "7":
            clear_screen()
            break
