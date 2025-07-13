# Caching System Documentation

## Overview

The shadowing webapp now includes a comprehensive caching system that stores and reuses caption files to improve performance and reduce redundant processing.

## Cache Structure

### Directory Structure

```
backend/
├── cache/                    # Cache directory
│   ├── {cache_key}.json     # Individual cache files
│   └── ...
├── transcribe/              # Temporary files directory
└── main.py                  # Main application with caching
```

### Cache File Format

Each cache file contains:

```json
{
  "captions": [
    {
      "start": 0.0,
      "end": 2.0,
      "text": "Hello world"
    }
  ],
  "metadata": {
    "url": "https://youtube.com/...",
    "method": "youtube_captions",
    "filename": "video.mp4",
    "file_size": 1234567,
    "original_segments": 50,
    "merged_segments": 25
  },
  "cached_at": "uuid-timestamp"
}
```

## Cache Key Generation

### For YouTube URLs

- Uses MD5 hash of the URL
- Ensures consistent caching for the same video

### For Uploaded Files

- Uses SHA256 hash of the file content
- Ensures identical files are cached together

## Caching Behavior

### File Uploads (`/transcribe`)

1. Generate file hash from uploaded content
2. Check if captions exist in cache
3. If cached: return cached captions immediately
4. If not cached: process with Whisper and cache results

### YouTube Videos

1. Check cache using URL hash
2. If cached: return cached captions
3. If not cached: extract/download and cache

### Smart Extraction

- Caches original captions (before merging)
- Allows re-merge with different durations
- Maintains quality assessment data

## API Endpoints

### Cache Management

- `GET /cache/info` - Get cache statistics and entries
- `DELETE /cache/clear` - Clear all cached entries
- `DELETE /cache/{cache_key}` - Delete specific cache entry

### Enhanced Response Format

All transcription endpoints now return:

```json
{
  "captions": [...],
  "method": "youtube_captions|whisper_transcription",
  "cached": true|false,
  "metadata": {...}
}
```

## Benefits

1. **Performance**: Avoids redundant processing
2. **Cost Savings**: Reduces API calls and computation
3. **Consistency**: Same input produces same output
4. **Flexibility**: Supports different merging strategies

## Cache Management

### Automatic Cleanup

- Temporary files are cleaned up after processing
- Cache files persist for reuse

### Manual Management

- Use cache endpoints to inspect and manage cache
- Clear cache when needed (e.g., storage constraints)

## Testing

Run the test script to verify caching functionality:

```bash
cd backend
python test_cache.py
```
