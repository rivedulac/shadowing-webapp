import hashlib
import os
import re
import shutil
import subprocess
import uuid

from fastapi import Body, File, UploadFile

from src.assess_quality import assess_caption_quality
from src.cache import (
    get_cache_key,
    get_cache_path,
    is_cached,
    load_from_cache,
    save_to_cache,
    get_file_hash,
)
from src.whisper_infer import transcribe_with_whisper

TS_DIR = "transcribe"
os.makedirs(TS_DIR, exist_ok=True)


def merge_short_captions(captions: list, min_duration: float = 2.5):
    """Merge short caption segments into longer ones for better shadowing practice"""
    if not captions:
        return captions

    merged = []
    current_segment = {
        "start": captions[0]["start"],
        "end": captions[0]["end"],
        "text": captions[0]["text"]
    }

    for i in range(1, len(captions)):
        current_caption = captions[i]
        current_duration = current_segment["end"] - current_segment["start"]

        # If current segment is too short, try to merge with next caption
        if current_duration < min_duration:
            # Check if there's a reasonable gap (less than 1 second)
            gap = current_caption["start"] - current_segment["end"]
            if gap < 1.0:
                # Merge the captions
                current_segment["end"] = current_caption["end"]
                current_segment["text"] += " " + current_caption["text"]
            else:
                # Gap is too large, finalize current segment and start new one
                if current_duration >= 0.5:  # Only add if it's at least 0.5 seconds
                    merged.append(current_segment)
                current_segment = {
                    "start": current_caption["start"],
                    "end": current_caption["end"],
                    "text": current_caption["text"]
                }
        else:
            # Current segment is long enough, finalize it and start new one
            merged.append(current_segment)
            current_segment = {
                "start": current_caption["start"],
                "end": current_caption["end"],
                "text": current_caption["text"]
            }

    # Add the last segment if it's long enough
    final_duration = current_segment["end"] - current_segment["start"]
    if final_duration >= 0.5:
        merged.append(current_segment)

    return merged


def extract_youtube_captions(url: str):
    """Extracts captions from YouTube video without downloading the video."""
    try:
        print(f"Attempting to extract captions from: {url}")

        # Check cache first
        cache_key = get_cache_key(url=url)
        if is_cached(cache_key):
            print(f"Using cached captions for URL: {url}")
            cached_data = load_from_cache(cache_key)
            return cached_data["captions"], None

        # First, try to get available captions
        result = subprocess.run([
            "yt-dlp",
            "--list-subs",
            url
        ], capture_output=True, text=True)

        print(f"List subs stdout: {result.stdout}")
        print(f"List subs stderr: {result.stderr}")
        print(f"List subs return code: {result.returncode}")

        if result.returncode != 0:
            return None, "Failed to get caption list"

        # Check if there are any captions available
        if "No subtitles found" in result.stdout:
            return None, "No captions available for this video"

        # Try to download the best available captions (prefer manual over auto-generated)
        caption_result = subprocess.run([
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",  # Prefer English
            "--sub-format", "vtt",
            "--skip-download",
            "--output", os.path.join(TS_DIR, "%(id)s.%(ext)s"),
            url
        ], capture_output=True, text=True)

        print(f"Download captions stdout: {caption_result.stdout}")
        print(f"Download captions stderr: {caption_result.stderr}")
        print(f"Download captions return code: {caption_result.returncode}")

        if caption_result.returncode != 0:
            return None, f"Failed to download captions: {caption_result.stderr}"

        # Find the downloaded caption file
        caption_files = [f for f in os.listdir(TS_DIR) if f.endswith('.vtt')]
        print(f"Found caption files: {caption_files}")

        if not caption_files:
            return None, "No caption files found after download attempt"

        # Use the most recent caption file
        caption_file = os.path.join(TS_DIR, caption_files[-1])
        print(f"Using caption file: {caption_file}")

        # Parse VTT file and convert to our format
        captions = parse_vtt_to_captions(caption_file)
        print(f"Parsed {len(captions)} captions")

        # Merge short captions into longer segments
        merged_captions = merge_short_captions(captions, min_duration=2.5)
        print(f"Merged into {len(merged_captions)} segments")

        # Cache the captions
        metadata = {
            "url": url,
            "method": "youtube_captions",
            "original_segments": len(captions),
            "merged_segments": len(merged_captions)
        }
        save_to_cache(cache_key, merged_captions, metadata)

        # Clean up the caption file
        os.remove(caption_file)

        return merged_captions, None

    except Exception as e:
        print(f"Exception in extract_youtube_captions: {e}")
        return None, f"Error extracting captions: {str(e)}"


