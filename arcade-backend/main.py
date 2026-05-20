"""Arcade Hub backend - FastAPI entry point.

Serves the built React SPA (./static) at /, and the JSON API under /api/*.

Run locally:
    uvicorn main:app --reload --port 8000
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import (
    admin_router,
    auth_router,
    health_router,
    play_router,
    wallet_router,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    from app.services.admin_bootstrap import bootstrap_admin
    bootstrap_admin()
    yield


app = FastAPI(
    title="Arcade Hub API",
    version="1.0.0",
    description="Backend for the Arcade Hub web app (auth, wallet, games, leaderboard, admin).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(health_router.router)
app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(wallet_router.router, prefix="/api/wallet", tags=["wallet"])
app.include_router(play_router.router, prefix="/api/games", tags=["games"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["admin"])


# ---------- Serve the built React SPA ----------
STATIC_DIR = Path(__file__).parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"

if STATIC_DIR.is_dir() and INDEX_FILE.is_file():
    # Hashed JS/CSS assets
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def spa_root():
        return FileResponse(INDEX_FILE)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        # Don't swallow API/doc routes
        reserved = ("api/", "docs", "redoc", "openapi.json")
        if full_path.startswith(reserved):
            raise HTTPException(status_code=404, detail="Not Found")

        # Serve real static files (favicon, robots.txt, etc.) if present
        candidate = STATIC_DIR / full_path
        if candidate.is_file():
            return FileResponse(candidate)

        # Otherwise hand off to the SPA router
        return FileResponse(INDEX_FILE)

else:
    # Fallback landing page when the SPA bundle isn't shipped with the image
    @app.get("/", include_in_schema=False)
    async def root():
        return JSONResponse(
            {
                "name": "Arcade Hub API",
                "version": "1.0.0",
                "docs": "/docs",
                "note": "Frontend bundle not found in ./static",
            }
        )
