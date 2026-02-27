import logging
from aiogram import Bot, Dispatcher
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
dp = Dispatcher(storage=RedisStorage(redis=redis))
scheduler = AsyncIOScheduler(timezone=ZoneInfo("UTC"))
