import motor.motor_asyncio
from beanie import init_beanie
from app.config import MONGODB_URL
from app.models import User, UserProfile, FormHistory, LearnedMapping

async def init_db():
    """Initializes the MongoDB connection and Beanie models."""
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
    print(f"✅ MongoDB Connected: {MONGODB_URL}")
