import hashlib
import json
import os
import uuid

from src.constants import CACHE_DIR


def setup_cache_directory():
    os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_key(url: str = None, file_hash: str = None) -> str:
    if url:
        return hashlib.sha256(url.encode()).hexdigest()
    elif file_hash:
        return file_hash
    else:
        raise ValueError("Either url or file_hash must be provided")

def get_cache_path(cache_key: str) -> str:
    return os.path.join(CACHE_DIR, f"{cache_key}.json")

def is_cached(cache_key: str) -> bool:
    return os.path.exists(get_cache_path(cache_key))


def save_to_cache(cache_key: str,
                  captions: list,
                  metadata: dict = None) -> None:
    cache_path = get_cache_path(cache_key)
    with open(cache_path, "w") as f:
        json.dump(
            {
                "captions": captions,
                "metadata": metadata,
                "cached_at": str(uuid.uuid4())
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_from_cache(cache_key: str) -> dict:
    cache_path = get_cache_path(cache_key)
    with open(cache_path, "r") as f:
        return json.load(f)


def get_file_hash(file_path: str) -> str:
    """Generate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


async def get_cache_info():
    """Get information about the cache directory and cached entries"""
    try:
        cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
        cache_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in cache_files)

        cache_entries = []
        for cache_file in cache_files:
            cache_path = os.path.join(CACHE_DIR, cache_file)
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    cache_entries.append({
                        "cache_key": cache_file.replace('.json', ''),
                        "method": metadata.get("method", "unknown"),
                        "url": metadata.get("url", "file_upload"),
                        "caption_count": len(data.get("captions", [])),
                        "file_size": os.path.getsize(cache_path)
                    })
            except Exception as e:
                cache_entries.append({
                    "cache_key": cache_file.replace('.json', ''),
                    "error": str(e)
                })

        return {
            "cache_directory": CACHE_DIR,
            "total_entries": len(cache_files),
            "total_size_bytes": cache_size,
            "entries": cache_entries
        }
    except Exception as e:
        return {"error": f"Failed to get cache info: {str(e)}"}


async def clear_cache():
    """Clear all cached captions"""
    try:
        cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
        deleted_count = 0

        for cache_file in cache_files:
            cache_path = os.path.join(CACHE_DIR, cache_file)
            try:
                os.remove(cache_path)
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {cache_file}: {e}")

        return {
            "message": f"Cache cleared successfully",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        return {"error": f"Failed to clear cache: {str(e)}"}


async def delete_cache_entry(cache_key: str):
    """Delete a specific cache entry"""
    try:
        cache_path = get_cache_path(cache_key)
        if os.path.exists(cache_path):
            os.remove(cache_path)
            return {"message": f"Cache entry {cache_key} deleted successfully"}
        else:
            return {"error": f"Cache entry {cache_key} not found"}
    except Exception as e:
        return {"error": f"Failed to delete cache entry: {str(e)}"}
