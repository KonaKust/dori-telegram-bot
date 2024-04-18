import json
from loguru import logger

from bot.admin.notifications import notify_admin
from bot.features.timetable.notifications import notify_timetable_subs


async def process_data(client_ip, json_data):
    try:
        if "notify_admin" in json_data:
            await notify_admin(json_data["notify_admin"])

        if "timetable" in json_data:
            await notify_timetable_subs(json_data["timetable"])

        if "factorio" in json_data:
            await notify_admin(json_data["factorio"])

        if "tally" in json_data:
            await notify_admin(json_data["tally"])

        response = b"\x00"
    except Exception as e:
        response = b"\x01"
        logger.error(f"Error processing data from {client_ip}: {e}, data - {json_data}")

    return response
