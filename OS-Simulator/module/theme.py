"""Shared application palette for simulator widgets without local styling."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QPushButton, QSizePolicy


DASHBOARD_BUTTON_STYLE = """
QPushButton {
    background-color: #FFDCE6;
    color: #87475D;
    border: 1px solid #F3B5C8;
    border-radius: 9px;
    padding: 8px;
    font-family: "Nunito";
    font-size: 10pt;
    font-weight: 600;
    min-height: 0px;
    max-height: 34px;
}
QPushButton:hover { background-color: #FFC4D6; }
QPushButton:pressed { background-color: #F2A9C0; }
QPushButton:focus { border: 1px solid #F3B5C8; }
"""
def apply_application_palette(app: QApplication) -> None:
    palette = QPalette(app.palette())
    colors = {
        QPalette.ColorRole.Window: "#FFF0F3",
        QPalette.ColorRole.WindowText: "#704653",
        QPalette.ColorRole.Base: "#FFFAFC",
        QPalette.ColorRole.AlternateBase: "#FFF0F4",
        QPalette.ColorRole.ToolTipBase: "#FFFAFC",
        QPalette.ColorRole.ToolTipText: "#704653",
        QPalette.ColorRole.Text: "#704653",
        QPalette.ColorRole.Button: "#FFDCE6",
        QPalette.ColorRole.ButtonText: "#704653",
        QPalette.ColorRole.BrightText: "#C45B7A",
        QPalette.ColorRole.Light: "#FFFAFC",
        QPalette.ColorRole.Midlight: "#FFDCE6",
        QPalette.ColorRole.Dark: "#C45B7A",
        QPalette.ColorRole.Mid: "#EABAC9",
        QPalette.ColorRole.Shadow: "#704653",
        QPalette.ColorRole.Highlight: "#F2A9C0",
        QPalette.ColorRole.HighlightedText: "#704653",
        QPalette.ColorRole.Link: "#C45B7A",
        QPalette.ColorRole.LinkVisited: "#87475D",
        QPalette.ColorRole.PlaceholderText: "#A77987",
    }
    for group in (
        QPalette.ColorGroup.Active,
        QPalette.ColorGroup.Inactive,
    ):
        for role, color in colors.items():
            palette.setColor(group, role, QColor(color))

    for role, color in colors.items():
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            role,
            QColor("#FFF0F3") if role in (
                QPalette.ColorRole.Window,
                QPalette.ColorRole.Base,
                QPalette.ColorRole.AlternateBase,
                QPalette.ColorRole.Button,
                QPalette.ColorRole.Light,
                QPalette.ColorRole.Midlight,
            ) else QColor(color),
        )
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            role,
            QColor("#A77987"),
        )
    app.setPalette(palette)


def style_dashboard_button(button: QPushButton) -> None:
    button.setObjectName("dashboardButton")
    button.setStyleSheet(DASHBOARD_BUTTON_STYLE)
    button.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Fixed,
    )
