import shutil
import subprocess
from pathlib import Path
from loguru import logger

from pdf2image import convert_from_path


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
            # logger.debug(f"Saving {locate}/{i}.png")
        return 1
    except Exception as e:
        shutil.move(swap, png)
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
    global swap
    global png

    module = Path("/home", "dori", "bot", "features", "timetable")
    new_doc = Path("/home", "nas_share", "01_Расписание", "00_Завтра").glob("*.docx")
    www_png = Path("/home", "nas_web")

    doc = Path(module, "Расписание.docx")
    pdf = Path(module, "Расписание.pdf")
    png = Path(www_png, "00_today/")
    swap = Path(module, "SWAP/")


async def convert_timetable():
    await paths()
    for file in new_doc:
        shutil.copy(str(file), str(doc))
        file.unlink()
    if doc.is_file():
        shutil.rmtree(swap)
        shutil.move(png, swap)
        png.mkdir()
        res_pdf = await convert_doc(doc, module)
        if res_pdf == 1:
            res_png = await convert_pdf(pdf, png)
            if res_png == 1:
                logger.info("Timetable converted automatically")
                return 1
            else:
                return res_png
        else:
            return res_pdf
    else:
        return 0