def parse_vtt_to_captions(vtt_file_path: str):
    """Parses VTT file and converts to our caption format"""
    captions = []

    try:
        print(f"Parsing VTT file: {vtt_file_path}")

        with open(vtt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"VTT file content length: {len(content)}")
        print(f"First 500 chars of VTT: {content[:500]}")

        # Split into caption blocks
        blocks = content.strip().split('\n\n')
        print(f"Found {len(blocks)} blocks in VTT file")

        for i, block in enumerate(blocks):
            lines = block.strip().split('\n')
            print(f"Block {i}: {len(lines)} lines")

            if len(lines) >= 2:
                # Skip the "WEBVTT" header and metadata
                if lines[0].startswith('WEBVTT') or lines[0].startswith('Kind:') or lines[0].startswith('Language:'):
                    print(f"Block {i}: Skipping header/metadata")
                    continue

                # Look for timestamp line (should be the first line that contains -->)
                timestamp_line = None
                text_lines = []

                for line in lines:
                    if '-->' in line and timestamp_line is None:
                        timestamp_line = line
                    elif timestamp_line is not None:
                        text_lines.append(line)

                if timestamp_line:
                    print(f"Block {i}: Timestamp line: {timestamp_line}")

                    # Extract just the timestamp part (before any additional attributes)
                    timestamp_part = timestamp_line.split(' ')[0] + ' --> ' + timestamp_line.split(' ')[2]
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', timestamp_part)

                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)

                        # Convert timestamp to seconds
                        start_seconds = timestamp_to_seconds(start_time)
                        end_seconds = timestamp_to_seconds(end_time)

                        # Clean up the text by removing styling tags and inline timestamps
                        text = ' '.join(text_lines).strip()

                        # Remove styling tags like <c>, </c>, <00:00:02.280>, etc.
                        text = re.sub(r'<[^>]*>', '', text)

                        # Clean up extra whitespace
                        text = re.sub(r'\s+', ' ', text).strip()

                        print(f"Block {i}: Start={start_seconds}, End={end_seconds}, Text='{text[:50]}...'")

                        if text and len(text) > 1:  # Only add if there's actual text (more than 1 char)
                            captions.append({
                                "start": round(start_seconds, 2),
                                "end": round(end_seconds, 2),
                                "text": text
                            })
                            print(f"Block {i}: Added caption")
                        else:
                            print(f"Block {i}: No meaningful text, skipping")
                    else:
                        print(f"Block {i}: No timestamp match in '{timestamp_part}'")
                else:
                    print(f"Block {i}: No timestamp line found")
            else:
                print(f"Block {i}: Not enough lines ({len(lines)})")

    except Exception as e:
        print(f"Error parsing VTT file: {e}")

    print(f"Final caption count: {len(captions)}")
    return captions


def timestamp_to_seconds(timestamp: str) -> float:
    """Convert VTT timestamp (HH:MM:SS.mmm) to seconds"""
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])

    return hours * 3600 + minutes * 60 + seconds


