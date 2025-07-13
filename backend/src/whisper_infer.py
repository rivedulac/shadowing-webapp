import whisper

model = whisper.load_model("base")

def transcribe_with_whisper(file_path: str):
    result = model.transcribe(file_path)
    segments = result.get("segments", [])
    caption_list = []

    for seg in segments:
        caption_list.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })

    return caption_list
