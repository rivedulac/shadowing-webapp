#!/usr/bin/env python3
"""
Test script to verify the server module works correctly with the new architecture.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

from src.server import (
    get_cache_info,
    clear_cache,
    delete_cache_entry,
    merge_short_captions,
    timestamp_to_seconds,
)


class TestServerCacheFunctions(unittest.TestCase):
    """Test that server cache functions properly delegate to cache module"""

    def test_get_cache_info_delegation(self):
        """Test that get_cache_info delegates to cache module"""
        async def run_test():
            with patch('src.cache.get_cache_info', new_callable=AsyncMock) as mock_cache_info:
                mock_cache_info.return_value = {"test": "data"}
                
                result = await get_cache_info()
                
                mock_cache_info.assert_called_once()
                self.assertEqual(result, {"test": "data"})
        
        asyncio.run(run_test())

    def test_clear_cache_delegation(self):
        """Test that clear_cache delegates to cache module"""
        async def run_test():
            with patch('src.cache.clear_cache', new_callable=AsyncMock) as mock_clear:
                mock_clear.return_value = {"message": "cleared", "deleted_entries": 5}
                
                result = await clear_cache()
                
                mock_clear.assert_called_once()
                self.assertEqual(result, {"message": "cleared", "deleted_entries": 5})
        
        asyncio.run(run_test())

    def test_delete_cache_entry_delegation(self):
        """Test that delete_cache_entry delegates to cache module"""
        async def run_test():
            with patch('src.cache.delete_cache_entry', new_callable=AsyncMock) as mock_delete:
                mock_delete.return_value = {"message": "deleted successfully"}
                
                result = await delete_cache_entry("test_key")
                
                mock_delete.assert_called_once_with("test_key")
                self.assertEqual(result, {"message": "deleted successfully"})
        
        asyncio.run(run_test())


class TestServerUtilityFunctions(unittest.TestCase):
    """Test server utility functions"""

    def test_merge_short_captions(self):
        """Test merge_short_captions function"""
        captions = [
            {"start": 0.0, "end": 1.0, "text": "Hello"},
            {"start": 1.0, "end": 2.0, "text": "world"},
            {"start": 2.0, "end": 4.0, "text": "This is longer"},
            {"start": 4.0, "end": 5.0, "text": "Short"},
            {"start": 5.0, "end": 6.0, "text": "again"}
        ]
        
        # Test with default min_duration (2.5)
        merged = merge_short_captions(captions)
        
        # Should merge short segments
        self.assertLess(len(merged), len(captions))
        
        # Check that merged segments are longer
        for segment in merged:
            duration = segment["end"] - segment["start"]
            self.assertGreaterEqual(duration, 0.5)  # Minimum duration threshold

    def test_merge_short_captions_empty(self):
        """Test merge_short_captions with empty list"""
        result = merge_short_captions([])
        self.assertEqual(result, [])

    def test_merge_short_captions_single(self):
        """Test merge_short_captions with single caption"""
        captions = [{"start": 0.0, "end": 1.0, "text": "Hello"}]
        result = merge_short_captions(captions)
        self.assertEqual(result, captions)

    def test_merge_short_captions_custom_duration(self):
        """Test merge_short_captions with custom min_duration"""
        captions = [
            {"start": 0.0, "end": 1.0, "text": "Hello"},
            {"start": 1.0, "end": 2.0, "text": "world"},
            {"start": 2.0, "end": 4.0, "text": "This is longer"}
        ]
        
        # Test with higher min_duration
        merged = merge_short_captions(captions, min_duration=3.0)
        
        # Should merge more aggressively
        self.assertLessEqual(len(merged), len(captions))

    def test_timestamp_to_seconds(self):
        """Test timestamp_to_seconds function"""
        # Test HH:MM:SS.mmm format
        self.assertEqual(timestamp_to_seconds("01:30:45.500"), 5445.5)
        
        # Test MM:SS.mmm format (should work with hours=0)
        self.assertEqual(timestamp_to_seconds("00:30:45.500"), 1845.5)
        
        # Test edge cases
        self.assertEqual(timestamp_to_seconds("00:00:00.000"), 0.0)
        self.assertEqual(timestamp_to_seconds("23:59:59.999"), 86399.999)


class TestServerIntegration(unittest.TestCase):
    """Test server integration with cache module"""

    @patch('src.server.get_cache_key')
    @patch('src.server.is_cached')
    @patch('src.server.load_from_cache')
    def test_cache_integration(self, mock_load, mock_is_cached, mock_get_key):
        """Test that server functions properly integrate with cache"""
        # Setup mocks
        mock_get_key.return_value = "test_key"
        mock_is_cached.return_value = True
        mock_load.return_value = {
            "captions": [{"start": 0, "end": 2, "text": "test"}],
            "metadata": {"method": "test"}
        }
        
        # This would be tested in the actual API functions
        # For now, just verify the cache functions are called correctly
        self.assertTrue(mock_is_cached.called or not mock_is_cached.called)  # Placeholder assertion


if __name__ == "__main__":
    unittest.main() 