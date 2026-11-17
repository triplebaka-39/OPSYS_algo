"""Load the simulator's bundled typefaces for use across its Qt windows."""

from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


FONT_FAMILY = "Nunito"
FONT_FILES = (
    "Nunito-Regular.ttf",
    "Nunito-SemiBold.ttf",
    "Nunito-Bold.ttf",
)


def load_application_fonts(app: QApplication):
    fonts_directory = (
        Path(__file__).resolve().parent.parent / "fonts" / "Nunito" / "static"
    )
    for filename in FONT_FILES:
        font_path = fonts_directory / filename
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id < 0:
            raise RuntimeError("Unable to load bundled font: %s" % font_path)
        if FONT_FAMILY not in QFontDatabase.applicationFontFamilies(font_id):
            raise RuntimeError("Bundled font has an unexpected family: %s" % font_path)

    app_font = QFont(FONT_FAMILY, 10)
    app_font.setWeight(QFont.Weight.Normal)
    app.setFont(app_font)
