from contextlib import suppress

import database.admin as admin_db
import database.user as user_db
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, TelegramObject
from bot.admin.filters.is_admin import IsAdmin
from runners.launch import bot

users_db = user_db.Users()
admin_db = admin_db.Admin()
router = Router()


class AdminState(StatesGroup):
    say_them = State()
    get_meassange = State()


@router.callback_query(F.data == "send_all", IsAdmin())
@router.message(Command("sendall"), IsAdmin())
async def cmd_notify_all(object: TelegramObject, state: FSMContext) -> None:
    if isinstance(object, CallbackQuery):
        await object.message.edit_text("Пиши, Я всех ознакомлю :)")
    else:
        await object.answer("Пиши, Я всех ознакомлю :)")
    await state.set_state(AdminState.say_them)


@router.message(AdminState.say_them)
async def send_message_to_all(object: TelegramObject, state: FSMContext) -> None:
    users = await users_db.id_of_users()
    for user in list(users):
        with suppress(TelegramForbiddenError):
            await bot.copy_message(
                user,
                object.from_user.id,
                object.message_id,
            )
    await state.clear()


@router.callback_query(F.data == "send_admins", IsAdmin())
@router.message(Command("sendadmins"), IsAdmin())
async def cmd_notify_admins(object: TelegramObject, state: FSMContext) -> None:
    if isinstance(object, CallbackQuery):
        await object.message.edit_text("Передам слово в слово 🫡")
    else:
        await object.answer("Передам слово в слово 🫡")
    await state.set_state(AdminState.get_meassange)


@router.message(AdminState.get_meassange)
async def send_message_to_aadmins(object: TelegramObject, state: FSMContext) -> None:
    admins = await admin_db.id_of_admins()
    for admin in list(admins):
        with suppress(TelegramForbiddenError):
            await bot.copy_message(
                admin,
                object.from_user.id,
                object.message_id,
            )
    await state.clear()
