import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from zoneinfo import ZoneInfo
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
redis = Redis.from_url(settings.REDIS_URL)

if redis is not None:
    logger.info("FSM storage: Redis (%s)", settings.REDIS_URL)
    dp = Dispatcher(storage=RedisStorage(redis=redis))
else:
    logger.warning("FSM storage: MemoryStorage (REDIS_URL is not set)")
    dp = Dispatcher(storage=MemoryStorage())

scheduler = AsyncIOScheduler(timezone=ZoneInfo("UTC"))
