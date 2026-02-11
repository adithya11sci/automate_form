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

# --- Path Resolution for Vercel ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent # The root directory (d:\form_filler)
FRONTEND_DIR = BASE_DIR / "frontend"

# Vercel Environment Check
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = Path("/var/task/frontend")

# Initialize FastAPI
app = FastAPI(title="AutoFill-GForm Pro")

# --- Middleware ---
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    if request.url.path.startswith("/api"):
        try:
            from app.database import init_db
            await init_db()
        except Exception as db_err:
            return JSONResponse(
                status_code=500,
                content={"detail": str(db_err), "type": "database_error"}
            )
    return await call_next(request)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Include API Routes
if not STARTUP_ERROR:
    app.include_router(auth_routes.router)
    app.include_router(profile_routes.router)
    app.include_router(form_routes.router)

# --- Static Files Mounting (The proper way to serve CSS/JS) ---
if FRONTEND_DIR.exists():
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
    if (FRONTEND_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

# --- Frontend Page Routes ---
@app.get("/")
async def root():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse(content=f"<h1>Backend Active</h1><p>Frontend not found at {FRONTEND_DIR}</p>")

@app.get("/dashboard")
async def serve_dashboard():
    path = FRONTEND_DIR / "dashboard.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse(content="Dashboard not found", status_code=404)

@app.get("/profile")
async def serve_profile():
    path = FRONTEND_DIR / "profile.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse(content="Profile not found", status_code=404)

@app.get("/history")
async def serve_history():
    path = FRONTEND_DIR / "history.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse(content="History not found", status_code=404)

@app.get("/api/ping")
async def ping():
    return {"status": "alive", "frontend_found": FRONTEND_DIR.exists(), "error": STARTUP_ERROR}
