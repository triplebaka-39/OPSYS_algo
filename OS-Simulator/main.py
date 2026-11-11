
import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMainWindow,
)

from ui_main_window import Ui_MainWindow


class ModuleWindow(QDialog):
    """Temporary window for an OS simulator module."""

    def __init__(self, module_name):
        super().__init__()

        self.setWindowTitle(module_name)
        self.resize(650, 450)

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("OS Simulator")
        self.resize(950, 650)

        # Keep references so opened windows remain available.
        self.module_windows = []

        # Connect each dashboard button to its module.
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

    def open_module(self, module_name):
        window = ModuleWindow(module_name)

        # Retain the window while it is open.
        self.module_windows.append(window)
        window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