async def fallback_to_whisper(url: str):
    """Fallback function to use Whisper transcription"""
    print(f"Falling back to Whisper for: {url}")

    # Check cache first
    cache_key = get_cache_key(url=url)
    if is_cached(cache_key):
        print(f"Using cached Whisper captions for URL: {url}")
        cached_data = load_from_cache(cache_key)
        return {
            "captions": cached_data["captions"],
            "method": "whisper_transcription",
            "cached": True,
            "metadata": cached_data.get("metadata", {})
        }

    # First, get video info to check duration
    info_result = subprocess.run([
        "yt-dlp",
        "--get-duration",
        url
    ], capture_output=True, text=True)

    if info_result.returncode == 0:
        duration_str = info_result.stdout.strip()
        try:
            # Parse duration (format: HH:MM:SS or MM:SS)
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                duration_minutes = hours * 60 + minutes + seconds / 60
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                duration_minutes = minutes + seconds / 60
            else:
                duration_minutes = float(parts[0]) / 60  # seconds to minutes

            print(f"Video duration: {duration_minutes:.1f} minutes")

            # Limit to 30 minutes for processing
            if duration_minutes > 30:
                return {
                    "error": "Video too long (max 30 minutes allowed)",
                    "detail": f"Video is {duration_minutes:.1f} minutes long"
                }
        except:
            print("Could not parse video duration, proceeding anyway")

    video_id = str(uuid.uuid4())
    file_path = os.path.join(TS_DIR, f"{video_id}.mp4")

    # Download audio-only to save bandwidth and storage
    result = subprocess.run([
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio",  # Audio only
        "-o", file_path,
        url
    ], capture_output=True)

    if result.returncode != 0:
        return {
            "error": "Failed to download video",
            "detail": result.stderr.decode(),
        }

    captions = transcribe_with_whisper(file_path)

    # Cache the captions
    metadata = {
        "url": url,
        "method": "whisper_transcription",
        "video_id": video_id
    }
    save_to_cache(cache_key, captions, metadata)

    # Clean up the downloaded video file
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Cleaned up downloaded file: {file_path}")

    return {
        "captions": captions,
        "method": "whisper_transcription",
        "cached": False,
        "metadata": metadata
    }


# Main API functions
async def upload_video(file: UploadFile):
    """Handle video upload and transcription"""
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TS_DIR, f"{file_id}{file_ext}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Generate file hash for caching
    file_hash = get_file_hash(file_path)
    cache_key = get_cache_key(file_hash=file_hash)

    # Check if captions are already cached
    if is_cached(cache_key):
        print(f"Using cached captions for file hash: {file_hash}")
        cached_data = load_from_cache(cache_key)

        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "captions": cached_data["captions"],
            "cached": True,
            "metadata": cached_data.get("metadata", {})
        }

    # Generate captions and cache them
    print(f"Generating captions for file hash: {file_hash}")
    captions = transcribe_with_whisper(file_path)

    # Save to cache with metadata
    metadata = {
        "filename": file.filename,
        "file_size": os.path.getsize(file_path),
        "method": "whisper_transcription"
    }
    save_to_cache(cache_key, captions, metadata)

    # Clean up the uploaded file
    if os.path.exists(file_path):
        os.remove(file_path)

    return {
        "captions": captions,
        "cached": False,
        "metadata": metadata
    }


