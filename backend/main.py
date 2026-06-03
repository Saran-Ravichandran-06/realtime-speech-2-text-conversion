from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as api_router
from routes import websocket_routes, file_routes, healthcheck
from config import HOST, PORT
from asr.faster_whisper_asr import FasterWhisperTranscriber

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.transcriber = FasterWhisperTranscriber()
    logger.info("Transcription model ready")
    yield
    logger.info("Shutting down Speech2Text backend")


app = FastAPI(title="Speech2Text Backend", lifespan=lifespan)

# CORS
origins = ["http://127.0.0.1:5500", "http://localhost:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(healthcheck.router)
app.include_router(file_routes.router)
app.include_router(websocket_routes.router)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
