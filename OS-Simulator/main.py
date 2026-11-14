
import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMainWindow,
)

from module.bankers import BankersWindow
from ui_main_window import Ui_MainWindow


# ==========================================
# MODULE WINDOW
# ==========================================

class ModuleWindow(QDialog):

    def __init__(self, module_name):
        super().__init__()

        self.setWindowTitle(module_name)

        # Lock module window size
        self.setFixedSize(650, 450)

        # Center module window
        self.center_window()

        # Layout
        layout = QVBoxLayout(self)

        title = QLabel(module_name)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )
        layout.addWidget(title)

        description = QLabel(
            "This module is under development.\n"
            "Its inputs and simulation results will appear here."
        )

        description.setWordWrap(True)
        layout.addWidget(description)

        close_button = QPushButton("Back to Dashboard")
        close_button.clicked.connect(self.close)

        layout.addWidget(close_button)

    def center_window(self):
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()

        window.moveCenter(screen.center())
        self.move(window.topLeft())


# ==========================================
# MAIN DASHBOARD
# ==========================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Load Qt Designer interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("OS Simulator")

        # Lock dashboard size
        self.setFixedSize(480, 500)

        # Center dashboard
        self.center_window()

        # Store references to opened module windows
        self.module_windows = []

        # Connect dashboard buttons
        self.ui.btnCpuScheduling.clicked.connect(
            lambda: self.open_module("CPU Scheduling")
        )

        self.ui.btnBankers.clicked.connect(
            lambda: self.open_module("Banker's Algorithm")
        )

        self.ui.btnPaging.clicked.connect(
            lambda: self.open_module("Paging")
        )

        self.ui.btnPageReplacement.clicked.connect(
            lambda: self.open_module("Page Replacement")
        )

        self.ui.btnSegmentation.clicked.connect(
            lambda: self.open_module("Segmentation")
        )

        self.ui.btnFragmentation.clicked.connect(
            lambda: self.open_module("Fragmentation")
        )

        self.ui.btnDiskScheduling.clicked.connect(
            lambda: self.open_module("Disk Scheduling")
        )

        self.ui.btnMultiprogramming.clicked.connect(
            lambda: self.open_module("Multiprogramming")
        )

    def center_window(self):
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()

        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def open_module(self, module_name):

        if module_name == "Banker's Algorithm":
            window = BankersWindow(self)
        else:
            window = ModuleWindow(module_name)

        # Retain reference while window is open
        self.module_windows.append(window)

        # Remove reference when window closes
        window.finished.connect(
            lambda: self.module_windows.remove(window)
            if window in self.module_windows else None
        )

        window.show()


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setFont(QFont("Inter"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
