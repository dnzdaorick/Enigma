import os
import tempfile
import unittest
from image_key_cipher import (
    ImageKeyCipher,
    generate_key_from_image,
    create_sample_bmp_image,
    image_to_code,
    FULL_CHARSET,
    ALPHABET_LOWER,
    ALPHABET_UPPER,
    NUMBERS,
    SYMBOLS,
)
import key_module
from menu_module import Menu


class TestImageKeyCipher(unittest.TestCase):
    """Test suite for ImageKeyCipher and image key generation."""

    def setUp(self):
        # Create a temporary BMP image file for deterministic testing
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_img_path = os.path.join(self.tmp_dir.name, "test_key.bmp")
        create_sample_bmp_image(self.test_img_path, width=32, height=32)

        with open(self.test_img_path, "rb") as f:
            self.img_bytes = f.read()

        self.key, self.inverse_key, self.code_info = generate_key_from_image(self.img_bytes)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_image_code_generation(self):
        code_info = image_to_code(self.img_bytes)
        self.assertIn("sha256", code_info)
        self.assertEqual(len(code_info["sha256"]), 64)
        self.assertIn("short_code", code_info)
        self.assertEqual(len(code_info["short_code"]), 16)
        self.assertTrue(int(code_info["byte_size"]) > 0)

    def test_substitution_key_covers_all_categories(self):
        # Must cover exactly 95 distinct characters
        self.assertEqual(len(self.key), 95)
        self.assertEqual(len(set(self.key.values())), 95)

        # Check alphabet, numbers, and symbols are all present as keys
        for char in ALPHABET_LOWER + ALPHABET_UPPER:
            self.assertIn(char, self.key)
        for num in NUMBERS:
            self.assertIn(num, self.key)
        for sym in SYMBOLS:
            self.assertIn(sym, self.key)

    def test_encrypt_and_decrypt_roundtrip(self):
        message = "Enigma Secret 2026: Hello World! [Symbols: @#$%^&*()-=_+{}|;:'\",.<>/?]"
        cipher = ImageKeyCipher(
            message=message,
            key=self.key,
            image_code=self.code_info["sha256"],
            image_path=self.test_img_path,
            show_ui=False,
        )
        encrypted = cipher.encrypt()
        self.assertNotEqual(message, encrypted)

        # Check that numbers and symbols were substituted
        self.assertNotIn("2026", encrypted)
        self.assertNotIn("@#$%^&*", encrypted)

        decrypt_cipher = ImageKeyCipher(
            message=encrypted,
            key=self.key,
            image_code=self.code_info["sha256"],
            image_path=self.test_img_path,
            show_ui=False,
        )
        decrypted = decrypt_cipher.decrypt()
        self.assertEqual(message, decrypted)

    def test_deterministic_key_reproducibility(self):
        # Two key generations from the exact same image bytes must produce identical keys
        key_1, _, code_1 = generate_key_from_image(self.img_bytes)
        key_2, _, code_2 = generate_key_from_image(self.img_bytes)
        self.assertEqual(key_1, key_2)
        self.assertEqual(code_1["sha256"], code_2["sha256"])

    def test_different_image_produces_different_key(self):
        # Alter a single byte
        altered_bytes = bytearray(self.img_bytes)
        altered_bytes[60] = (altered_bytes[60] + 1) % 256
        altered_bytes = bytes(altered_bytes)

        key_altered, _, code_altered = generate_key_from_image(altered_bytes)
        self.assertNotEqual(self.code_info["sha256"], code_altered["sha256"])
        self.assertNotEqual(self.key, key_altered)

    def test_preserves_multiline_newlines(self):
        message = "Line 1: Hello\nLine 2: World 123!\nLine 3: End."
        cipher = ImageKeyCipher(message, self.key, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertEqual(encrypted.count("\n"), 2)

        decrypt_cipher = ImageKeyCipher(encrypted, self.key, show_ui=False)
        self.assertEqual(decrypt_cipher.decrypt(), message)


class TestKeyModule(unittest.TestCase):
    """Test suite for image key management and persistence."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_keys_file = os.path.join(self.tmp_dir.name, "test_keys.json")
        self.original_keys_file = key_module.KEYS_FILE
        self.original_keys_dir = key_module.KEYS_DIR

        key_module.KEYS_FILE = self.tmp_keys_file
        key_module.KEYS_DIR = os.path.join(self.tmp_dir.name, "key_images")
        key_module.keys.clear()
        key_module.keys_metadata.clear()

    def tearDown(self):
        key_module.KEYS_FILE = self.original_keys_file
        key_module.KEYS_DIR = self.original_keys_dir
        self.tmp_dir.cleanup()

    def test_generate_sample_image_key(self):
        key = key_module.generate_key(interactive=False)
        self.assertEqual(len(key), 95)
        self.assertEqual(len(key_module.keys), 1)
        self.assertTrue(os.path.exists(self.tmp_keys_file))

    def test_key_persistence_json(self):
        gen_key = key_module.generate_key(interactive=False)
        self.assertTrue(os.path.exists(self.tmp_keys_file))

        # Clear in-memory keys and reload from JSON
        key_module.keys.clear()
        key_module.keys_metadata.clear()
        key_module.load_keys()

        self.assertEqual(len(key_module.keys), 1)
        self.assertEqual(key_module.keys["1"], gen_key)
        self.assertIn("1", key_module.keys_metadata)

    def test_delete_key(self):
        key_module.keys["999"] = {"a": "b"}
        key_module.keys_metadata["999"] = {"image_code": "test"}
        self.assertTrue(key_module.delete_key("999"))
        self.assertNotIn("999", key_module.keys)
        self.assertFalse(key_module.delete_key("999"))

    def test_select_key(self):
        key_module.keys["123"] = {"a": "b"}
        sel = key_module.select_key("123")
        self.assertEqual(sel, ("123", {"a": "b"}))
        invalid = key_module.select_key("999999")
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


if __name__ == "__main__":
    unittest.main()
