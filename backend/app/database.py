import motor.motor_asyncio
from beanie import init_beanie
from app.config import MONGODB_URL
from app.models import User, UserProfile, FormHistory, LearnedMapping
import asyncio

# Global initialized flag
_initialized = False

async def init_db():
    """Simple, robust MongoDB initialization for Vercel."""
    global _initialized
    if _initialized:
        return
        
    try:
        # Standard Motor connection - works best on Vercel
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        database = client.get_default_database()
        
        await init_beanie(
            database=database,
            document_models=[
                User,
                UserProfile,
                FormHistory,
                LearnedMapping
            ]
        )
        _initialized = True
        print(f"✅ DB Connected to: {database.name}")
    except Exception as e:
        print(f"❌ DB Error: {e}")
        # Raising the error so the middleware catches it and shows it in diagnostic mode
        raise Exception(f"MongoDB Connection Failed: {str(e)}. Please check your MONGODB_URI and IP Whitelist.")
