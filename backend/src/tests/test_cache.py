#!/usr/bin/env python3
"""
Simple test script to verify the caching system works correctly.
"""

import asyncio
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
    get_cache_info,
    clear_cache,
    delete_cache_entry,
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


class TestAsyncCacheFunctions(unittest.TestCase):
    def setUp(self):
        self.test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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

    def tearDown(self):
        # Clean up any cache files created
        path = get_cache_path(self.url_cache_key)
        if os.path.exists(path):
            os.remove(path)

    def test_get_cache_info_empty(self):
        """Test get_cache_info when cache is empty"""
        async def run_test():
            result = await get_cache_info()
            self.assertIn("cache_directory", result)
            self.assertEqual(result["total_entries"], 0)
            self.assertEqual(result["total_size_bytes"], 0)
            self.assertEqual(result["entries"], [])
        
        asyncio.run(run_test())

    def test_get_cache_info_with_data(self):
        """Test get_cache_info when cache has data"""
        async def run_test():
            # First save some data
            save_to_cache(self.url_cache_key, self.test_captions, self.test_metadata)
            
            result = await get_cache_info()
            self.assertIn("cache_directory", result)
            self.assertEqual(result["total_entries"], 1)
            self.assertGreater(result["total_size_bytes"], 0)
            self.assertEqual(len(result["entries"]), 1)
            
            entry = result["entries"][0]
            self.assertEqual(entry["cache_key"], self.url_cache_key)
            self.assertEqual(entry["method"], "test_method")
            self.assertEqual(entry["url"], self.test_url)
            self.assertEqual(entry["caption_count"], 2)
        
        asyncio.run(run_test())

    def test_clear_cache(self):
        """Test clear_cache function"""
        async def run_test():
            # First save some data
            save_to_cache(self.url_cache_key, self.test_captions, self.test_metadata)
            self.assertTrue(is_cached(self.url_cache_key))
            
            # Clear cache
            result = await clear_cache()
            self.assertIn("message", result)
            self.assertGreaterEqual(result["deleted_entries"], 1)  # At least our test entry
            
            # Verify our test entry is gone
            self.assertFalse(is_cached(self.url_cache_key))
        
        asyncio.run(run_test())

    def test_clear_cache_empty(self):
        """Test clear_cache when cache is already empty"""
        async def run_test():
            result = await clear_cache()
            self.assertIn("message", result)
            self.assertEqual(result["deleted_entries"], 0)
        
        asyncio.run(run_test())

    def test_delete_cache_entry(self):
        """Test delete_cache_entry function"""
        async def run_test():
            # First save some data
            save_to_cache(self.url_cache_key, self.test_captions, self.test_metadata)
            self.assertTrue(is_cached(self.url_cache_key))
            
            # Delete specific entry
            result = await delete_cache_entry(self.url_cache_key)
            self.assertIn("message", result)
            self.assertIn("deleted successfully", result["message"])
            
            # Verify entry is gone
            self.assertFalse(is_cached(self.url_cache_key))
        
        asyncio.run(run_test())

    def test_delete_cache_entry_not_found(self):
        """Test delete_cache_entry when entry doesn't exist"""
        async def run_test():
            result = await delete_cache_entry("nonexistent_key")
            self.assertIn("error", result)
            self.assertIn("not found", result["error"])
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
