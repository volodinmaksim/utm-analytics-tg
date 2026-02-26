from data.states import StoryState
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.story_content import text_after_15_minutes


async def send_15min_survey(chat_id: int, bot: Bot, state: FSMContext):
    current_state = await state.get_state()
    if current_state != StoryState.waiting_15min_pause:
        return

    await state.set_state(StoryState.waiting_for_extra_materials)

    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="extra_yes")
    builder.button(text="Нет", callback_data="extra_no")
    builder.adjust(2)

    await bot.send_message(
        chat_id, text_after_15_minutes, reply_markup=builder.as_markup()
    )
