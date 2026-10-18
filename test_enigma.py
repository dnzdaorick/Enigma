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

        key_module.KEYS_FILE = self.tmp_keys_file
        key_module.KEYS_DIR = os.path.join(self.tmp_dir.name, "key_media")
        key_module.keys.clear()
        key_module.keys_metadata.clear()

    def tearDown(self):
        key_module.KEYS_FILE = self.original_keys_file
        key_module.KEYS_DIR = self.original_keys_dir
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

        resolved_single = key_module.parse_and_resolve_keys("1")
        self.assertEqual(len(resolved_single), 1)

        resolved_double = key_module.parse_and_resolve_keys("1, 2")
        self.assertEqual(len(resolved_double), 2)
        self.assertEqual(resolved_double[0][0], "1")
        self.assertEqual(resolved_double[1][0], "2")

        resolved_space = key_module.parse_and_resolve_keys("1 2")
        self.assertEqual(len(resolved_space), 2)

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
