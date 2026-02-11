import motor.motor_asyncio
from beanie import init_beanie
from app.config import MONGODB_URL
from app.models import User, UserProfile, FormHistory, LearnedMapping

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
            serverSelectionTimeoutMS=5000
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
        print("✅ DB Connected")
    except Exception as e:
        print(f"❌ DB Error: {e}")
        # We don't raise here so we can still see the /api/ping test
        pass
