import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- Global Diagnostics ---
STARTUP_ERROR = None
try:
    from app.config import CORS_ORIGINS
    from app.database import init_db
    from app.routes import auth_routes, profile_routes, form_routes
except Exception as e:
    import traceback
    STARTUP_ERROR = f"Startup Error: {str(e)}\n{traceback.format_exc()}"

# Initialize FastAPI
app = FastAPI(title="AutoFill-GForm Pro")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fix for Vercel Static Pathing
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = Path("/var/task/frontend")

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    if request.url.path.startswith("/api"):
        try:
            from app.database import init_db
            await init_db()
        except Exception as db_err:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Database Connection Error: {str(db_err)}", "type": "db_error"}
            )
    return await call_next(request)

# Include API Routes
if not STARTUP_ERROR:
    app.include_router(auth_routes.router)
    app.include_router(profile_routes.router)
    app.include_router(form_routes.router)

# --- Routes ---

@app.get("/api/ping")
async def ping():
    return {"status": "alive", "db": "connected", "error": STARTUP_ERROR}

@app.get("/")
async def root():
    path = FRONTEND_DIR / "index.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse("Frontend not found")

@app.get("/{folder}/{filename}")
async def serve_static(folder: str, filename: str):
    if folder in ["css", "js", "assets"]:
        path = FRONTEND_DIR / folder / filename
        if path.exists():
            return FileResponse(str(path))
    return HTMLResponse("404 Not Found", status_code=404)

@app.get("/{page_name}")
async def serve_page(page_name: str):
    if page_name in ["dashboard", "profile", "history"]:
        path = FRONTEND_DIR / f"{page_name}.html"
        if path.exists():
            return FileResponse(str(path))
    return HTMLResponse("404 Not Found", status_code=404)
