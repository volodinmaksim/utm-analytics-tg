from datetime import datetime, timezone

from database import SessionLocal, User
from loader import bot, logger


async def check_and_send_daily():
    session = SessionLocal()
    now = datetime.now(timezone.utc)
    try:
        users_to_notify = session.query(User).filter(
            User.sent_delayed == False,
            User.scheduled_time <= now
        ).all()

        for user in users_to_notify:
            try:
                text = """Привет! Это твое персонализированное сообщение через сутки."""
                await bot.send_message(user.tg_id, text)
                user.sent_delayed = True
                session.commit()
                logger.info(f"Sent scheduled msg to {user.tg_id}")
            except Exception as e:
                logger.error(f"Failed to send to {user.tg_id}: {e}")
    finally:
        session.close()
