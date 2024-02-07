from loguru import logger
from bot.admin.handlers import admin_menu, user_management, send_as_bot, help_to_users
from runners.launch import dp_main as dp


def enable() -> None:  # Регестрация Роутеров
    dp.include_routers(
        admin_menu.router,
        user_management.router,
        send_as_bot.router,
        help_to_users.router,
    )
    logger.info("Admin routers included")


enable()
