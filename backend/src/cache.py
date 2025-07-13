from constants import CACHE_DIR


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
