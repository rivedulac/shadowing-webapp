#!/usr/bin/env python3
"""
Simple test script to verify the caching system works correctly.
"""

import os
import json
import hashlib
from main import (
    get_cache_key, 
    get_cache_path, 
    is_cached, 
    save_to_cache, 
    load_from_cache,
    get_file_hash
)

def test_cache_functions():
    """Test basic cache functions"""
    print("Testing cache functions...")
    
    # Test cache key generation
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    url_cache_key = get_cache_key(url=test_url)
    print(f"URL cache key: {url_cache_key}")
    
    # Test file hash cache key
    test_file_hash = "abc123def456"
    file_cache_key = get_cache_key(file_hash=test_file_hash)
    print(f"File hash cache key: {file_cache_key}")
    
    # Test cache path
    cache_path = get_cache_path(url_cache_key)
    print(f"Cache path: {cache_path}")
    
    # Test cache operations
    test_captions = [
        {"start": 0.0, "end": 2.0, "text": "Hello world"},
        {"start": 2.0, "end": 4.0, "text": "This is a test"}
    ]
    
    test_metadata = {
        "url": test_url,
        "method": "test_method",
        "test": True
    }
    
    # Save to cache
    save_to_cache(url_cache_key, test_captions, test_metadata)
    print("Saved to cache")
    
    # Check if cached
    cached = is_cached(url_cache_key)
    print(f"Is cached: {cached}")
    
    # Load from cache
    loaded_data = load_from_cache(url_cache_key)
    print(f"Loaded data: {loaded_data}")
    
    # Verify data integrity
    assert loaded_data["captions"] == test_captions
    assert loaded_data["metadata"] == test_metadata
    print("Data integrity verified!")
    
    # Clean up test cache file
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print("Test cache file cleaned up")
    
    print("All cache function tests passed!")

def test_file_hash():
    """Test file hash generation"""
    print("\nTesting file hash generation...")
    
    # Create a test file
    test_file_path = "test_file.txt"
    test_content = "This is a test file for hash generation"
    
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    # Generate hash
    file_hash = get_file_hash(test_file_path)
    print(f"File hash: {file_hash}")
    
    # Verify hash is consistent
    file_hash2 = get_file_hash(test_file_path)
    assert file_hash == file_hash2
    print("Hash consistency verified!")
    
    # Clean up
    os.remove(test_file_path)
    print("Test file cleaned up")

if __name__ == "__main__":
    test_cache_functions()
    test_file_hash()
    print("\nAll tests completed successfully!") 