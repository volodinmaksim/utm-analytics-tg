from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager


from config import settings
from aiogram.fsm.storage.memory import MemoryStorage

from db.db_helper import db_helper
from db.models import Base
from loader import bot, dp, logger, scheduler
from routers import (
    start_router,
    onboarding_router,
    pro_router,
    survey_router,
    novice_router,
    pro_continued_router,
    novice_continued_router,
)

storage = MemoryStorage()


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = settings.BASE_URL + "/webhook"
    dp.include_router(start_router)
    dp.include_router(onboarding_router)
    dp.include_router(novice_router)
    dp.include_router(survey_router)
    dp.include_router(pro_router)
    dp.include_router(pro_continued_router)
    dp.include_router(novice_continued_router)
    scheduler.start()
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.SECRET_TG_KEY,
        drop_pending_updates=True,
    )
    logger.info(f"Webhook set to: {webhook_url}")

    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    scheduler.shutdown()
    await bot.delete_webhook()
    logger.info("Webhook deleted")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def handle_telegram_webhook(request: Request):
    try:
        update_data = await request.json()
        from aiogram.types import Update

        update = Update.model_validate(update_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}", exc_info=True)
        return JSONResponse({"status": "error"}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, log_level="info")
