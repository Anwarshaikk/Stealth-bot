import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import weaviate

from .routers import resume, jobs, apply, settings

# Load environment variables from .env file
load_dotenv()

# Lifespan context manager for Weaviate client
@asynccontextmanager
def lifespan(app: FastAPI):
    app.state.weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL"))
    try:
        yield
    finally:
        app.state.weaviate_client.close()

app = FastAPI(lifespan=lifespan)

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
