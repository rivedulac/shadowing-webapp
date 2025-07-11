import shutil
import os
import uuid

from fastapi import FastAPI, File, UploadFile
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
