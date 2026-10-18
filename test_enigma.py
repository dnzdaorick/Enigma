import os
import tempfile
import unittest
from media_cipher import (
    MultiKeyCipher,
    ImageKeyCipher,
    generate_key_from_bytes,
    create_sample_bmp_image,
    create_sample_wav_music,
    media_to_code,
    detect_media_type,
    FULL_CHARSET,
    ALPHABET_LOWER,
    ALPHABET_UPPER,
    NUMBERS,
    SYMBOLS,
)
from cipher_module import (
    generate_monoalphabetic_key,
    generate_vigenere_key,
    generate_xor_key,
    vigenere_encrypt,
    vigenere_decrypt,
    xor_encrypt,
    xor_decrypt,
)
import key_module
from menu_module import Menu


class TestMediaCipher(unittest.TestCase):
    """Test suite for MediaCipher (Image & Music keys, single & multi-key cascade)."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_img_path = os.path.join(self.tmp_dir.name, "test_key.bmp")
        self.test_wav_path = os.path.join(self.tmp_dir.name, "test_music.wav")

        create_sample_bmp_image(self.test_img_path, width=32, height=32)
        create_sample_wav_music(self.test_wav_path, duration_sec=0.5)

        with open(self.test_img_path, "rb") as f:
            self.img_bytes = f.read()
        with open(self.test_wav_path, "rb") as f:
            self.wav_bytes = f.read()

        self.img_key, self.img_inv, self.img_info = generate_key_from_bytes(self.img_bytes, self.test_img_path)
        self.wav_key, self.wav_inv, self.wav_info = generate_key_from_bytes(self.wav_bytes, self.test_wav_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_media_type_detection(self):
        self.assertEqual(detect_media_type("photo.png"), "image")
        self.assertEqual(detect_media_type("song.mp3"), "music")
        self.assertEqual(detect_media_type("track.wav"), "music")
        self.assertEqual(detect_media_type("data.bin"), "media")

    def test_image_and_music_code_generation(self):
        img_code = media_to_code(self.img_bytes, self.test_img_path)
        wav_code = media_to_code(self.wav_bytes, self.test_wav_path)

        self.assertEqual(len(img_code["sha256"]), 64)
        self.assertEqual(len(wav_code["sha256"]), 64)
        self.assertEqual(img_code["media_type"], "image")
        self.assertEqual(wav_code["media_type"], "music")
        self.assertNotEqual(img_code["sha256"], wav_code["sha256"])

    def test_single_key_roundtrip(self):
        message = "Single Key Secret 2026: Hello World! [100% OK!]"
        cipher = ImageKeyCipher(message, self.img_key, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertNotEqual(message, encrypted)

        decrypt_cipher = ImageKeyCipher(encrypted, self.img_key, show_ui=False)
        decrypted = decrypt_cipher.decrypt()
        self.assertEqual(message, decrypted)

    def test_two_key_cascade_image_and_music(self):
        message = "Multi-Key Mission 2026: Image + Music Fused! #TopSecret"
        layers = [
            ("1", self.img_key, self.img_info),
            ("2", self.wav_key, self.wav_info),
        ]

        cipher = MultiKeyCipher(message, layers, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertNotEqual(message, encrypted)

        # Single key decryption must FAIL to decrypt correctly
        single_decrypt = ImageKeyCipher(encrypted, self.img_key, show_ui=False).decrypt()
        self.assertNotEqual(message, single_decrypt)

        # Both keys in reverse order must decrypt perfectly
        decrypt_cipher = MultiKeyCipher(encrypted, layers, show_ui=False)
        decrypted = decrypt_cipher.decrypt()
        self.assertEqual(message, decrypted)

    def test_three_key_cascade_roundtrip(self):
        # Alter 1 byte in wav to create a 3rd distinct key
        wav_bytes_3 = bytearray(self.wav_bytes)
        wav_bytes_3[100] = (wav_bytes_3[100] + 1) % 256
        key_3, _, info_3 = generate_key_from_bytes(bytes(wav_bytes_3), "synth.wav")

        message = "Triple Layer Cryptography: 12345 @#$%^&*"
        layers = [
            ("1", self.img_key, self.img_info),
            ("2", self.wav_key, self.wav_info),
            ("3", key_3, info_3),
        ]

        cipher = MultiKeyCipher(message, layers, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertNotEqual(message, encrypted)

        decrypt_cipher = MultiKeyCipher(encrypted, layers, show_ui=False)
        decrypted = decrypt_cipher.decrypt()
        self.assertEqual(message, decrypted)

    def test_preserves_multiline_newlines(self):
        message = "Line 1\nLine 2: 123\nLine 3: Symbols @#"
        layers = [
            ("1", self.img_key, self.img_info),
            ("2", self.wav_key, self.wav_info),
        ]
        cipher = MultiKeyCipher(message, layers, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertEqual(encrypted.count("\n"), 2)

        decrypt_cipher = MultiKeyCipher(encrypted, layers, show_ui=False)
        self.assertEqual(decrypt_cipher.decrypt(), message)


class TestKeyModule(unittest.TestCase):
    """Test suite for image and music key management and multi-key parsing."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_keys_file = os.path.join(self.tmp_dir.name, "test_keys.json")
        self.original_keys_file = key_module.KEYS_FILE
        self.original_keys_dir = key_module.KEYS_DIR
        self.original_keys = dict(key_module.keys)
        self.original_keys_meta = dict(key_module.keys_metadata)

        key_module.KEYS_FILE = self.tmp_keys_file
        key_module.KEYS_DIR = os.path.join(self.tmp_dir.name, "key_media")
        key_module.keys = {}
        key_module.keys_metadata = {}

    def tearDown(self):
        key_module.KEYS_FILE = self.original_keys_file
        key_module.KEYS_DIR = self.original_keys_dir
        key_module.keys = self.original_keys
        key_module.keys_metadata = self.original_keys_meta
        self.tmp_dir.cleanup()

    def test_generate_image_and_music_keys(self):
        img_res = key_module.generate_sample_image(interactive=False)
        self.assertIsNotNone(img_res)
        self.assertEqual(key_module.keys_metadata["1"]["media_type"], "image")

        mus_res = key_module.generate_sample_music(interactive=False)
        self.assertIsNotNone(mus_res)
        self.assertEqual(key_module.keys_metadata["2"]["media_type"], "music")

        self.assertEqual(len(key_module.keys), 2)
        self.assertTrue(os.path.exists(self.tmp_keys_file))

    def test_parse_and_resolve_multiple_keys(self):
        key_module.keys["1"] = {"a": "b"}
        key_module.keys_metadata["1"] = {"media_type": "image", "code": "hash1"}
        key_module.keys["2"] = {"b": "c"}
        key_module.keys_metadata["2"] = {"media_type": "music", "code": "hash2"}

        key_module.keys["3"] = {"c": "d"}
        key_module.keys_metadata["3"] = {"media_type": "monoalphabetic", "code": "hash3"}
        key_module.keys["4"] = {"d": "e"}
        key_module.keys_metadata["4"] = {"media_type": "vigenere", "code": "hash4"}
        key_module.keys["5"] = {"e": "f"}
        key_module.keys_metadata["5"] = {"media_type": "xor", "code": "hash5"}

        resolved_single = key_module.parse_and_resolve_keys("1")
        self.assertEqual(len(resolved_single), 1)

        resolved_double = key_module.parse_and_resolve_keys("1, 2")
        self.assertEqual(len(resolved_double), 2)
        self.assertEqual(resolved_double[0][0], "1")
        self.assertEqual(resolved_double[1][0], "2")

        resolved_space = key_module.parse_and_resolve_keys("1 2 3 4 5")
        self.assertEqual(len(resolved_space), 5)
        self.assertEqual([k[0] for k in resolved_space], ["1", "2", "3", "4", "5"])

        resolved_unseparated = key_module.parse_and_resolve_keys("12345")
        self.assertEqual(len(resolved_unseparated), 5)
        self.assertEqual([k[0] for k in resolved_unseparated], ["1", "2", "3", "4", "5"])

        invalid = key_module.parse_and_resolve_keys("999, 888")
        self.assertIsNone(invalid)

    def test_key_persistence_json(self):
        key_module.generate_sample_image(interactive=False)
        self.assertTrue(os.path.exists(self.tmp_keys_file))

        key_module.keys.clear()
        key_module.keys_metadata.clear()
        key_module.load_keys()

        self.assertEqual(len(key_module.keys), 1)
        self.assertIn("1", key_module.keys)
        self.assertEqual(key_module.keys_metadata["1"]["media_type"], "image")

    def test_delete_key(self):
        key_module.keys["999"] = {"a": "b"}
        key_module.keys_metadata["999"] = {"media_type": "image"}
        self.assertTrue(key_module.delete_key("999"))
        self.assertNotIn("999", key_module.keys)

    def test_scan_media_folder_and_default_audio(self):
        tmp_media = os.path.join(self.tmp_dir.name, "media")
        os.makedirs(os.path.join(tmp_media, "images"), exist_ok=True)
        sample_img = os.path.join(tmp_media, "images", "cat.png")
        create_sample_bmp_image(sample_img, width=16, height=16)

        # Scans media folder; should automatically ensure default_audio.wav exists
        files = key_module.scan_media_folder(tmp_media)
        self.assertGreaterEqual(len(files), 2)
        # Audio should be prioritized first (#1)
        self.assertTrue(any("default_audio.wav" in f for f in files))
        self.assertTrue(any("cat.png" in f for f in files))

    def test_resolve_media_input(self):
        sample_files = ["media/audio/default_audio.wav", "media/images/photo.png"]
        # Numeric index selection
        res1 = key_module.resolve_media_input("1", sample_files)
        self.assertEqual(res1, ["media/audio/default_audio.wav"])

        res2 = key_module.resolve_media_input("1, 2", sample_files)
        self.assertEqual(res2, sample_files)

        # Out of bounds
        invalid = key_module.resolve_media_input("99", sample_files)
        self.assertIsNone(invalid)


