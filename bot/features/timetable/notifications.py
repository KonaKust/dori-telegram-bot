import datetime
from contextlib import suppress

import database.timetable as timetable_db
import redis
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import FSInputFile
from bot.admin.notifications import notify_admin
from loguru import logger
from runners.launch import bot

timetable_db = timetable_db.Timetable()
redis = redis.Redis(host="localhost", port=6379, decode_responses=True)


async def notify_timetable_subs():
    users = await timetable_db.id_of_subscribers()
    current_date_pdf = f"{datetime.date.today()}.pdf"
    try:
        converted_pdf = FSInputFile(
            f"/srv/dori/bot/features/timetable/{current_date_pdf}"
        )

        if not (redis.get("saved_pdf") == current_date_pdf):
            old_pdf_id = redis.get("new_pdf")
            redis.set(name="old_pdf", value=old_pdf_id)
            redis.set(name="saved_pdf", value=current_date_pdf)
        new_pdf = await bot.send_document(list(users)[0], FSInputFile(converted_pdf))
        new_pdf_id = new_pdf.document.file_id
        redis.set(name="new_pdf", value=new_pdf_id)
        with suppress(TelegramForbiddenError):
            for user in list(users)[1:]:
                await bot.send_document(user, new_pdf_id)
    except Exception as e:
        logger.error(f"Save pdf error: {e}")
        await notify_admin(
            f"""
        Ошибка при сохранении pdf!

        {e}
        """
        )
