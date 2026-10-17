import os
import json
import tempfile
import unittest
from monoalphabetic_cipher import MonoalphabeticCipher
import key_module
from menu_module import Menu


class TestMonoalphabeticCipher(unittest.TestCase):
    """Test suite for MonoalphabeticCipher."""

    def setUp(self):
        # Deterministic shift-by-1 substitution key
        letters = [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)]
        self.test_key = {
            letters[i]: letters[(i + 1) % len(letters)]
            for i in range(len(letters))
        }

    def test_encrypt_and_decrypt_roundtrip(self):
        message = "Hello, World! 123 - Test Suite."
        cipher = MonoalphabeticCipher(message, self.test_key, preserve_formatting=True, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertNotEqual(message, encrypted)

        decrypt_cipher = MonoalphabeticCipher(encrypted, self.test_key, preserve_formatting=True, show_ui=False)
        decrypted = decrypt_cipher.decrypt()
        self.assertEqual(message, decrypted)

    def test_preserves_punctuation_and_spaces(self):
        message = "Spacing & Punctuation: [100% OK!]"
        cipher = MonoalphabeticCipher(message, self.test_key, preserve_formatting=True, show_ui=False)
        encrypted = cipher.encrypt()

        # Check symbols and digits are preserved in place
        self.assertIn(" ", encrypted)
        self.assertIn("&", encrypted)
        self.assertIn(":", encrypted)
        self.assertIn("100%", encrypted)
        self.assertIn("[", encrypted)
        self.assertIn("]", encrypted)

    def test_strict_mode_strips_spaces(self):
        message = "Hello World"
        cipher = MonoalphabeticCipher(message, self.test_key, preserve_formatting=False, show_ui=False)
        encrypted = cipher.encrypt()
        self.assertNotIn(" ", encrypted)


class TestKeyModule(unittest.TestCase):
    """Test suite for key management and persistence."""

    def test_generate_key_structure(self):
        key = key_module.generate_key(interactive=False)
        self.assertEqual(len(key), 52)
        for i in range(97, 123):
            self.assertIn(chr(i), key)
        for i in range(65, 91):
            self.assertIn(chr(i), key)

    def test_key_persistence_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        original_file = key_module.KEYS_FILE
        try:
            key_module.KEYS_FILE = tmp_path
            key_module.keys.clear()
            key_module.keys_metadata.clear()

            gen_key = key_module.generate_key(interactive=False)
            self.assertTrue(os.path.exists(tmp_path))

            # Clear memory and reload from file
            key_module.keys.clear()
            key_module.load_keys()
            self.assertEqual(len(key_module.keys), 1)
            self.assertEqual(key_module.keys["1"], gen_key)
        finally:
            key_module.KEYS_FILE = original_file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_delete_key(self):
        key_module.keys["999"] = {"a": "b"}
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
