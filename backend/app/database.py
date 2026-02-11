import motor.motor_asyncio
from beanie import init_beanie
from app.config import MONGODB_URL
from app.models import User, UserProfile, FormHistory, LearnedMapping
import asyncio

# Global client and initialized flag
_initialized = False
_client = None

async def init_db():
    """Initializes the MongoDB connection and Beanie models (Serverless optimized)."""
    global _initialized, _client
    
    if _initialized:
        return
        
    print(f"🔄 Connecting to MongoDB...")
    try:
        if _client is None:
            # For serverless, we want to reuse the client if possible
            # but also ensure we don't have multiple loops
            _client = motor.motor_asyncio.AsyncIOMotorClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                # Explicitly use the current event loop
                io_loop=asyncio.get_event_loop()
            )
            
        database = _client.get_default_database()
        
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
        print(f"✅ MongoDB Connected: {MONGODB_URL.split('@')[-1]}") # Log without credentials
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {str(e)}")
        # Don't re-raise if we want the app to stay alive for non-DB routes
        # But for this app, most of it needs DB
        raise e
