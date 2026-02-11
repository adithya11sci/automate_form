import motor.motor_asyncio
from beanie import init_beanie
from app.config import MONGODB_URL
from app.models import User, UserProfile, FormHistory, LearnedMapping

# Global flag to prevent multiple initializations
_initialized = False

async def init_db():
    """Initializes the MongoDB connection and Beanie models (Idempotent)."""
    global _initialized
    if _initialized:
        return
        
    print(f"🔄 Connecting to MongoDB...")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
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
        print(f"✅ MongoDB Connected successfully")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        raise e
