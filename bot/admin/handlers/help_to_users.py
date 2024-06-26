from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.admin.filters.is_admin import IsAdmin

from aiogram import flags

from runners.launch import bot
import database.admin as admin_db


admin_db = admin_db.Admin()
router = Router()


class UsersState(StatesGroup):
    asking_for_help = State()


@router.callback_query(F.data == "say_to_admin")
# @flags.rate_limit(100)
async def asking_admin(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Пиши, Я предам им")
    await state.set_state(UsersState.asking_for_help)


@router.message(UsersState.asking_for_help)
async def forvard_message_to_admins(message: Message, state: FSMContext) -> None:
    admins = await admin_db.id_of_admins()
    for admin in list(admins):
        await bot.send_message(admin, f"*{message.from_user.id}* просит о помощи:")
        await bot.forward_message(
            admin, message.from_user.id, message.message_id, disable_notification=True
        )
        await state.clear()

    await message.answer("Сообщение доставлено администраторам!")
