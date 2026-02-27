import asyncio
from datetime import datetime, timedelta
from aiogram import Router, types
from aiogram.types import FSInputFile, InputMediaPhoto

from data.states import StoryState
from data.story_content import (
    text_10_for_pro,
    text_11_for_pro,
    text_12_for_pro,
    final_goodbye_text_up,
)
from loader import scheduler, dp, bot
from utils.common import my_send_text_and_photos
from utils.keyboards import get_reviews_kb

router = Router()


def calculate_run_date():
    """Считает время: сейчас + 3 часа, но строго в интервале 10:00 - 21:00"""
    run_date = datetime.now() + timedelta(hours=3)

    if run_date.hour >= 21:
        run_date = (run_date + timedelta(days=1)).replace(hour=10, minute=0, second=0)

    elif run_date.hour < 10:
        run_date = run_date.replace(hour=10, minute=0, second=0)

    return run_date


async def send_pro_reviews_auto(chat_id: int):
    photo = FSInputFile("data/photos/text_final.jpg")
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=final_goodbye_text_up,
        parse_mode="HTML",
    )


async def send_pro_text_12(chat_id: int):
    state_context = dp.fsm.resolve_context(bot=bot, chat_id=chat_id, user_id=chat_id)
    await state_context.set_state(StoryState.final_stage)

    await my_send_text_and_photos(
        chat_id=chat_id,
        text=text_12_for_pro,
        photos=["data/photos/text_12_pro_1.jpg"],
        post_id="12pro",
    )

    # run_date = calculate_run_date()

    scheduler.add_job(
        send_pro_reviews_auto,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=16),  # run_date,
        args=[chat_id],
    )


async def send_pro_text_11(chat_id: int):
    await my_send_text_and_photos(
        chat_id=chat_id,
        text=text_11_for_pro,
        photos=["data/photos/text_11_pro_1.jpg"],
        post_id="11pro",
    )

    scheduler.add_job(
        send_pro_text_12,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=6),
        args=[chat_id],
    )


async def send_pro_text_10(chat_id: int):
    # Обновляем стейт
    state_context = dp.fsm.resolve_context(bot=bot, chat_id=chat_id, user_id=chat_id)
    await state_context.set_state(StoryState.final_stage)

    await my_send_text_and_photos(
        chat_id=chat_id,
        text=text_10_for_pro,
        photos=["data/photos/text_10_pro_1.jpg"],
        post_id="10pro",
    )

    scheduler.add_job(
        send_pro_text_11,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=6),
        args=[chat_id],
    )
