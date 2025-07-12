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
        # First, try to get available captions
        result = subprocess.run([
            "yt-dlp",
            "--list-subs",
            url
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return None, "Failed to get caption list"
        
        # Check if there are any captions available
        if "No subtitles found" in result.stdout:
            return None, "No captions available for this video"
        
        # Try to download the best available captions (prefer auto-generated if available)
        caption_result = subprocess.run([
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-format", "vtt",
            "--skip-download",
            "--output", os.path.join(TS_DIR, "%(id)s.%(ext)s"),
            url
        ], capture_output=True, text=True)
        
        if caption_result.returncode != 0:
            return None, f"Failed to download captions: {caption_result.stderr}"
        
        # Find the downloaded caption file
        caption_files = [f for f in os.listdir(TS_DIR) if f.endswith('.vtt')]
        if not caption_files:
            return None, "No caption files found after download attempt"
        
        # Use the most recent caption file
        caption_file = os.path.join(TS_DIR, caption_files[-1])
        
        # Parse VTT file and convert to our format
        captions = parse_vtt_to_captions(caption_file)
        
        # Clean up the caption file
        os.remove(caption_file)
        
        return captions, None
        
    except Exception as e:
        return None, f"Error extracting captions: {str(e)}"

def parse_vtt_to_captions(vtt_file_path: str):
    """Parses VTT file and converts to our caption format"""
    captions = []
    
    try:
        with open(vtt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into caption blocks
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Skip the "WEBVTT" header
                if lines[0].startswith('WEBVTT'):
                    continue
                
                # Parse timestamp line
                timestamp_line = lines[1]
                time_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', timestamp_line)
                
                if time_match:
                    start_time = time_match.group(1)
                    end_time = time_match.group(2)
                    
                    # Convert timestamp to seconds
                    start_seconds = timestamp_to_seconds(start_time)
                    end_seconds = timestamp_to_seconds(end_time)
                    
                    # Get the text (all lines after timestamp)
                    text = ' '.join(lines[2:]).strip()
                    
                    if text:  # Only add if there's actual text
                        captions.append({
                            "start": round(start_seconds, 2),
                            "end": round(end_seconds, 2),
                            "text": text
                        })
    
    except Exception as e:
        print(f"Error parsing VTT file: {e}")
    
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
    
    return {"captions": captions}
