#!/usr/bin/env python3
"""
Simple test script to verify the caching system works correctly.
"""

import hashlib
import json
import os
import unittest

from src.cache import (
    get_cache_key,
    get_cache_path,
    get_file_hash,
    is_cached,
    load_from_cache,
    save_to_cache,
)

class TestCacheFunctions(unittest.TestCase):
    def setUp(self):
        self.test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.test_file_hash = "abc123def456"
        self.test_captions = [
            {"start": 0.0, "end": 2.0, "text": "Hello world"},
            {"start": 2.0, "end": 4.0, "text": "This is a test"}
        ]
        self.test_metadata = {
            "url": self.test_url,
            "method": "test_method",
            "test": True
        }
        self.url_cache_key = get_cache_key(url=self.test_url)
        self.file_cache_key = get_cache_key(file_hash=self.test_file_hash)
        self.cache_path = get_cache_path(self.url_cache_key)

    def tearDown(self):
        # Clean up any cache files created
        for key in [self.url_cache_key, self.file_cache_key]:
            path = get_cache_path(key)
            if os.path.exists(path):
                os.remove(path)
        # Clean up test file if present
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")

    def test_get_cache_key_url(self):
        key = get_cache_key(url=self.test_url)
        expected = hashlib.sha256(self.test_url.encode()).hexdigest()
        self.assertEqual(key, expected)

    def test_get_cache_key_file_hash(self):
        key = get_cache_key(file_hash=self.test_file_hash)
        self.assertEqual(key, self.test_file_hash)

    def test_get_cache_key_raises(self):
        with self.assertRaises(ValueError):
            get_cache_key()

    def test_get_cache_path(self):
        path = get_cache_path(self.url_cache_key)
        self.assertTrue(path.endswith(f"{self.url_cache_key}.json"))

    def test_save_and_is_cached(self):
        save_to_cache(self.url_cache_key, self.test_captions, self.test_metadata)
        self.assertTrue(is_cached(self.url_cache_key))

    def test_save_and_load_from_cache(self):
        save_to_cache(self.url_cache_key, self.test_captions, self.test_metadata)
        loaded = load_from_cache(self.url_cache_key)
        self.assertEqual(loaded["captions"], self.test_captions)
        self.assertEqual(loaded["metadata"], self.test_metadata)
        self.assertIn("cached_at", loaded)

    def test_get_file_hash(self):
        # Create a test file
        test_content = "This is a test file for hash generation"
        with open("test_file.txt", "w") as f:
            f.write(test_content)
        hash1 = get_file_hash("test_file.txt")
        hash2 = get_file_hash("test_file.txt")
        self.assertEqual(hash1, hash2)
        # Check that it's a valid SHA256 hex string
        self.assertEqual(len(hash1), 64)
        int(hash1, 16)  # Should not raise

if __name__ == "__main__":
    unittest.main()
