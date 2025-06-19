import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .routers import resume, jobs, apply, settings

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Stealth Bot API", version="0.1.0")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck endpoint
@app.get("/ping")
def ping():
    return JSONResponse({"pong": True})

# Mount routers
app.include_router(resume.router, prefix="/resume")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(apply.router, prefix="/apply")
app.include_router(settings.router, prefix="/settings")
