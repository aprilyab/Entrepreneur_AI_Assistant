# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.api.auth import router as auth_router
from app.api.plans import router as plans_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables
    await init_db()
    from app.services.generation_jobs import recover_incomplete_generation_jobs
    await recover_incomplete_generation_jobs()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent AI assistant for entrepreneurs. Generates business plans, viability scores, and strategic insights using LangGraph.",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(plans_router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
