"""
AutoFill-GForm Pro — FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import CORS_ORIGINS, FRONTEND_DIR
from app.database import init_db
from app.routes import auth_routes, profile_routes, form_routes

# Initialize FastAPI
app = FastAPI(
    title="AutoFill-GForm Pro",
    description="Intelligent Google Form Auto Filling Platform",
    version="1.0.0",
)

# Middleware to ensure DB connection on every request (Needed for Vercel)
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    if not request.url.path.startswith("/css") and not request.url.path.startswith("/js"):
        await init_db()
    response = await call_next(request)
    return response

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)
app.include_router(profile_routes.router)
app.include_router(form_routes.router)

# Serve frontend static files
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


@app.on_event("startup")
async def on_startup():
    """Initialize database on startup."""
    await init_db()
    print("✅ Database initialized")
    print("🚀 AutoFill-GForm Pro is running!")


# Frontend page routes
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


# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "AutoFill-GForm Pro", "version": "1.0.0"}
