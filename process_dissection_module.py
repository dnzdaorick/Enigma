"""Cryptographic Process Dissection Module for Enigma Machine.

Deconstructs and dissects the cryptographic process character-by-character and byte-by-byte:
- Shows the mathematical formula applied at each stage.
- Reveals binary bitwise operations, modular shifts, and dictionary substitutions.
- Provides deep inspection for both forward encryption and reverse decryption unwinding.
- Implements linked encryption/decryption execution with dual verification.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from utilities_module import clear_screen, prompt_delay, display_header
from cipher_module import (
    vigenere_encrypt,
    vigenere_decrypt,
    xor_encrypt,
    xor_decrypt,
)
from media_cipher import MultiKeyCipher

console = Console()


def dissect_monoalphabetic_layer(
    text: str, mapping: dict[str, str], is_decrypt: bool = False
) -> Table:
    """Renders a character-by-character dissection table for a monoalphabetic substitution layer."""
    title_op = "Decryption (Inverse Map)" if is_decrypt else "Encryption (Substitution)"
    table = Table(
        title=f"Monoalphabetic Dissection: {title_op}",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Pos", justify="center", style="dim", width=5)
    table.add_column("Input Char", justify="center", style="bold yellow", width=12)
    table.add_column("ASCII (Dec)", justify="center", style="cyan", width=12)
    table.add_column("Action / Rule", justify="left", style="green", width=30)
    table.add_column("Output Char", justify="center", style="bold magenta", width=12)

    active_map = {v: k for k, v in mapping.items()} if is_decrypt else mapping
    sample_text = text[:32]  # Dissect first 32 characters for clarity

    for idx, c in enumerate(sample_text, start=1):
        dec_code = ord(c)
        c_disp = "' '" if c == " " else c
        if c in active_map:
            out_c = active_map[c]
            out_disp = "' '" if out_c == " " else out_c
            if c.isalpha():
                rule = f"Alphabet Permutation ('{c_disp}' → '{out_disp}')"
            else:
                rule = f"Symbol Identity Preserve ('{c_disp}')"
        else:
            out_c = c
            out_disp = c_disp
            rule = "Unmapped Passthrough"

        table.add_row(str(idx), c_disp, str(dec_code), rule, out_disp)

    return table


def dissect_vigenere_layer(
    text: str, key: str, is_decrypt: bool = False
) -> Table:
    """Renders a mathematical modular arithmetic dissection table for a Vigenère layer."""
    title_op = "Decryption (C - K mod 26)" if is_decrypt else "Encryption (P + K mod 26)"
    table = Table(
        title=f"Vigenère Dissection: {title_op} [Key: '{key}']",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Pos", justify="center", style="dim", width=5)
    table.add_column("Text Char", justify="center", style="bold yellow", width=10)
    table.add_column("Key Char", justify="center", style="bold green", width=10)
    table.add_column("Shift", justify="center", style="cyan", width=8)
    table.add_column("Mathematical Formula", justify="left", style="white", width=35)
    table.add_column("Result Char", justify="center", style="bold magenta", width=12)

    clean_key = [c for c in key if c.isalpha()]
    if not clean_key:
        clean_key = list("KEY")
    k_len = len(clean_key)
    sample_text = text[:32]
    k_idx = 0

    for idx, c in enumerate(sample_text, start=1):
        c_disp = "' '" if c == " " else c
        if c.isalpha():
            k_char = clean_key[k_idx % k_len]
            if is_decrypt:
                if "a" <= c <= "z":
                    shift = ord(k_char.lower()) - ord("a")
                    p_idx = ord(c) - ord("a")
                    out_idx = (p_idx - shift) % 26
                    out_c = chr(out_idx + ord("a"))
                    formula = f"({p_idx} - {shift}) mod 26 = {out_idx}"
                else:
                    shift = ord(k_char.upper()) - ord("A")
                    p_idx = ord(c) - ord("A")
                    out_idx = (p_idx - shift) % 26
                    out_c = chr(out_idx + ord("A"))
                    formula = f"({p_idx} - {shift}) mod 26 = {out_idx}"
            else:
                if "a" <= c <= "z":
                    shift = ord(k_char.lower()) - ord("a")
                    p_idx = ord(c) - ord("a")
                    out_idx = (p_idx + shift) % 26
                    out_c = chr(out_idx + ord("a"))
                    formula = f"({p_idx} + {shift}) mod 26 = {out_idx}"
                else:
                    shift = ord(k_char.upper()) - ord("A")
                    p_idx = ord(c) - ord("A")
                    out_idx = (p_idx + shift) % 26
                    out_c = chr(out_idx + ord("A"))
                    formula = f"({p_idx} + {shift}) mod 26 = {out_idx}"

            table.add_row(str(idx), c_disp, k_char, f"{'+' if not is_decrypt else '-'}{shift}", formula, out_c)
            k_idx += 1
        else:
            table.add_row(str(idx), c_disp, "-", "0", "Preserve non-alphabetic", c_disp)

    return table


def dissect_xor_layer(
    text: str, key: str, is_decrypt: bool = False
) -> Table:
    """Renders a bitwise binary XOR dissection table."""
    title_op = "Decryption (Hex → XOR Bytes → Text)" if is_decrypt else "Encryption (Text → XOR Bytes → Hex)"
    table = Table(
        title=f"XOR Dissection: {title_op} [Key: '{key[:12]}...']",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Byte #", justify="center", style="dim", width=6)
    table.add_column("Input Char/Hex", justify="center", style="bold yellow", width=15)
    table.add_column("Input Byte", justify="center", style="cyan", width=12)
    table.add_column("Key Byte", justify="center", style="green", width=12)
    table.add_column("Bitwise XOR Operation (A ⊕ B)", justify="left", style="white", width=32)
    table.add_column("Output Result", justify="center", style="bold magenta", width=15)

    key_bytes = key.encode("utf-8")
    k_len = len(key_bytes) if key_bytes else 1

    if is_decrypt:
        # Decryption input is hex string
        try:
            cipher_bytes = bytes.fromhex(text.strip())
        except (ValueError, TypeError):
            cipher_bytes = text.encode("utf-8")
        sample_bytes = cipher_bytes[:16]

        for idx, b in enumerate(sample_bytes, start=1):
            k_b = key_bytes[(idx - 1) % k_len]
            x_b = b ^ k_b
            out_c = chr(x_b) if 32 <= x_b <= 126 else f"\\x{x_b:02x}"
            in_hex = f"0x{b:02X}"
            in_bin = f"{b:08b}"
            key_bin = f"{k_b:08b}"
            xor_math = f"{in_bin} ⊕ {key_bin}"
            table.add_row(str(idx), in_hex, f"{b} ({in_bin})", f"'{chr(k_b)}' ({key_bin})", xor_math, f"'{out_c}' (0x{x_b:02X})")
    else:
        text_bytes = text.encode("utf-8")
        sample_bytes = text_bytes[:16]

        for idx, b in enumerate(sample_bytes, start=1):
            k_b = key_bytes[(idx - 1) % k_len]
            x_b = b ^ k_b
            in_c = chr(b) if 32 <= b <= 126 else f"\\x{b:02x}"
            in_bin = f"{b:08b}"
            key_bin = f"{k_b:08b}"
            xor_math = f"{in_bin} ⊕ {key_bin} = {x_b:08b}"
            table.add_row(str(idx), f"'{in_c}'", in_bin, f"'{chr(k_b)}' ({key_bin})", xor_math, f"0x{x_b:02X}")

    return table


def dissect_media_layer(
    text: str, mapping: dict[str, str], meta: dict[str, str], is_decrypt: bool = False
) -> Table:
    """Renders a character transformation dissection table for a media key (Image / Audio)."""
    m_type = meta.get("media_type", "media").capitalize()
    src = os.path.basename(meta.get("file_path", meta.get("image_path", "Media File")))
    title_op = "Decryption (Inverse PRNG Shuffle)" if is_decrypt else "Encryption (PRNG Permutation)"

    table = Table(
        title=f"{m_type} Key Dissection: {title_op} [Source: '{src}']",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Pos", justify="center", style="dim", width=5)
    table.add_column("Input Char", justify="center", style="bold yellow", width=12)
    table.add_column("ASCII", justify="center", style="cyan", width=8)
    table.add_column("Action / Mapping Rule", justify="left", style="green", width=35)
    table.add_column("Output Char", justify="center", style="bold magenta", width=12)

    active_map = {v: k for k, v in mapping.items()} if is_decrypt else mapping
    sample_text = text[:32]

    for idx, c in enumerate(sample_text, start=1):
        dec_code = ord(c)
        c_disp = "' '" if c == " " else c
        out_c = active_map.get(c, c)
        out_disp = "' '" if out_c == " " else out_c
        rule = f"SHA-256 Seeded Map: '{c_disp}' → '{out_disp}'"
        table.add_row(str(idx), c_disp, str(dec_code), rule, out_disp)

    return table


def dissect_full_pipeline(
    message: str,
    key_layers: list[tuple[str, dict[str, str], dict[str, str]]],
    operation: str = "encrypt",
) -> None:
    """Renders the comprehensive multi-layer character-by-character mathematical dissection."""
    clear_screen()
    op_label = "Encryption (Forward Cascade)" if operation == "encrypt" else "Decryption (Reverse Unwinding)"
    display_header("ENIGMA", f"Cryptographic Dissection Studio: {op_label}")

    overview_text = (
        f"[bold cyan]Input Message:[/bold cyan]  {message}\n"
        f"[bold cyan]Cascade Depth:[/bold cyan]  {len(key_layers)} Key Layer(s)\n"
        f"[dim]The tables below dissect the exact mathematical transformation performed at each layer.[/dim]"
    )
    console.print(Panel(overview_text, title="Dissection Overview", border_style="bright_blue"))

    if operation == "encrypt":
        layers_to_run = list(key_layers)
    else:
        from media_cipher import MultiKeyCipher
        layers_to_run = MultiKeyCipher.determine_unwind_sequence(key_layers, message)
    current_text = message

    for step_idx, (key_id, mapping, meta) in enumerate(layers_to_run, start=1):
        cipher_type = meta.get("cipher_type", meta.get("media_type", "media")).lower()
        key_label = meta.get("file_path", f"Key #{key_id}")
        code_snip = meta.get("code", meta.get("image_code", "N/A"))[:16]

        console.print(
            f"\n[bold white]═══ Stage {step_idx}/{len(layers_to_run)}: Key #{key_id} ({cipher_type.upper()}) | SHA: {code_snip}... ═══[/bold white]"
        )

        if cipher_type == "monoalphabetic":
            tbl = dissect_monoalphabetic_layer(current_text, mapping, is_decrypt=(operation == "decrypt"))
            if operation == "encrypt":
                current_text = "".join(mapping.get(c, c) for c in current_text)
            else:
                inv = {v: k for k, v in mapping.items()}
                current_text = "".join(inv.get(c, c) for c in current_text)
        elif cipher_type == "vigenere":
            kw = meta.get("key_value", "")
            tbl = dissect_vigenere_layer(current_text, kw, is_decrypt=(operation == "decrypt"))
            if operation == "encrypt":
                current_text = vigenere_encrypt(current_text, kw)
            else:
                current_text = vigenere_decrypt(current_text, kw)
        elif cipher_type == "xor":
            k_val = meta.get("key_value", "")
            tbl = dissect_xor_layer(current_text, k_val, is_decrypt=(operation == "decrypt"))
            if operation == "encrypt":
                current_text = xor_encrypt(current_text, k_val)
            else:
                current_text = xor_decrypt(current_text, k_val)
        else:
            tbl = dissect_media_layer(current_text, mapping, meta, is_decrypt=(operation == "decrypt"))
            if operation == "encrypt":
                current_text = "".join(mapping.get(c, c) for c in current_text)
            else:
                inv = {v: k for k, v in mapping.items()}
                current_text = "".join(inv.get(c, c) for c in current_text)

        console.print(tbl)
        console.print(f"[bold cyan]Stage Output Preview:[/bold cyan] {current_text[:60]}{'...' if len(current_text) > 60 else ''}")

    console.print(
        Panel(
            f"[bold green]Final {operation.capitalize()} Result:[/bold green]\n{current_text}",
            title="Pipeline Completed",
            border_style="green",
        )
    )
    console.print()
    prompt_delay()
    clear_screen()


def linked_encrypt_and_decrypt_mode() -> None:
    """Executes linked encryption and decryption side-by-side with live verification and dissection."""
    from key_module import key_selection_menu

    display_header("ENIGMA", "Linked Encrypt & Decrypt")
    console.print(
        Panel(
            "[bold white]Linked Cryptographic Execution[/bold white]\n"
            "This mode takes your plaintext, encrypts it through your chosen key cascade,\n"
            "and immediately links it into the inverse decryption pipeline.\n"
            "It validates roundtrip mathematical symmetry and allows instant character-level dissection.",
            border_style="cyan",
        )
    )

    message = input("Enter plaintext message: ").strip()
    if not message:
        console.print("[yellow]Empty message entered.[/yellow]")
        prompt_delay()
        return

    selection = key_selection_menu(operation="encrypt")
    if not selection:
        clear_screen()
        return

    layer_names = [f"#{k_id}" for k_id, _, _ in selection]
    key_desc = " + ".join(layer_names)

    # 1. Forward Encryption Pass
    enc_cipher = MultiKeyCipher(message, selection, show_ui=False)
    ciphertext = enc_cipher.encrypt()

    # 2. Linked Reverse Decryption Pass
    dec_cipher = MultiKeyCipher(ciphertext, selection, show_ui=False)
    restored_text = dec_cipher.decrypt()

    # 3. Verification Check
    is_exact_match = (message == restored_text)
    match_badge = (
        "[bold green]✓ ROUNDTRIP INTEGRITY VERIFIED (100% Exact Match)[/bold green]"
        if is_exact_match
        else "[bold red]✗ INTEGRITY MISMATCH[/bold red]"
    )

    clear_screen()
    display_header("ENIGMA", "Linked Cryptographic Result")

    result_panel = (
        f"[cyan]Plaintext (Input):[/cyan]   {message}\n"
        f"[bold yellow]Ciphertext (Encrypted):[/bold yellow] {ciphertext}\n"
        f"[bold green]Decrypted (Restored):[/bold green]   {restored_text}\n\n"
        f"Key Combination:   [bold white]{key_desc}[/bold white] ({len(selection)} Layer(s))\n"
        f"Verification:      {match_badge}"
    )
    console.print(Panel(result_panel, title="Linked Dual Pipeline", border_style="bright_blue"))

    # Save to both logs
    enc_cipher.save_encryption_to_file(key_desc, ciphertext)
    dec_cipher.save_decryption_to_file(key_desc, restored_text)
    console.print("[dim]Audit logs appended to Encryption.txt and Decryption.txt[/dim]\n")

    console.print("[1] Dissect Forward Encryption Process (Step-by-Step Math)", style="bold cyan")
    console.print("[2] Dissect Reverse Decryption Process (Step-by-Step Math)", style="bold yellow")
    console.print("[3] Return to Main Menu", style="bold white")
    console.print()

    action = input("Choose option [default 3]: ").strip()
    if action == "1":
        dissect_full_pipeline(message, selection, operation="encrypt")
    elif action == "2":
        dissect_full_pipeline(ciphertext, selection, operation="decrypt")
    else:
        clear_screen()


def process_dissection_studio_menu() -> None:
    """Interactive studio allowing users to input any message, choose keys, and view live dissection."""
    from key_module import key_selection_menu

    display_header("ENIGMA", "Process Dissection Studio")
    console.print(
        Panel(
            "[bold white]Cryptographic Process Dissection Studio[/bold white]\n"
            "Inspect the character-by-character and bit-by-bit transformations performed\n"
            "by each algorithm layer in your multi-key cipher pipeline.",
            border_style="yellow",
        )
    )

    console.print("[1] Dissect Encryption Process", style="bold green")
    console.print("[2] Dissect Decryption Process", style="bold yellow")
    console.print("[3] Return to Main Menu", style="bold white")
    console.print()

    choice = Prompt.ask("Choose mode", choices=["1", "2", "3"], default="1")
    if choice == "3":
        clear_screen()
        return

    op = "encrypt" if choice == "1" else "decrypt"
    prompt_txt = "Enter plaintext to encrypt & dissect: " if op == "encrypt" else "Enter ciphertext to decrypt & dissect: "
    text = input(prompt_txt).strip()
    if not text:
        console.print("[yellow]Empty text entered.[/yellow]")
        prompt_delay()
        clear_screen()
        return

    selection = key_selection_menu(operation=op)
    if not selection:
        clear_screen()
        return

    dissect_full_pipeline(text, selection, operation=op)
