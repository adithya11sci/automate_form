import sys
import os
from pathlib import Path

# Add the project root and backend directory to sys.path
# This ensures that 'app' can be found regardless of how Vercel invokes the function
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))
sys.path.append(str(base_dir / "backend"))

from app.main import app

# Vercel requires the app object to be available at the module level
# We import it here so Vercel can find it
