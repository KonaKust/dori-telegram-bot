import os

import database.admin as admin_db  # Импортируем класс (ещё не изучено)
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from bot.admin.filters.is_admin import IsAdmin
from bot.admin.keyboards import user_managment as kb
from loguru import logger
from aiogram.types import FSInputFile

global db
router = Router()
db = admin_db.Admin()


@router.callback_query(F.data == "user_managment", IsAdmin())
async def user_managment_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "*Управление пользователями*", reply_markup=kb.menu_kb
    )
    await callback.answer()


@router.callback_query(F.data == "users_list")
async def user_list_handler(callback: CallbackQuery):
    logger.info("Users_list command handled!")
    users = await db.list_of_all_users()
    response_text = ""
    for user in users:
        if user["username"] != None:
            response_text += (
                f"#{user ['id']} - {user['username']} (ID: {user['user_id']})\n"
            )
        else:
            response_text += f"#{user ['id']} - {user['first_name']} {user['last_name']} (ID: {user['user_id']})\n"
    with open("UsersList.md", "w+") as f:
        f.write(response_text)
    await callback.message.delete()
    file = FSInputFile("UsersList.md")
    await callback.message.answer_document(file)
    await callback.message.answer("Что-нибудь ещё?", reply_markup=kb.admins_kb)
    await callback.answer()
    os.remove("UsersList.md")
    logger.info("Users list sended")


@router.callback_query(F.data == "admins_list")
async def admins_list_handler(callback: CallbackQuery):
    logger.info("Admins_list command handled!")
    users = await db.list_of_admins()
    response_text = "Список Администраторов:\n"
    for user in users:
        if user["username"] != None:
            response_text += (
                f"#{user ['id']} - {user['username']} (ID: {user['user_id']})\n"
            )
        else:
            response_text += f"#{user ['id']} \- {user['first_name']} {user['last_name']} (ID: {user['user_id']})\n"
    await callback.message.edit_text(response_text, reply_markup=kb.users_kb)
    await callback.answer()
    logger.info("Users list sended")


@router.callback_query(F.data == "users_statistic")
async def count_users_handler(callback: CallbackQuery):
    logger.info("Count_users command handled")
    counts = await db.count_users()
    response_text = f"""
    *Информация о колличестве пользователей*
        Всего: {counts ['total_users']}
        Susbscribe Time: {counts ['subscribed_users']}
        Админов: {counts ['admin_users']}
    """
    await callback.message.edit_text(response_text, reply_markup=kb.stats_kb)
    await callback.answer()
    logger.info("Counts of users sended")
