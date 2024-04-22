import datetime
from contextlib import suppress
from pathlib import Path

import database.timetable as timetable_db
import redis
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import FSInputFile
from bot.admin.notifications import notify_admin
from loguru import logger
from runners.launch import bot

timetable_db = timetable_db.Timetable()
redis = redis.Redis(host="localhost", port=6379, decode_responses=True)

if not redis.get("saved_pdf"):
    redis.set(name="old_pdf", value="")
    redis.set(name="new_pdf", value="")
    redis.set(name="saved_pdf", value="")
    logger.warning('Redis key "saved_pdf" was None!')

if not redis.get("old_pdf"):
    redis.set(name="old_pdf", value=(redis.get("new_pdf")))
    logger.warning('Redis key "old_pdf" was None!')


async def notify_timetable_subs(date):
    users = await timetable_db.id_of_subscribers()
    today = datetime.date.today().strftime("%d.%m.%Y")
    converted_pdf = Path("/srv", "dori", "bot", "features", "timetable", f"{date}.pdf")
    try:
        pdf = await bot.send_document(list(users)[0], FSInputFile(converted_pdf))
        pdf_id = pdf.document.file_id
        if date > today:
            if redis.get("saved_pdf") != today:
                redis.set(name="old_pdf", value=(redis.get("saved_pdf")))
                redis.set(name="saved_pdf", value=today)
            redis.set(name="new_pdf", value=pdf_id)
        else:
            redis.set(name="old_pdf", value=pdf_id)
        with suppress(TelegramForbiddenError):
            for user in list(users)[1:]:
                await bot.send_document(user, pdf_id)
    except Exception as e:
        logger.error(f"Save pdf error: {e}")
        await notify_admin(
            f"""
        Ошибка при сохранении pdf!

        {e}
        """
        )