class TestMenuModule(unittest.TestCase):
    """Test suite for menu options and verification."""

    def test_menu_add_option_chaining(self):
        menu = Menu("Z", "Test Option", "bold white").add_option()
        self.assertIsInstance(menu, Menu)
        self.assertEqual(menu.menu_code, "Z")

    def test_verify_user_code(self):
        Menu("A", "Encrypt", "bold green").add_option()
        verified = Menu.verify_user_code("A")
        self.assertEqual(verified, "A")
        invalid = Menu.verify_user_code("NONEXISTENT")
        self.assertEqual(invalid, "code not found")


class TestNewCiphers(unittest.TestCase):
    """Test suite for classical Monoalphabetic, Vigenère, and XOR ciphers and cascade integration."""

    def test_monoalphabetic_classical_random_alphabet_roundtrip(self):
        subst, inv, info = generate_monoalphabetic_key()
        self.assertEqual(len(subst), 95)
        self.assertEqual(len(inv), 95)
        self.assertEqual(info["cipher_type"], "monoalphabetic")
        self.assertEqual(info["variant"], "classical")
        message = "Testing Classical Random Alphabet 2026! [Hello World]"
        enc = "".join(subst.get(c, c) for c in message)
        self.assertNotEqual(enc, message)
        dec = "".join(inv.get(c, c) for c in enc)
        self.assertEqual(dec, message)
        # Digits, spaces, and punctuation preserved
        self.assertEqual(subst["0"], "0")
        self.assertEqual(subst["9"], "9")
        self.assertEqual(subst[" "], " ")
        self.assertEqual(subst["!"], "!")

    def test_vigenere_classical_known_vector(self):
        plaintext = "ATTACKATDAWN"
        key = "LEMON"
        ciphertext = vigenere_encrypt(plaintext, key)
        self.assertEqual(ciphertext, "LXFOPVEFRNHR")
        decrypted = vigenere_decrypt(ciphertext, key)
        self.assertEqual(decrypted, plaintext)

    def test_vigenere_classical_with_spaces_and_symbols(self):
        plaintext = "Attack at Dawn! 100% Ready."
        key = "LEMON"
        ciphertext = vigenere_encrypt(plaintext, key)
        decrypted = vigenere_decrypt(ciphertext, key)
        self.assertEqual(decrypted, plaintext)

    def test_xor_cipher_roundtrip(self):
        plaintext = "XOR Cipher Cryptography Test 2026! Top Secret."
        key = "XOR_KEY_STRING"
        hex_ciphertext = xor_encrypt(plaintext, key)
        # Result must be a valid hex string
        self.assertTrue(all(c in "0123456789abcdef" for c in hex_ciphertext))
        decrypted = xor_decrypt(hex_ciphertext, key)
        self.assertEqual(decrypted, plaintext)

    def test_multikey_cascade_all_four_cipher_types(self):
        # 1. Media key (sample image)
        tmp_img = "test_quad_img.bmp"
        create_sample_bmp_image(tmp_img, width=16, height=16)
        with open(tmp_img, "rb") as f:
            b = f.read()
        os.remove(tmp_img)
        img_key, _, img_info = generate_key_from_bytes(b, "test_quad_img.bmp")

        # 2. Monoalphabetic key (Classical Random Alphabet)
        mono_key, _, mono_info = generate_monoalphabetic_key()

        # 3. Vigenère key (Classical)
        vig_key, vig_info = generate_vigenere_key(keyword="LEMON")

        # 4. XOR key (Classical)
        xor_key, xor_info = generate_xor_key(key_string="CASCADE_XOR_KEY")

        layers = [
            ("1", img_key, img_info),
            ("2", mono_key, mono_info),
            ("3", {}, vig_info),
            ("4", {}, xor_info),
        ]

        message = "Full 4-Cipher Cascade: Image + Mono + Vigenere + XOR!"
        cipher = MultiKeyCipher(message, layers, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertNotEqual(encrypted, message)

        decipher = MultiKeyCipher(encrypted, layers, show_ui=False)
        decrypted = decipher.decrypt()
        self.assertEqual(decrypted, message)

        # Decrypt when user passes keys in reverse unwinding order (e.g. 4, 3, 2, 1)
        decipher_rev = MultiKeyCipher(encrypted, list(reversed(layers)), show_ui=False)
        decrypted_rev = decipher_rev.decrypt()
        self.assertEqual(decrypted_rev, message)

    def test_key_module_registration_of_new_keys(self):
        orig_file = key_module.KEYS_FILE
        orig_keys = dict(key_module.keys)
        orig_meta = dict(key_module.keys_metadata)
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_keys = os.path.join(tmp_dir, "test_keys.json")
            key_module.KEYS_FILE = tmp_keys
            try:
                init_count = len(key_module.keys)
                # Register Mono (Classical Random Alphabet)
                k1_id, _ = key_module.register_monoalphabetic_key(interactive=False)
                self.assertIn(k1_id, key_module.keys)
                self.assertEqual(key_module.keys_metadata[k1_id]["cipher_type"], "monoalphabetic")
                self.assertEqual(key_module.keys_metadata[k1_id]["variant"], "classical")

                # Register Vigenere (Classical)
                k2_id, _ = key_module.register_vigenere_key(keyword="TESTVIG", interactive=False)
                self.assertIn(k2_id, key_module.keys)
                self.assertEqual(key_module.keys_metadata[k2_id]["cipher_type"], "vigenere")
                self.assertEqual(key_module.keys_metadata[k2_id]["key_value"], "TESTVIG")
                self.assertEqual(key_module.keys_metadata[k2_id]["variant"], "classical")

                # Register XOR (Classical)
                k3_id, _ = key_module.register_xor_key(key_string="TESTXOR", interactive=False)
                self.assertIn(k3_id, key_module.keys)
                self.assertEqual(key_module.keys_metadata[k3_id]["cipher_type"], "xor")
                self.assertEqual(key_module.keys_metadata[k3_id]["key_value"], "TESTXOR")
                self.assertEqual(key_module.keys_metadata[k3_id]["variant"], "classical")

                # Clean up
                key_module.delete_key(k1_id)
                key_module.delete_key(k2_id)
                key_module.delete_key(k3_id)
                self.assertEqual(len(key_module.keys), init_count)
            finally:
                key_module.KEYS_FILE = orig_file
                key_module.keys = orig_keys
                key_module.keys_metadata = orig_meta

    def test_cipher_module_generators(self):
        # Auto-generated Vigenere key (Classical)
        v_key, v_info = generate_vigenere_key()
        self.assertEqual(len(v_key), 12)
        self.assertEqual(v_info["variant"], "classical")
        self.assertEqual(v_info["cipher_type"], "vigenere")

        # Auto-generated XOR key (Classical)
        x_key, x_info = generate_xor_key(length=32)
        self.assertEqual(len(x_key), 32)
        self.assertEqual(x_info["cipher_type"], "xor")
        self.assertEqual(x_info["variant"], "classical")

        # Classical random alphabet monoalphabetic key
        m_sub, m_inv, m_info = generate_monoalphabetic_key()
        self.assertEqual(m_info["cipher_type"], "monoalphabetic")
        self.assertEqual(m_info["variant"], "classical")
        # Letters should be mapped, digits and symbols preserved
        self.assertEqual(m_sub["1"], "1")
        self.assertEqual(m_sub["!"], "!")


class TestAdditionalFeatures(unittest.TestCase):
    """Test suite for Cryptographic Dossiers, Process Dissection, and Linked Cryptography."""

    def test_crypto_info_dossiers(self):
        from crypto_info_module import ALGORITHM_DOSSIERS
        expected_keys = {"monoalphabetic", "vigenere", "xor", "media", "cascade"}
        self.assertTrue(expected_keys.issubset(set(ALGORITHM_DOSSIERS.keys())))

        for key, dossier in ALGORITHM_DOSSIERS.items():
            self.assertIn("title", dossier)
            self.assertIn("origin", dossier)
            self.assertIn("use", dossier)
            self.assertIn("pros", dossier)
            self.assertIn("cons", dossier)
            self.assertGreater(len(dossier["pros"]), 0)
            self.assertGreater(len(dossier["cons"]), 0)

    def test_process_dissection_tables(self):
        from process_dissection_module import (
            dissect_monoalphabetic_layer,
            dissect_vigenere_layer,
            dissect_xor_layer,
            dissect_media_layer,
        )
        from rich.table import Table

        mono_sub, _, _ = generate_monoalphabetic_key()
        t_mono = dissect_monoalphabetic_layer("Hello World", mono_sub, is_decrypt=False)
        self.assertIsInstance(t_mono, Table)

        t_vig = dissect_vigenere_layer("Hello World", "KEY", is_decrypt=False)
        self.assertIsInstance(t_vig, Table)

        t_xor = dissect_xor_layer("Hello World", "XORKEY", is_decrypt=False)
        self.assertIsInstance(t_xor, Table)

        t_media = dissect_media_layer("Hello World", mono_sub, {"media_type": "image"}, is_decrypt=False)
        self.assertIsInstance(t_media, Table)

    def test_linked_encryption_decryption_symmetry(self):
        mono_sub, _, m_meta = generate_monoalphabetic_key()
        vig_key, v_meta = generate_vigenere_key("SECRETKEY")
        xor_key, x_meta = generate_xor_key("CASCADEKEY")

        layers = [
            ("1", mono_sub, m_meta),
            ("2", {}, v_meta),
            ("3", {}, x_meta),
        ]

        original = "Linked Roundtrip Cryptography Verification 2026!"
        enc_cipher = MultiKeyCipher(original, layers, show_ui=False)
        ciphertext = enc_cipher.encrypt()

        dec_cipher = MultiKeyCipher(ciphertext, layers, show_ui=False)
        restored = dec_cipher.decrypt()

        self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
