from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from config import settings
from database import init_db
from utils.logger import logger
from routers import upload, translate, status, download, websocket

app = FastAPI(
    title="LinguaFuse AI - Video Translation API",
    version="1.0.0",
    description="Production-ready backend for AI-powered multilingual video translation"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "*" # Keeping wildcard for broader local dev, but explicitly listing Live Server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing LinguaFuse AI Backend...")
    # Initialize DB schema
    await init_db()
    logger.info("Startup complete.")

@app.get("/")
async def root():
    return {"message": "LinguaFuse AI API is running"}

# Include routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(translate.router, tags=["Translation"])
app.include_router(status.router, tags=["Status"])
app.include_router(download.router, tags=["Download"])
app.include_router(websocket.router, tags=["WebSockets"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
