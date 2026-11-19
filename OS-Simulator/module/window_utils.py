"""Window utility functions for adaptive responsive sizing, scrolling, and application icons."""

import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QScrollArea, QFrame, QVBoxLayout, QWidget


def get_base_path() -> Path:
    """Return base path whether running from source or PyInstaller bundle."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_app_icon() -> QIcon:
    """Load application icon from bundle or source directory."""
    base = get_base_path()
    ico_path = base / "app_icon.ico"
    png_path = base / "app_icon.png"
    if ico_path.exists():
        return QIcon(str(ico_path))
    if png_path.exists():
        return QIcon(str(png_path))
    return QIcon()


def make_window_adaptive(
    window,
    preferred_width: int = 1000,
    preferred_height: int = 750,
    min_width: int = 650,
    min_height: int = 480,
):
    """
    Enables minimize and maximize window buttons, clamps window size
    responsively to the current screen's available geometry (leaving safe margins),
    and centers the window.
    """
    # Enable minimize and maximize controls on dialogs
    window.setWindowFlags(
        window.windowFlags()
        | Qt.WindowType.WindowMinimizeButtonHint
        | Qt.WindowType.WindowMaximizeButtonHint
    )

    icon = get_app_icon()
    if not icon.isNull():
        window.setWindowIcon(icon)

    screen = window.screen() or QGuiApplication.primaryScreen()
    if screen:
        avail = screen.availableGeometry()
        margin_w = 36
        margin_h = 56

        # Clamp preferred size to available screen area
        target_w = min(preferred_width, max(min_width, avail.width() - margin_w))
        target_h = min(preferred_height, max(min_height, avail.height() - margin_h))

        calc_min_w = min(min_width, target_w)
        calc_min_h = min(min_height, target_h)

        window.setMinimumSize(calc_min_w, calc_min_h)
        window.resize(target_w, target_h)

        # Center in available screen geometry
        frame = window.frameGeometry()
        frame.moveCenter(avail.center())
        window.move(frame.topLeft())
    else:
        window.setMinimumSize(min_width, min_height)
        window.resize(preferred_width, preferred_height)


def center_adaptive_window(window):
    """Center window within current screen available geometry."""
    screen = window.screen() or QGuiApplication.primaryScreen()
    if screen:
        avail = screen.availableGeometry()
        frame = window.frameGeometry()
        frame.moveCenter(avail.center())
        window.move(frame.topLeft())


def wrap_in_scroll_area(content_widget: QWidget, parent: QWidget = None, background_color: str = "#FFF0F3") -> QScrollArea:
    """
    Wraps a content widget in a seamless, borderless QScrollArea so that
    if the screen is smaller than the required content, the user can smoothly scroll.
    """
    scroll = QScrollArea(parent)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setStyleSheet(f"""
        QScrollArea {{
            background-color: {background_color};
            border: none;
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: {background_color};
        }}
        QScrollBar:vertical {{
            background: #FFF0F4;
            width: 10px;
            margin: 0px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: #F2A9C0;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #C45B7A;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: #FFF0F4;
            height: 10px;
            margin: 0px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: #F2A9C0;
            min-width: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #C45B7A;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """)
    scroll.setWidget(content_widget)
    return scroll
