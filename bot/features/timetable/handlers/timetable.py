from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from contextlib import suppress


from bot.features.timetable.keyboards import timetable_menu as kb
from bot.features.timetable.convert import convert_timetable
import database.timetable as timetable_db  # Импортируем класс (ещё не изучено)

from bot.features.timetable.notifications import redis

db = timetable_db.Timetable()  # создаём алиас на метод класса?
router = Router()


@router.callback_query(F.data == "timetable")
async def timetable_menu_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Расписание занятий в Таймырском колледже", reply_markup=kb.sub_kb
    )
    await callback.answer()


@router.callback_query(F.data == "convert_timetable")
async def convert_timetable_callback_handler(callback: CallbackQuery) -> None:
    await convert_timetable()
    await callback.answer()


@router.callback_query(F.data == "get_timetable")
async def send_timetable_callback_handler(callback: CallbackQuery) -> None:
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.message.answer_document(redis.get("pdf"))
    await callback.message.answer(
        "Возвращайся в главное меню ⛔︎", reply_markup=kb.menu_kb
    )
    await callback.answer()


@router.callback_query(F.data == "subscribe")
async def subscribe_callback_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    if not await db.subscribed_user(user_id):
        await db.toggle_user(user_id)
        await callback.message.edit_text(
            "Вы успешно подписаны!", reply_markup=kb.get_kb
        )
    else:
        await callback.answer("Вы уже подписаны на обновления расписания :)")

    await callback.answer()


@router.callback_query(F.data == "unsubscribe")
async def unsubscribe_callback_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    if await db.subscribed_user(user_id):
        await db.toggle_user(user_id, toggle=0)
        await callback.message.edit_text(
            "Уведомления отключены!", reply_markup=kb.menu_kb
        )
    else:
        await callback.answer("Вы ничего не изменили, хахах :)")

    await callback.answer()
