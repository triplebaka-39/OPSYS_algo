
import sys
import re

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QMessageBox,
    QHeaderView,
    QAbstractItemView
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from algorithms.page_replacement import (
    fifo,
    lru,
    optimal
)
from module.theme import style_dashboard_button
from module.typography import load_application_fonts
from module.window_utils import (
    center_adaptive_window,
    make_window_adaptive,
    wrap_in_scroll_area,
)


class PageReplacementWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Page Replacement - OS Simulator")
        make_window_adaptive(
            self, preferred_width=950, preferred_height=740, min_width=720, min_height=500
        )

        self.create_ui()
        self.apply_stylesheet()

        self.step_output = None
        self.step_index = 0
        self.step_frame_count = 0

        # Connect buttons
        self.btnSimulate.clicked.connect(self.run_simulation)
        self.btnStartStepByStep.clicked.connect(self.start_step_by_step)
        self.btnNextStep.clicked.connect(self.next_step)
        self.btnClear.clicked.connect(self.clear_simulation)
        self.btnBackToDashboard.clicked.connect(self.close)

    # -----------------------------------
    # CENTER WINDOW
    # -----------------------------------

    def center_window(self):
        center_adaptive_window(self)

    # -----------------------------------
    # CREATE GUI
    # -----------------------------------

    def create_ui(self):

        # Main layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("container")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(24, 20, 24, 11)
        main_layout.setSpacing(15)

        # -----------------------------------
        # HEADER
        # -----------------------------------

        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()

        self.lblTitle = QLabel("Page Replacement")
        self.lblTitle.setObjectName("title")

        self.lblSubtitle = QLabel(
            "Operating Systems Learning Lab"
        )
        self.lblSubtitle.setObjectName("subtitle")

        title_layout.addWidget(self.lblTitle)
        title_layout.addWidget(self.lblSubtitle)

        self.cmbAlgorithm = QComboBox()
        self.cmbAlgorithm.addItems([
            "FIFO",
            "LRU",
            "Optimal"
        ])
        self.cmbAlgorithm.setMinimumWidth(190)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.cmbAlgorithm)

        main_layout.addLayout(header_layout)

        # -----------------------------------
        # INPUT SECTION
        # -----------------------------------

        input_group = QGroupBox("Simulation Configuration")

        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(12)

        # Reference String
        lblReference = QLabel("Page Reference String")

        self.txtReferenceString = QLineEdit()
        self.txtReferenceString.setPlaceholderText(
            "Example: 7, 0, 1, 2, 0, 3, 0, 4, 2, 3"
        )

        # Number of Frames
        lblFrames = QLabel("Number of Frames")

        self.spnFrames = QSpinBox()
        self.spnFrames.setMinimum(1)
        self.spnFrames.setMaximum(20)
        self.spnFrames.setValue(3)

        input_layout.addWidget(lblReference, 0, 0)
        input_layout.addWidget(self.txtReferenceString, 1, 0)

        input_layout.addWidget(lblFrames, 0, 1)
        input_layout.addWidget(self.spnFrames, 1, 1)

        main_layout.addWidget(input_group)

        # -----------------------------------
        # BUTTONS
        # -----------------------------------

        button_layout = QHBoxLayout()

        self.btnSimulate = QPushButton("Run Simulation")
        self.btnSimulate.setObjectName("primaryButton")

        self.btnStartStepByStep = QPushButton("Step-by-Step")
        self.btnStartStepByStep.setObjectName("secondaryButton")

        self.btnNextStep = QPushButton("Next Step")
        self.btnNextStep.setObjectName("secondaryButton")
        self.btnNextStep.setEnabled(False)

        self.btnClear = QPushButton("Clear")
        self.btnClear.setObjectName("secondaryButton")

        self.btnBackToDashboard = QPushButton("Back to Dashboard")
        style_dashboard_button(self.btnBackToDashboard)
        button_layout.addWidget(self.btnSimulate)
        button_layout.addWidget(self.btnStartStepByStep)
        button_layout.addWidget(self.btnNextStep)
        button_layout.addWidget(self.btnClear)

        main_layout.addLayout(button_layout)

        # -----------------------------------
        # RESULTS SECTION
        # -----------------------------------

        results_group = QGroupBox("Simulation Results")

        results_layout = QVBoxLayout(results_group)

        self.lblStepStatus = QLabel("Click Step-by-Step, then Next Step to advance.")
        self.lblStepStatus.setObjectName("statLabel")
        self.lblStepStatus.setWordWrap(True)
        results_layout.addWidget(self.lblStepStatus)

        self.tblResults = QTableWidget()

        self.tblResults.setAlternatingRowColors(True)

        self.tblResults.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tblResults.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tblResults.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.tblResults.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tblResults.verticalHeader().setVisible(False)

        results_layout.addWidget(self.tblResults)

        main_layout.addWidget(results_group, 1)

        # -----------------------------------
        # STATISTICS
        # -----------------------------------

        stats_layout = QHBoxLayout()

        self.lblPageFaults = QLabel("Page Faults: 0")
        self.lblPageHits = QLabel("Page Hits: 0")
        self.lblFaultRate = QLabel("Fault Rate: 0.00%")

        self.lblPageFaults.setObjectName("statLabel")
        self.lblPageHits.setObjectName("statLabel")
        self.lblFaultRate.setObjectName("statLabel")

        stats_layout.addWidget(self.lblPageFaults)
        stats_layout.addStretch()
        stats_layout.addWidget(self.lblPageHits)
        stats_layout.addStretch()
        stats_layout.addWidget(self.lblFaultRate)

        main_layout.addLayout(stats_layout)

        main_layout.addStretch(1)
        main_layout.addWidget(self.btnBackToDashboard)

        scroll = wrap_in_scroll_area(container, self)
        root_layout.addWidget(scroll)

        # Example input
        self.txtReferenceString.setText(
            "7, 0, 1, 2, 0, 3, 0, 4, 2, 3"
        )

    # -----------------------------------
    # STYLESHEET
    # -----------------------------------

    def apply_stylesheet(self):

        self.setStyleSheet("""
            QDialog {
                background-color: #FFF0F3;
                color: #704653;
                font-family: "Nunito";
                font-size: 10pt;
            }

            QWidget {
                font-family: "Nunito";
            }

            QLabel {
                color: #704653;
                background: transparent;
                font-size: 10pt;
            }

            QLabel#title {
                color: #C45B7A;
                font-size: 24pt;
                font-weight: 700;
            }

            QLabel#subtitle {
                color: #A66C7D;
                font-size: 10pt;
            }

            QGroupBox {
                background-color: #FFFAFC;
                color: #C45B7A;
                border: 1px solid #EABAC9;
                border-radius: 10px;
                margin-top: 12px;
                padding: 15px;
                font-weight: 700;
                font-size: 11pt;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }

            QLineEdit, QSpinBox, QComboBox {
                background-color: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 9px;
                min-height: 22px;
                font-size: 10pt;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFAFC;
                color: #704653;
                selection-background-color: #F2A9C0;
                selection-color: #704653;
                outline: 0;
            }

            QComboBox QAbstractItemView::item {
                color: #704653;
                min-height: 28px;
                padding: 5px;
            }

            QLineEdit:focus, QSpinBox:focus,
            QComboBox:focus {
                border: 2px solid #D77D9A;
            }

            QPushButton {
                background-color: #FFDCE6;
                color: #87475D;
                border: 1px solid #F3B5C8;
                border-radius: 9px;
                padding: 11px;
                font-size: 10pt;
                font-weight: 600;
                min-height: 25px;
            }

            QPushButton:hover {
                background-color: #FFC4D6;
            }

            QPushButton:pressed {
                background-color: #F2A9C0;
            }

            QPushButton#primaryButton {
                background-color: #D66F91;
                color: white;
                border: none;
            }

            QPushButton#primaryButton:hover {
                background-color: #C45B7A;
            }

            QTableWidget {
                background-color: #FFFAFC;
                alternate-background-color: #FFF0F4;
                color: #704653;
                gridline-color: #F0C6D3;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                selection-background-color: #F6C5D6;
                selection-color: #704653;
            }

            QHeaderView::section {
                background-color: #F8D4E0;
                color: #784254;
                padding: 10px;
                border: none;
                font-size: 10pt;
                font-weight: 700;
            }

            QLabel#statLabel {
                color: #C45B7A;
                font-size: 10pt;
                font-weight: 700;
            }
        """)

        # Style the popup view directly so native palette colors cannot make
        # the algorithm names disappear against the popup background.
        self.cmbAlgorithm.view().setStyleSheet("""
            QListView {
                background-color: #FFFAFC;
                color: #704653;
                outline: 0;
            }
            QListView::item {
                color: #704653;
                min-height: 28px;
                padding: 5px;
            }
            QListView::item:selected {
                background-color: #F2A9C0;
                color: #704653;
            }
        """)

    # -----------------------------------
    # RUN SIMULATION
    # -----------------------------------

    def run_simulation(self):

        try:
            pages, frame_count, output = self.calculate_output()
            self.display_results(output, frame_count)
            self.reset_step_controls("Full simulation complete.")

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Invalid Input",
                str(error)
            )

    def calculate_output(self):
        reference_text = self.txtReferenceString.text().strip()
        if not reference_text:
            raise ValueError("Please enter a page reference string.")

        # Accept commas or spaces and ignore repeated separators.
        raw_pages = [value for value in re.split(r"[\s,]+", reference_text) if value]
        try:
            pages = [int(page) for page in raw_pages]
        except ValueError:
            raise ValueError("Page references must be whole numbers separated by commas or spaces.")
        if any(page < 0 for page in pages):
            raise ValueError("Page numbers cannot be negative.")

        frame_count = self.spnFrames.value()
        algorithm = self.cmbAlgorithm.currentText()
        algorithms = {"FIFO": fifo, "LRU": lru, "Optimal": optimal}
        output = algorithms[algorithm](pages, frame_count)
        return pages, frame_count, output

    def start_step_by_step(self):
        try:
            _, frame_count, output = self.calculate_output()
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Input", str(error))
            return

        self.step_output = output
        self.step_index = 0
        self.step_frame_count = frame_count
        self.prepare_results_table(frame_count)
        self.set_statistics(0, 0, 0, 0)
        self.lblStepStatus.setText(
            f"Ready: {len(output['results'])} page references. Click Next Step to begin."
        )
        self.btnNextStep.setEnabled(bool(output["results"]))

    def next_step(self):
        if self.step_output is None or self.step_index >= len(self.step_output["results"]):
            self.btnNextStep.setEnabled(False)
            return

        result = self.step_output["results"][self.step_index]
        self.append_step_result(result, self.step_index, self.step_frame_count)
        self.step_index += 1

        shown = self.step_output["results"][:self.step_index]
        faults = sum(step["status"] == "Fault" for step in shown)
        hits = self.step_index - faults
        self.set_statistics(faults, hits, self.step_index, len(self.step_output["results"]))

        explanation = self.describe_frame_change(result, self.step_index)
        if self.step_index == len(self.step_output["results"]):
            self.btnNextStep.setEnabled(False)
            self.lblStepStatus.setText(
                f"{explanation}  Complete: {faults} faults, {hits} hits."
            )
        else:
            self.lblStepStatus.setText(
                f"Step {self.step_index}/{len(self.step_output['results'])}: {explanation}"
            )

    def prepare_results_table(self, frame_count):
        headers = ["Step", "Page"]
        headers.extend(f"Frame {i + 1}" for i in range(frame_count))
        headers.append("Status")
        self.tblResults.clearContents()
        self.tblResults.setColumnCount(len(headers))
        self.tblResults.setHorizontalHeaderLabels(headers)
        self.tblResults.setRowCount(0)

    def append_step_result(self, result, index, frame_count):
        table = self.tblResults
        row = table.rowCount()
        table.insertRow(row)
        values = [index + 1, result["page"]]
        values.extend(frame if frame is not None else "-" for frame in result["frames"])
        values.append(result["status"])

        previous_frames = (
            self.step_output["results"][index - 1]["frames"] if index > 0
            else [None] * frame_count
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if column == len(values) - 1:
                item.setForeground(QColor("#704653"))
            elif 2 <= column < 2 + frame_count and value != previous_frames[column - 2]:
                item.setBackground(QColor("#FFF0F3"))
            table.setItem(row, column, item)
        table.resizeRowsToContents()
        table.scrollToBottom()

    def describe_frame_change(self, result, step_number):
        if result["status"] == "Hit":
            return f"Step {step_number}: page {result['page']} is already in a frame (Hit)."

        previous = (
            self.step_output["results"][step_number - 2]["frames"]
            if step_number > 1 else [None] * self.step_frame_count
        )
        for index, (old_page, new_page) in enumerate(zip(previous, result["frames"]), start=1):
            if old_page != new_page:
                if old_page is None:
                    return f"Step {step_number}: page {new_page} enters empty Frame {index} (Fault)."
                return (
                    f"Step {step_number}: page {old_page} leaves Frame {index}; "
                    f"page {new_page} enters it (Fault)."
                )
        return f"Step {step_number}: page {result['page']} causes a page fault."

    def set_statistics(self, faults, hits, processed, total):
        self.lblPageFaults.setText(f"Page Faults: {faults}")
        self.lblPageHits.setText(f"Page Hits: {hits}")
        rate = faults / processed * 100 if processed else 0
        suffix = f" ({processed}/{total} steps)" if total else ""
        self.lblFaultRate.setText(f"Fault Rate: {rate:.2f}%{suffix}")

    def reset_step_controls(self, status):
        self.step_output = None
        self.step_index = 0
        self.step_frame_count = 0
        self.btnNextStep.setEnabled(False)
        self.lblStepStatus.setText(status)

    # -----------------------------------
    # DISPLAY RESULTS
    # -----------------------------------

    def display_results(self, output, frame_count):

        table = self.tblResults
        results = output["results"]
        self.prepare_results_table(frame_count)
        table.setRowCount(len(results))

        for row, result in enumerate(results):
            values = [row + 1, result["page"]]
            values.extend(frame if frame is not None else "-" for frame in result["frames"])
            values.append(result["status"])
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == len(values) - 1:
                    item.setForeground(QColor("#704653"))

                table.setItem(row, column, item)

        # Statistics
        self.lblPageFaults.setText(f"Page Faults: {output['faults']}")
        self.lblPageHits.setText(f"Page Hits: {output['hits']}")
        self.lblFaultRate.setText(f"Fault Rate: {output['fault_rate']:.2f}%")
        table.resizeRowsToContents()

    # -----------------------------------
    # CLEAR SIMULATION
    # -----------------------------------

    def clear_simulation(self):

        self.reset_step_controls("Cleared. Enter a reference string to begin.")
        self.txtReferenceString.clear()

        self.tblResults.clearContents()
        self.tblResults.setRowCount(0)
        self.tblResults.setColumnCount(0)

        self.lblPageFaults.setText("Page Faults: 0")
        self.lblPageHits.setText("Page Hits: 0")
        self.lblFaultRate.setText("Fault Rate: 0.00%")


# -----------------------------------
# MAIN
# -----------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)
    load_application_fonts(app)

    window = PageReplacementWindow()
    window.show()

    sys.exit(app.exec())
