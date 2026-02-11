import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Global error for diagnostics
STARTUP_ERROR = None

try:
    # Attempt imports
    from app.config import CORS_ORIGINS
    from app.database import init_db
    from app.routes import auth_routes, profile_routes, form_routes
except Exception as e:
    import traceback
    STARTUP_ERROR = f"Import Error: {str(e)}\n{traceback.format_exc()}"

# Initialize FastAPI
app = FastAPI(title="AutoFill-GForm Pro Diagnostics")

# Middleware for DB & Debugging
@app.middleware("http")
async def diagnostic_middleware(request: Request, call_next):
    if STARTUP_ERROR and request.url.path == "/":
        return HTMLResponse(content=f"<h1>Startup Error</h1><pre>{STARTUP_ERROR}</pre>", status_code=500)
    
    if request.url.path.startswith("/api"):
        try:
            from app.database import init_db
            await init_db()
        except:
            pass
            
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Only include routers if no startup error
if not STARTUP_ERROR:
    try:
        app.include_router(auth_routes.router)
        app.include_router(profile_routes.router)
        app.include_router(form_routes.router)
    except Exception as e:
        STARTUP_ERROR = f"Router Inclusion Error: {str(e)}"

# Serve index or show error
@app.get("/")
async def root():
    if STARTUP_ERROR:
        return HTMLResponse(content=f"<h1>System Failure</h1><pre>{STARTUP_ERROR}</pre>", status_code=500)
    
    # Try to return the index.html from frontend
    try:
        frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html"
        if not frontend_path.exists():
             frontend_path = Path("/var/task/frontend/index.html")
             
        if frontend_path.exists():
            with open(frontend_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return {"status": "ok", "msg": "Backend is running, but index.html was not found."}
    except Exception as e:
        return {"status": "ok", "error_finding_html": str(e)}

@app.get("/api/ping")
async def ping():
    return {"status": "alive", "error": STARTUP_ERROR}
