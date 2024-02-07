from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from loguru import logger
from bot.admin.filters.is_admin import IsAdmin
from bot.admin.keyboards import admin_menu

router = Router()


@router.message(F.text.lower() == "/.", IsAdmin())
@router.message(F.text.lower() == "/admin", IsAdmin())  # Открыть админку
async def open_admin_menu_handler(message: Message) -> None:
    await message.delete()
    await message.answer("*Панель администратора:*", reply_markup=admin_menu.main_kb)


@router.callback_query(F.data == "admin_menu", IsAdmin())
async def to_admin_menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "*Панель администратора:*", reply_markup=admin_menu.main_kb
    )
    await callback.answer()


@router.callback_query(F.data == "bot_settings", IsAdmin())
async def bot_settings_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Здесь ничего нет, хахах", reply_markup=admin_menu.one_bt
    )
    await callback.answer()


@router.callback_query(F.data == "help_for_admin", IsAdmin())
async def help_for_admin_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "*тебе никто не поможет* ⚰️", reply_markup=admin_menu.sad_kb
    )
    await callback.answer()
