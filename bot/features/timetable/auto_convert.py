import datetime
import re
import shutil
import subprocess
from pathlib import Path

from loguru import logger
from pdf2image import convert_from_path
from pypdf import PdfReader

# Need install "poppler" and libreoffice


async def convert_doc(bad_doc, locate):
    try:
        subprocess.call(  # use libreoffice to convert
            [
                "libreoffice",
                "lowriter",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                locate,
                bad_doc,
            ]
        )
        bad_doc.unlink()  # delete used doc
        return 1
    except Exception as e:
        logger.error(f"Converting docx error: {e}")
        return f"""
        Ошибка при конвертации расписания в pdf!

        {e}
        """


async def convert_pdf(bad_pdf, locate):
    try:
        images = convert_from_path(f"{bad_pdf}", 310)  # use pdf2image to convert
        for i, image in enumerate(images):  # save result for all pages
            image.save(f"{locate}/{i}.png", "PNG")
        return 1
    except Exception as e:
        logger.error(f"Coverting pdf error: {e}")
        return f"""
        Ошибка при конвертации расписания в png!

        {e}
        """


async def paths():
    global module
    global new_doc
    global doc
    global pdf
    global png
    global old_pdf

    current_date_doc = f"{datetime.date.today() + datetime.timedelta(days=1)}.docx"
    current_date_pdf = f"{datetime.date.today() + datetime.timedelta(days=1)}.pdf"

    module = Path("/srv", "dori", "bot", "features", "timetable")
    new_doc = Path("/home", "nas_share", "01_Расписание", "00_Завтра").glob("*.docx")
    www_png = Path("/home", "nas_web")

    doc = Path(module, current_date_doc)
    pdf = Path(module, current_date_pdf)
    png = Path(www_png, "00_today/")
    old_pdf = Path(module).glob("*.pdf")


def extract_timetable_date(text):
    # Используем регулярное выражение для извлечения даты из текста расписания
    date_pattern = r"\s+(\d{2}\.\d{2}\.\d{4})"
    match = re.search(date_pattern, text)
    if match:
        # Если найдено соответствие, возвращаем дату
        return match.group(1)
    return None


def get_pdf_date(pdf_path):
    # Получаем текст из первой страницы PDF
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text()

    # Извлекаем дату из текста расписания
    return extract_timetable_date(text)


async def convert_timetable():
    await paths()
    for file in new_doc:
        shutil.copy(str(file), str(doc))
        file.unlink()
    if doc.is_file():
        old_pdf.unlink()
        res_pdf = await convert_doc(doc, module)
        if res_pdf == 1:
            converted_date = get_pdf_date(pdf)
            extracted_date_pdf = Path(module, converted_date)
            shutil.move(pdf, extracted_date_pdf)
            res_png = await convert_pdf(pdf, png)
            if res_png == 1:
                logger.info("Timetable converted automatically")
                return 1, converted_date
            else:
                return res_png, None
        else:
            return res_pdf, None
    else:
        return 0, None
