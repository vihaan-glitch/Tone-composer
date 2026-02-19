from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from gemini_music import GeminiMusicError, generate_gemini_music_audio

APP_TITLE = "Gemini Lyria Audio API"

logger = logging.getLogger(__name__)

class GeminiAudioRequest(BaseModel):
    prompt: str = Field(default="", description="Text prompt describing the tone to generate.")
    bpm: int = Field(default=120, ge=40, le=240)
    density: float = Field(default=0.8, ge=0.0, le=1.0)
    brightness: float = Field(default=0.7, ge=0.0, le=1.0)
    guidance: float = Field(default=4.0, ge=0.1, le=20.0)
    duration_seconds: int = Field(default=12, ge=6, le=30)

app = FastAPI(title=APP_TITLE)

frontend_path = Path(__file__).resolve().parents[1] / "web" / "dist"
if frontend_path.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
else:
    logger.warning(
        "Frontend build not found at `%s`. Run `npm run build` inside web/ so FastAPI can serve the SPA.",
        frontend_path,
    )

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://tone-composer-mu.vercel.app",
]
cors_env = os.environ.get("CORS_ALLOW_ORIGINS", "").strip()
allow_origins = [o.strip() for o in cors_env.split(",") if o.strip()] if cors_env else default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/gemini/audio/wav")
def gemini_audio(req: GeminiAudioRequest):
    clean_prompt = (req.prompt or "").strip()
    if not clean_prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    try:
        wav = generate_gemini_music_audio(
            prompt=clean_prompt,
            bpm=req.bpm,
            density=req.density,
            brightness=req.brightness,
            guidance=req.guidance,
            duration_seconds=req.duration_seconds,
        )
        return Response(content=wav, media_type="audio/wav")
    except GeminiMusicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
