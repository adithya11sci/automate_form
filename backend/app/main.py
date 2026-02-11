import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import CORS_ORIGINS
from app.database import init_db
from app.routes import auth_routes, profile_routes, form_routes

# --- Robust Path Helper for Vercel ---
BASE_DIR = Path(__file__).resolve().parent.parent # backend/
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

if not FRONTEND_DIR.exists():
    # Attempt to find frontend if pathing is different on Vercel
    FRONTEND_DIR = Path("/var/task/frontend") 
    if not FRONTEND_DIR.exists():
        FRONTEND_DIR = ROOT_DIR # Fallback to root

# Initialize FastAPI
app = FastAPI(title="AutoFill-GForm Pro", version="1.0.0")

# Middleware for DB
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # Only init DB for API routes
    if request.url.path.startswith("/api"):
        await init_db()
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "msg": "Critial Error in Middleware"}
        )

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Include routes
app.include_router(auth_routes.router)
app.include_router(profile_routes.router)
app.include_router(form_routes.router)

# Serve Frontend
@app.get("/")
async def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(str(FRONTEND_DIR / "dashboard.html"))

@app.get("/profile")
async def serve_profile():
    return FileResponse(str(FRONTEND_DIR / "profile.html"))

@app.get("/history")
async def serve_history():
    return FileResponse(str(FRONTEND_DIR / "history.html"))

# Static Files - wrapping in try/except to prevent 500 if folder missing
try:
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
except:
    pass

@app.get("/api/ping")
async def ping():
    return {"status": "ok", "db_url_set": bool(os.getenv("MONGODB_URI"))}
