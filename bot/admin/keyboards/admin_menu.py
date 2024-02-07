from aiogram.types import (
    InlineKeyboardButton as IButton,
    InlineKeyboardMarkup as IMarkup,
)


main_kb = [
    [
        IButton(text="Пользователи", callback_data="user_managment"),
        IButton(text="Настройка бота", callback_data="bot_settings"),
    ],
    [IButton(text="Сконвертировать расписание", callback_data="convert_timetable")],
    [
        IButton(text="Помощь", callback_data="help_for_admin"),
        IButton(text="Выход", callback_data="exit_from_menu"),
    ],
    [IButton(text="Сообщение пользователям", callback_data="send_all")],
    [IButton(text="Сообщение Администраторам", callback_data="send_admins")],
]

one_bt = [
    [
        IButton(text="Меню", callback_data="admin_menu"),
    ]
]


sad_kb = [
    [
        IButton(text="Х Смириться Х", callback_data="admin_menu"),
    ]
]


main_kb = IMarkup(inline_keyboard=main_kb)
one_bt = IMarkup(inline_keyboard=one_bt)
sad_kb = IMarkup(inline_keyboard=sad_kb)