async def transcribe_youtube(url: str):
    """Handle YouTube video transcription"""
    # Check cache first
    cache_key = get_cache_key(url=url)
    if is_cached(cache_key):
        print(f"Using cached captions for URL: {url}")
        cached_data = load_from_cache(cache_key)
        return {
            "captions": cached_data["captions"],
            "method": cached_data.get("metadata", {}).get("method", "unknown"),
            "cached": True,
            "metadata": cached_data.get("metadata", {})
        }

    # First, try to extract captions without downloading the video
    captions, error = extract_youtube_captions(url)

    if captions:
        return {"captions": captions, "method": "youtube_captions", "cached": False}

    # If no captions available, fall back to downloading and transcribing
    print(f"Falling back to video download: {error}")

    # Check video duration first
    info_result = subprocess.run([
        "yt-dlp",
        "--get-duration",
        url
    ], capture_output=True, text=True)

    if info_result.returncode == 0:
        duration_str = info_result.stdout.strip()
        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                duration_minutes = hours * 60 + minutes + seconds / 60
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                duration_minutes = minutes + seconds / 60
            else:
                duration_minutes = float(parts[0]) / 60

            print(f"Video duration: {duration_minutes:.1f} minutes")

            if duration_minutes > 30:
                return {
                    "error": "Video too long (max 30 minutes allowed)",
                    "detail": f"Video is {duration_minutes:.1f} minutes long"
                }
        except:
            print("Could not parse video duration, proceeding anyway")

    video_id = str(uuid.uuid4())
    file_path = os.path.join(TS_DIR, f"{video_id}.mp4")

    # Download audio-only to save bandwidth and storage
    result = subprocess.run([
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio",  # Audio only
        "-o", file_path,
        url
    ], capture_output=True)

    if result.returncode != 0:
        return {
            "error": "Failed to download video",
            "detail": result.stderr.decode(),
        }

    captions = transcribe_with_whisper(file_path)

    # Cache the captions
    metadata = {
        "url": url,
        "method": "whisper_transcription",
        "video_id": video_id
    }
    save_to_cache(cache_key, captions, metadata)

    # Clean up the downloaded video file
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Cleaned up downloaded file: {file_path}")

    return {
        "captions": captions,
        "method": "whisper_transcription",
        "cached": False,
        "metadata": metadata
    }


async def extract_youtube_captions_only(url: str):
    """Extracts only YouTube captions without fallback to video download."""
    # Check cache first
    cache_key = get_cache_key(url=url)
    if is_cached(cache_key):
        print(f"Using cached captions for URL: {url}")
        cached_data = load_from_cache(cache_key)
        metadata = cached_data.get("metadata", {})

        # Only return if cached data is from YouTube captions
        if metadata.get("method") == "youtube_captions":
            return {
                "captions": cached_data["captions"],
                "method": "youtube_captions",
                "cached": True,
                "metadata": metadata
            }

    captions, error = extract_youtube_captions(url)

    if error:
        return {"error": error}

    return {
        "captions": captions,
        "method": "youtube_captions",
        "cached": False
    }


