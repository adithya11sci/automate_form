"""
Application configuration settings.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data' / 'autofill.db'}"

# Ensure data directory exists
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "autofill-gform-pro-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# AI Settings
# Set to "local", "openai", or "grok"
AI_MODE = os.getenv("AI_MODE", "grok")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Grok (via Groq) Settings
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_BASE_URL = "https://api.groq.com/openai/v1"
GROK_MODEL = "llama3-70b-8192"


# Playwright settings
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "100"))

# Frontend
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# CORS
CORS_ORIGINS = ["*"]
