
import asyncio
from business_backend.database.connection import get_engine
from business_backend.database.models import Base
from business_backend.database.models.computer import Computer  # Ensure model is verified

async def init_tables():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_tables())
