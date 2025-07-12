import shutil
import os
import subprocess
import uuid
import json
import re

from fastapi import Body, FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from whisper_infer import transcribe_with_whisper

app = FastAPI()

# Set up CORS to be reachable from frontend side
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TS_DIR = "transcribe"
os.makedirs(TS_DIR, exist_ok=True)

@app.post("/transcribe")
async def upload_video(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    file_path = os.path.join(TS_DIR, f"{file_id}{file_ext}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    captions = transcribe_with_whisper(file_path)
    return {"captions": captions}

def extract_youtube_captions(url: str):
    """Extracts captions from YouTube video without downloading the video."""
    try:
        print(f"Attempting to extract captions from: {url}")
        
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
        
        # Clean up the caption file
        os.remove(caption_file)
        
        return captions, None
        
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

@app.post("/transcribe-youtube")
async def transcribe_youtube(url: str = Body(..., embed=True)):
    # First, try to extract captions without downloading the video
    captions, error = extract_youtube_captions(url)
    
    if captions:
        return {"captions": captions, "method": "youtube_captions"}
    
    # If no captions available, fall back to downloading and transcribing
    print(f"Falling back to video download: {error}")
    
    video_id = str(uuid.uuid4())
    file_path = os.path.join(TS_DIR, f"{video_id}.mp4")

    result = subprocess.run([
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "-o", file_path,
        url
    ], capture_output=True)

    if result.returncode != 0:
        return {
            "error": "Failed to download video", 
            "detail": result.stderr.decode(),
        }
    
    captions = transcribe_with_whisper(file_path)
    
    # Clean up the downloaded video file
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {"captions": captions, "method": "whisper_transcription"}

@app.post("/extract-youtube-captions")
async def extract_youtube_captions_only(url: str = Body(..., embed=True)):
    """Extracts only YouTube captions without fallback to video download."""
    captions, error = extract_youtube_captions(url)
    
    if error:
        return {"error": error}
    
    return {"captions": captions, "method": "youtube_captions"}
