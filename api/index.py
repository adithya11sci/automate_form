import sys
import os
from pathlib import Path

# Setup paths
base_dir = Path(__file__).resolve().parent.parent
backend_dir = base_dir / "backend"

sys.path.append(str(base_dir))
sys.path.append(str(backend_dir))

# Try to import the app
try:
    from app.main import app
except Exception as e:
    # If import fails, create a placeholder app to report the error
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    import traceback
    
    app = FastAPI()
    err_msg = f"Import Error in api/index.py: {str(e)}\n{traceback.format_exc()}"
    
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        return HTMLResponse(content=f"<h1>API Import Failure</h1><pre>{err_msg}</pre>", status_code=500)
