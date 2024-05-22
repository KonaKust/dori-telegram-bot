import shutil
from datetime import date
from pathlib import Path

from loguru import logger
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.admin.filters.is_admin import IsAdmin
from bot.admin.keyboards import admin_menu

router = Router()


class DoriState(StatesGroup):
    saving_link = State()


@router.message(F.text.lower() == "/.", IsAdmin())
@router.message(F.text.lower() == "/admin", IsAdmin())  # Открыть админку
async def open_admin_menu_handler(message: Message) -> None:
    await message.delete()
    await message.answer("*Панель администратора:*", reply_markup=admin_menu.main_kb)


@router.callback_query(F.data == "admin_menu", IsAdmin())
async def to_admin_menu_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "*Панель администратора:*", reply_markup=admin_menu.main_kb
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "bot_settings", IsAdmin())
async def bot_settings_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Здесь ничего нет, хахах", reply_markup=admin_menu.one_bt
    )
    await callback.answer()


@router.callback_query(F.data == "save_link", IsAdmin())
async def help_for_admin_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        """*тебе никто не поможет* ⚰️ 
Отправь мне ссылку, я ее съем :)""",
        reply_markup=admin_menu.sad_kb,
    )
    await state.set_state(DoriState.saving_link)
    await callback.answer()


@router.message(DoriState.saving_link)
async def save_link_in_NAS(message: Message, state: FSMContext) -> None:
    note = Path("/home", "nas_share", "links.txt")
    link = f"""--- {date.today()}
{message.text}
--- --- ---

"""
    try:
        if note.is_file():
            with open(note, "a") as file:
                file.write(link)
        else:
            with open(note, "w+") as file:
                file.write(link)
        await message.answer("Ссылка успешно сохрнена!") 
    except expression as e:
        await message.answer(f"{e}")

    await state.clear()
