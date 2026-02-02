from asyncio import sleep

from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from aiogram.fsm.state import StatesGroup, State


from database import init_db, add_user_with_schedule
from aiogram import Router, types, F
from aiogram.fsm.storage.memory import MemoryStorage

from config import (
    BOT_TOKEN,
    HOST,
    PORT,
    BASE_URL,
    WEBHOOK_PATH, CHAT_ID_TO_CHECK
)
from loader import bot, dp, logger, scheduler
from scheduler_task import check_and_send_daily



storage = MemoryStorage()
router = Router()
dp.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = f"{BASE_URL}/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")
    scheduler.add_job(check_and_send_daily, "interval", minutes=4)
    scheduler.start()

    yield

    await bot.delete_webhook()
    logger.info("Webhook deleted")



app = FastAPI(lifespan=lifespan)

class Survey(StatesGroup):
    waiting_for_subscription = State()
    waiting_for_extra_materials = State()
    waiting_for_stage = State()



@app.post(f"{WEBHOOK_PATH}")
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


@router.message(Command("start"))
async def answer_start(message: types.Message, command: CommandObject, state: FSMContext):
    try:
        await state.set_state(Survey.waiting_for_subscription)
        payload = str(command.args).strip()
        add_user_with_schedule(message.from_user.id, payload)
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text=f"1. Подписаться",
            url="https://t.me/yellow_submarin04")
        )
        builder.row(types.InlineKeyboardButton(
            text="2. Я подписался!",
            callback_data="check_subscription")
        )
        text = f"""
        Привет. Бла-бла. Получите гайд бесплатно за подписку на Telegram-канал Школы.
        """
        await message.answer(
            text,
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"error in answer_start: {e}", exc_info=True)


@router.callback_query(Survey.waiting_for_subscription, F.data == "check_subscription")
async def verify_subscription(callback: types.CallbackQuery, state: FSMContext):
    try:
        user_channel_status = await bot.get_chat_member(
            chat_id=CHAT_ID_TO_CHECK,
            user_id=callback.from_user.id
        )
        if user_channel_status.status in ("member", "administrator", "creator"):
            await state.set_state(Survey.waiting_for_extra_materials)
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(
                text="Да",
                callback_data="yes_for_extra_materials")
            )
            builder.row(types.InlineKeyboardButton(
                text="Нет",
                callback_data="no_for_extra_materials")
            )
            new_text = (
                "Ура! Подписка подтверждена.\n"
                "Вот ваша ссылка на пакет: [ССЫЛКА]\n\n"
                "У нас есть еще полезные материалы для психологов. Хотели бы получить больше?"
            )
            await sleep(0.4)
            await callback.message.edit_text(
                text=new_text,
                reply_markup=builder.as_markup())
        else:
            await callback.answer(
                "Вы еще не подписались на канал!",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        await callback.answer("Произошла ошибка. Убедитесь, что бот добавлен в канал.")


@router.callback_query(Survey.waiting_for_extra_materials, F.data == "no_for_extra_materials")
async def say_no_for_extra_materials(callback: types.CallbackQuery, state: FSMContext):
    text = ("Тогда прощаемся. Рады были поделиться пакетом. "
            "Если передумаете — выбор можно изменить.")
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Я передумал, хочу материалы! ⚡️",
        callback_data="yes_for_extra_materials")
    )
    await sleep(0.4)
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(Survey.waiting_for_extra_materials, F.data == "yes_for_extra_materials")
async def say_no_for_extra_materials(callback: types.CallbackQuery, state: FSMContext):
    await sleep(0.4)
    await callback.message.edit_text(
        text="Круто, что ты с нами дальше. Вот что еще у нас есть."
    )
    await state.set_state(Survey.waiting_for_stage)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Я начинающий в теме РПП",
        callback_data="beginner")
    )
    builder.row(types.InlineKeyboardButton(
        text="Я практикую в теме РПП более года",
        callback_data="knowledgeable")
    )
    builder.row(types.InlineKeyboardButton(
        text="Я практикую в теме РПП более 3х лет",
        callback_data="expert")
    )
    await callback.message.answer(
        text="На какой стадии находитесь?",
        reply_markup=builder.as_markup()
    )


@router.callback_query(Survey.waiting_for_stage, F.data == "beginner")
async def talk_to_beginner(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Ничего страшного мы всё расскажем.")

@router.callback_query(Survey.waiting_for_stage, F.data == "knowledgeable")
async def talk_to_knowledgeable(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Супер! Ты разбираешься в теме.")


@router.callback_query(Survey.waiting_for_stage, F.data == "expert")
async def talk_to_expert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Отлично! Ты уже эксперт!")


if __name__ == "__main__":
    import uvicorn
    init_db()

    uvicorn.run(
        "main:app", host=HOST, port=PORT, log_level="info"
    )