async def extract_youtube_captions_with_duration(url: str, min_duration: float = 2.5):
    """Extracts YouTube captions with custom minimum duration for merging."""
    try:
        print(f"Attempting to extract captions from: {url} with min_duration: {min_duration}")

        # Check cache first
        cache_key = get_cache_key(url=url)
        if is_cached(cache_key):
            print(f"Using cached captions for URL: {url}")
            cached_data = load_from_cache(cache_key)
            cached_captions = cached_data["captions"]

            # Re-merge with the requested min_duration
            merged_captions = merge_short_captions(cached_captions, min_duration=min_duration)

            return {
                "captions": merged_captions,
                "method": "youtube_captions",
                "cached": True,
                "metadata": cached_data.get("metadata", {})
            }

        # First, try to get available captions
        result = subprocess.run([
            "yt-dlp",
            "--list-subs",
            url
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": "Failed to get caption list"}

        # Check if there are any captions available
        if "No subtitles found" in result.stdout:
            return {"error": "No captions available for this video"}

        # Try to download the best available captions
        caption_result = subprocess.run([
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "--output", os.path.join(TS_DIR, "%(id)s.%(ext)s"),
            url
        ], capture_output=True, text=True)

        if caption_result.returncode != 0:
            return {"error": f"Failed to download captions: {caption_result.stderr}"}

        # Find the downloaded caption file
        caption_files = [f for f in os.listdir(TS_DIR) if f.endswith('.vtt')]
        if not caption_files:
            return {"error": "No caption files found after download attempt"}

        # Use the most recent caption file
        caption_file = os.path.join(TS_DIR, caption_files[-1])

        # Parse VTT file and convert to our format
        captions = parse_vtt_to_captions(caption_file)
        print(f"Parsed {len(captions)} captions")

        # Merge short captions into longer segments with custom duration
        merged_captions = merge_short_captions(captions, min_duration=min_duration)
        print(f"Merged into {len(merged_captions)} segments with min_duration={min_duration}")

        # Cache the original captions (before merging) so we can re-merge with different durations
        metadata = {
            "url": url,
            "method": "youtube_captions",
            "original_segments": len(captions),
            "merged_segments": len(merged_captions),
            "min_duration_used": min_duration
        }
        save_to_cache(cache_key, captions, metadata)  # Cache original captions, not merged ones

        # Clean up the caption file
        os.remove(caption_file)

        return {
            "captions": merged_captions,
            "method": "youtube_captions",
            "cached": False,
            "metadata": metadata
        }

    except Exception as e:
        return {"error": f"Error extracting captions: {str(e)}"}


async def smart_extract_captions(url: str, min_duration: float = 2.5):
    """Smart extraction: tries YouTube captions first, falls back to Whisper if quality is poor."""
    try:
        print(f"Smart extraction for: {url} with min_duration: {min_duration}")

        # Check cache first
        cache_key = get_cache_key(url=url)
        if is_cached(cache_key):
            print(f"Using cached captions for URL: {url}")
            cached_data = load_from_cache(cache_key)
            cached_captions = cached_data["captions"]
            metadata = cached_data.get("metadata", {})

            # If cached captions are from YouTube, re-merge with requested duration
            if metadata.get("method") == "youtube_captions":
                merged_captions = merge_short_captions(cached_captions, min_duration=min_duration)
                quality_assessment = assess_caption_quality(merged_captions)

                return {
                    "captions": merged_captions,
                    "method": "youtube_captions",
                    "cached": True,
                    "quality_assessment": quality_assessment,
                    "metadata": metadata
                }
            else:
                # Cached captions are from Whisper, return as-is
                return {
                    "captions": cached_captions,
                    "method": "whisper_transcription",
                    "cached": True,
                    "metadata": metadata
                }

        # First, try to get YouTube captions
        captions, error = extract_youtube_captions(url)

        if error:
            print(f"YouTube caption extraction failed: {error}")
            # Fall back to Whisper
            return await fallback_to_whisper(url)

        # Assess the quality of YouTube captions
        quality_assessment = assess_caption_quality(captions)
        print(f"Quality assessment: {quality_assessment}")

        if quality_assessment["recommend_whisper"]:
            print("YouTube captions quality is poor, falling back to Whisper")
            return await fallback_to_whisper(url)

        # YouTube captions are good enough, merge them
        merged_captions = merge_short_captions(captions, min_duration=min_duration)

        # Cache the original captions (before merging)
        metadata = {
            "url": url,
            "method": "youtube_captions",
            "original_segments": len(captions),
            "merged_segments": len(merged_captions),
            "min_duration_used": min_duration,
            "quality_assessment": quality_assessment
        }
        save_to_cache(cache_key, captions, metadata)  # Cache original captions

        return {
            "captions": merged_captions,
            "method": "youtube_captions",
            "cached": False,
            "quality_assessment": quality_assessment,
            "metadata": metadata
        }

    except Exception as e:
        print(f"Error in smart extraction: {e}")
        return await fallback_to_whisper(url)


# Cache management functions
async def get_cache_info():
    """Get information about the cache directory and cached entries"""
    from src.cache import get_cache_info as cache_get_info
    return await cache_get_info()


async def clear_cache():
    """Clear all cached captions"""
    from src.cache import clear_cache as cache_clear
    return await cache_clear()


async def delete_cache_entry(cache_key: str):
    """Delete a specific cache entry"""
    from src.cache import delete_cache_entry as cache_delete_entry
    return await cache_delete_entry(cache_key)
