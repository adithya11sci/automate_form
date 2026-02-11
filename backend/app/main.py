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

# Enable CORS for all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Path Resolution
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # Only try to connect to DB for API routes
    if request.url.path.startswith("/api"):
        try:
            from app.database import init_db
            await init_db()
        except Exception as db_err:
            import traceback
            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Database Connection Error: {str(db_err)}",
                    "trace": traceback.format_exc(),
                    "type": "database_error"
                }
            )
    
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "trace": traceback.format_exc()}
        )

# Include API Routers
if not STARTUP_ERROR:
    app.include_router(auth_routes.router)
    app.include_router(profile_routes.router)
    app.include_router(form_routes.router)

# --- Serving Frontend (Manual Routing for Vercel stability) ---

@app.get("/api/ping")
async def ping():
    return {"status": "alive", "error": STARTUP_ERROR}

@app.get("/")
async def serve_index():
    path = FRONTEND_DIR / "index.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse(f"Index not found at {path}")

@app.get("/dashboard")
async def serve_dashboard():
    path = FRONTEND_DIR / "dashboard.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse("Dashboard not found")

@app.get("/profile")
async def serve_profile():
    path = FRONTEND_DIR / "profile.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse("Profile not found")

@app.get("/history")
async def serve_history():
    path = FRONTEND_DIR / "history.html"
    return FileResponse(str(path)) if path.exists() else HTMLResponse("History not found")

# Serve static files (CSS/JS)
@app.get("/{folder}/{filename}")
async def serve_static(folder: str, filename: str):
    if folder in ["css", "js", "assets"]:
        path = FRONTEND_DIR / folder / filename
        if path.exists():
            return FileResponse(str(path))
    return HTMLResponse("File not found", status_code=404)
