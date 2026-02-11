import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Global error for diagnostics
STARTUP_ERROR = None

try:
    from app.config import CORS_ORIGINS
    from app.database import init_db
    from app.routes import auth_routes, profile_routes, form_routes
except Exception as e:
    import traceback
    STARTUP_ERROR = f"Startup Import Error: {str(e)}\n{traceback.format_exc()}"

# Initialize FastAPI
app = FastAPI(title="AutoFill-GForm Pro")

# Middleware for DB & Debugging
@app.middleware("http")
async def diagnostic_middleware(request: Request, call_next):
    # Route for health check
    if request.url.path == "/api/ping":
        return JSONResponse({"status": "alive", "startup_error": STARTUP_ERROR})

    # Try to init DB on every API call (idempotent)
    if request.url.path.startswith("/api"):
        try:
            from app.database import init_db
            await init_db()
        except Exception as db_err:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Database Error: {str(db_err)}", "type": "db_connection_fail"}
            )
            
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "trace": traceback.format_exc()}
        )

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Include routes
if not STARTUP_ERROR:
    app.include_router(auth_routes.router)
    app.include_router(profile_routes.router)
    app.include_router(form_routes.router)

# Serve Frontend
@app.get("/")
async def root():
    try:
        frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html"
        if not frontend_path.exists():
             frontend_path = Path("/var/task/frontend/index.html")
             
        if frontend_path.exists():
            with open(frontend_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Backend is running</h1><p>But index.html was not found in static paths.</p>")
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    # Try to serve dashboard.html, profile.html etc.
    frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
    if not frontend_path.exists():
        frontend_path = Path("/var/task/frontend")
        
    file_path = frontend_path / f"{full_path}.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    
    # Check for css/js folders
    static_file = frontend_path / full_path
    if static_file.exists() and static_file.is_file():
        return FileResponse(str(static_file))
        
    return HTMLResponse(content="404 Not Found", status_code=404)
