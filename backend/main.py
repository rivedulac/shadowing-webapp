from fastapi import Body, FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import src.server as server

app = FastAPI()

# Set up CORS to be reachable from frontend side
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/transcribe")
async def upload_video(file: UploadFile = File(...)):
    return await server.upload_video(file)


@app.post("/transcribe-youtube")
async def transcribe_youtube(url: str = Body(..., embed=True)):
    return await server.transcribe_youtube(url)


@app.post("/extract-youtube-captions")
async def extract_youtube_captions_only(url: str = Body(..., embed=True)):
    return await server.extract_youtube_captions_only(url)


@app.post("/extract-youtube-captions-with-duration")
async def extract_youtube_captions_with_duration(
    url: str = Body(..., embed=True),
    min_duration: float = Body(2.5, embed=True)
):
    return await server.extract_youtube_captions_with_duration(url, min_duration)


@app.post("/smart-extract-captions")
async def smart_extract_captions(
    url: str = Body(..., embed=True),
    min_duration: float = Body(2.5, embed=True)
):
    return await server.smart_extract_captions(url, min_duration)


@app.get("/cache/info")
async def get_cache_info():
    return await server.get_cache_info()


@app.delete("/cache/clear")
async def clear_cache():
    return await server.clear_cache()


@app.delete("/cache/{cache_key}")
async def delete_cache_entry(cache_key: str):
    return await server.delete_cache_entry(cache_key)
