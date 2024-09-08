import logging
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from app.config import config

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None

    def connect(self):
        self.client = AsyncIOMotorClient(config.MONGO_URL)
        self.engine = AIOEngine(client=self.client, database=config.MONGO_DB_NAME)
        logger.info("Connected to MongoDB")

    def close(self):
        self.client.close()
        logger.info("Disconnected from MongoDB")


mongodb = MongoDB()
