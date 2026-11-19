"""Interactive paging and logical-address translation simulator."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from module.theme import style_dashboard_button
from module.window_utils import (
    center_adaptive_window,
    make_window_adaptive,
    wrap_in_scroll_area,
)


DEFAULT_PROCESS_SIZE = 1700
DEFAULT_PAGE_SIZE = 256
DEFAULT_PHYSICAL_MEMORY_SIZE = 1024


def calculate_page_counts(process_size, page_size, physical_memory_size):
    for label, value in (("Process size", process_size), ("Page size", page_size),
                         ("Physical memory size", physical_memory_size)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{label} must be a whole number.")
    if process_size <= 0:
        raise ValueError("Process size must be greater than zero.")
    if page_size <= 0:
        raise ValueError("Page size must be greater than zero.")
    if physical_memory_size <= 0:
        raise ValueError("Physical memory size must be greater than zero.")

    page_count = (process_size + page_size - 1) // page_size
    frame_count = physical_memory_size // page_size
    unused_memory = physical_memory_size % page_size
    return page_count, frame_count, unused_memory


def translate_logical_address(
    logical_address,
    process_size,
    page_size,
    physical_memory_size,
    page_to_frame,
):
    calculate_page_counts(process_size, page_size, physical_memory_size)
    if not isinstance(logical_address, int) or isinstance(logical_address, bool):
        raise ValueError("Logical address must be a whole number.")
    if not isinstance(page_to_frame, dict):
        raise ValueError("Page table must be a mapping of pages to frames.")
    if logical_address < 0 or logical_address >= process_size:
        raise ValueError(
            "Logical address must be between 0 and %d."
            % (process_size - 1)
        )

    page = logical_address // page_size
    offset = logical_address % page_size
    frame = page_to_frame.get(page)
    if frame is None:
        raise ValueError(
            "Page %d does not have a physical frame assigned yet." % page
        )
    if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0:
        raise ValueError("Page table frame entries must be non-negative whole numbers.")

    physical_address = frame * page_size + offset
    if physical_address >= physical_memory_size:
        raise ValueError("The page's frame is outside physical memory.")
    return page, offset, frame, physical_address


class PagingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paging - OS Simulator")
        make_window_adaptive(
            self, preferred_width=1100, preferred_height=760, min_width=760, min_height=520
        )

        self.page_to_frame = {}
        self.processed_pages = set()
        self.frame_labels = {}
        self.page_count = 0
        self.frame_count = 0
        self.step_index = 0
        self.current_page = None
        self.current_frame = None
        self.simulation_started = False
        self._loading_inputs = False
        self._updating_page_table = False

        self._build_ui()
        self._apply_stylesheet()
        self._connect_signals()
        self._refresh_configuration()

    def center_window(self):
        center_adaptive_window(self)

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        content = QWidget()
        content.setObjectName("pagingContent")
        scroll = wrap_in_scroll_area(content, self)
        outer_layout.addWidget(scroll, 1)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 11)
        content_layout.setSpacing(8)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        self.lblTitle = QLabel("Paging")
        self.lblTitle.setObjectName("title")
        self.lblSubtitle = QLabel(
            "Processes are split into pages and loaded into equal-sized frames. "
            "Select a page row to highlight its frame."
        )
        self.lblSubtitle.setObjectName("subtitle")
        header_layout.addWidget(self.lblTitle)
        header_layout.addWidget(self.lblSubtitle)
        content_layout.addLayout(header_layout)

        workspace_layout = QHBoxLayout()
        workspace_layout.setSpacing(12)

        memory_group = QGroupBox("Memory Visualization")
        memory_layout = QVBoxLayout(memory_group)
        memory_layout.setSpacing(8)

        table_heading = QLabel("Page Table")
        table_heading.setObjectName("sectionHeading")
        memory_layout.addWidget(table_heading)

        self.page_table = QTableWidget()
        self.page_table.setColumnCount(4)
        self.page_table.setHorizontalHeaderLabels(
            ["Page", "Logical Range", "Frame", "Status"]
        )
        self.page_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.page_table.verticalHeader().setVisible(False)
        self.page_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.page_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.page_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.page_table.setMinimumHeight(180)
        self.page_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        memory_layout.addWidget(self.page_table, 3)

        frames_heading = QLabel("Physical Memory Frames")
        frames_heading.setObjectName("sectionHeading")
        memory_layout.addWidget(frames_heading)

        self.frame_scroll = QScrollArea()
        self.frame_scroll.setWidgetResizable(True)
        self.frame_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_grid_widget = QWidget()
        self.frame_grid = QGridLayout(self.frame_grid_widget)
        self.frame_grid.setContentsMargins(2, 2, 2, 2)
        self.frame_grid.setSpacing(8)
        self.frame_scroll.setWidget(self.frame_grid_widget)
        self.frame_scroll.setMinimumHeight(120)
        self.frame_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        memory_layout.addWidget(self.frame_scroll, 2)
        workspace_layout.addWidget(memory_group, 3)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(7)

        config_group = QGroupBox("Configuration")
        config_layout = QGridLayout(config_group)
        config_layout.setHorizontalSpacing(10)
        config_layout.setVerticalSpacing(6)
        self.process_size = self._size_input(1, 16384, DEFAULT_PROCESS_SIZE)
        self.page_size = self._size_input(64, 4096, DEFAULT_PAGE_SIZE)
        self.physical_memory_size = self._size_input(
            1, 16384, DEFAULT_PHYSICAL_MEMORY_SIZE
        )
        for row, (label, field) in enumerate((
            ("Process Size", self.process_size),
            ("Page Size", self.page_size),
            ("Physical Memory Size", self.physical_memory_size),
        )):
            heading = QLabel(label)
            heading.setObjectName("fieldLabel")
            field.setSuffix(" bytes")
            config_layout.addWidget(heading, row, 0)
            config_layout.addWidget(field, row, 1)

        self.lblPageCount = QLabel()
        self.lblFrameCount = QLabel()
        self.lblUnusedMemory = QLabel()
        for label in (
            self.lblPageCount,
            self.lblFrameCount,
            self.lblUnusedMemory,
        ):
            label.setObjectName("statLabel")
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(self.lblPageCount)
        summary_layout.addWidget(self.lblFrameCount)
        summary_layout.addWidget(self.lblUnusedMemory)
        config_layout.addLayout(summary_layout, 3, 0, 1, 2)
        right_layout.addWidget(config_group)

        simulation_group = QGroupBox("Simulation Steps")
        simulation_layout = QVBoxLayout(simulation_group)
        controls_layout = QHBoxLayout()
        self.btnStartSimulation = QPushButton("Start Simulation")
        self.btnStartSimulation.setObjectName("primaryButton")
        self.btnNextStep = QPushButton("Next Page")
        self.btnNextStep.setObjectName("secondaryButton")
        self.btnNextStep.setEnabled(False)
        self.btnReset = QPushButton("Reset")
        self.btnReset.setObjectName("secondaryButton")
        controls_layout.addWidget(self.btnStartSimulation)
        controls_layout.addWidget(self.btnNextStep)
        if self.width() >= 900:
            controls_layout.addWidget(self.btnReset)
            simulation_layout.addLayout(controls_layout)
        else:
            simulation_layout.addLayout(controls_layout)
            simulation_layout.addWidget(self.btnReset)

        self.lblStepExplanation = QLabel(
            "Start the simulation to map pages to available frames."
        )
        self.lblStepExplanation.setObjectName("stepExplanation")
        self.lblStepExplanation.setWordWrap(True)
        simulation_layout.addWidget(self.lblStepExplanation)
        right_layout.addWidget(simulation_group)

        translation_group = QGroupBox("Address Translation")
        translation_layout = QGridLayout(translation_group)
        address_label = QLabel("Logical Address")
        address_label.setObjectName("fieldLabel")
        self.txtLogicalAddress = QLineEdit()
        self.txtLogicalAddress.setPlaceholderText("Enter a byte address")
        self.btnTranslate = QPushButton("Translate Address")
        translation_layout.addWidget(address_label, 0, 0, 1, 2)
        translation_layout.addWidget(self.txtLogicalAddress, 1, 0)
        translation_layout.addWidget(self.btnTranslate, 1, 1)
        self.lblTranslationResult = QLabel(
            "Enter an address to see its page, offset, and physical location."
        )
        self.lblTranslationResult.setObjectName("translationResult")
        self.lblTranslationResult.setWordWrap(True)
        translation_layout.addWidget(self.lblTranslationResult, 2, 0, 1, 2)
        right_layout.addWidget(translation_group)

        self.btnBackToDashboard = QPushButton("Back to Dashboard")
        style_dashboard_button(self.btnBackToDashboard)
        workspace_layout.addWidget(right_panel, 2)
        content_layout.addLayout(workspace_layout, 1)
        outer_layout.addWidget(self.btnBackToDashboard)

    @staticmethod
    def _size_input(minimum, maximum, value):
        field = QSpinBox()
        field.setRange(minimum, maximum)
        field.setValue(value)
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return field

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog,
            QWidget#pagingContent,
            QScrollArea::viewport {
                background-color: #FFF0F3;
                color: #704653;
                font-family: "Nunito";
                font-size: 10pt;
            }

            QWidget {
                font-family: "Nunito";
            }

            QScrollArea {
                background-color: #FFF0F3;
                border: none;
            }

            QAbstractScrollArea,
            QAbstractScrollArea::viewport {
                background-color: #FFFAFC;
            }

            QAbstractScrollArea::corner {
                background-color: #FFDCE6;
            }

            QScrollArea::viewport {
                background-color: #FFF0F3;
            }

            QHeaderView {
                background-color: #FFDCE6;
            }

            QTableCornerButton::section {
                background-color: #FFDCE6;
                border: 1px solid #EABAC9;
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
                color: #704653;
                font-size: 10pt;
            }

            QLabel#fieldLabel,
            QLabel#statLabel,
            QLabel#sectionHeading {
                color: #C45B7A;
                font-size: 10pt;
                font-weight: 700;
            }

            QLabel#helperText {
                color: #704653;
                font-size: 10pt;
            }

            QLabel#stepExplanation,
            QLabel#translationResult {
                color: #704653;
                padding: 2px 0;
                font-size: 9pt;
            }

            QGroupBox {
                background-color: #FFFAFC;
                color: #C45B7A;
                border: 1px solid #EABAC9;
                border-radius: 10px;
                margin-top: 8px;
                padding: 8px;
                font-size: 11pt;
                font-weight: 700;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }

            QGroupBox QWidget {
                background-color: transparent;
            }

            QLineEdit,
            QSpinBox {
                background-color: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 6px;
                min-height: 18px;
                font-size: 10pt;
            }

            QLineEdit:focus,
            QSpinBox:focus {
                border: 2px solid #F2A9C0;
            }

            QSpinBox::up-button,
            QSpinBox::down-button {
                background-color: #FFDCE6;
                border: none;
            }

            QPushButton {
                background-color: #FFDCE6;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 9px;
                padding: 7px 10px;
                min-height: 20px;
                font-size: 10pt;
                font-weight: 600;
            }

            QPushButton:hover,
            QPushButton:pressed {
                background-color: #F2A9C0;
            }

            QPushButton:focus {
                border: 2px solid #C45B7A;
            }

            QPushButton:disabled {
                background-color: #FFF0F3;
                color: #704653;
                border-color: #EABAC9;
            }

            QPushButton#primaryButton {
                background-color: #C45B7A;
                color: #FFFAFC;
                border: none;
            }

            QPushButton#primaryButton:hover,
            QPushButton#primaryButton:pressed {
                background-color: #F2A9C0;
                color: #704653;
            }

            QTableWidget {
                background-color: #FFFAFC;
                alternate-background-color: #FFF0F3;
                color: #704653;
                gridline-color: #EABAC9;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                selection-background-color: #F2A9C0;
                selection-color: #704653;
                font-size: 10pt;
            }

            QTableWidget::viewport {
                background-color: #FFFAFC;
            }

            QTableWidget::item {
                background-color: #FFFAFC;
                color: #704653;
            }

            QTableWidget::item:alternate {
                background-color: #FFF0F3;
            }

            QTableWidget::item:selected {
                background-color: #F2A9C0;
                color: #704653;
            }

            QHeaderView::section {
                background-color: #FFDCE6;
                color: #704653;
                padding: 8px;
                border: 1px solid #EABAC9;
                font-size: 10pt;
                font-weight: 700;
            }

            QScrollBar:vertical,
            QScrollBar:horizontal {
                background-color: #FFF0F3;
                border: none;
            }

            QScrollBar::handle:vertical,
            QScrollBar::handle:horizontal {
                background-color: #F2A9C0;
                border-radius: 5px;
                min-height: 20px;
                min-width: 20px;
            }

            QToolTip {
                background-color: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                font-family: "Nunito";
            }
        """)

    def _connect_signals(self):
        self.process_size.valueChanged.connect(self._configuration_changed)
        self.page_size.valueChanged.connect(self._configuration_changed)
        self.physical_memory_size.valueChanged.connect(self._configuration_changed)
        self.page_table.currentCellChanged.connect(self._page_selected)
        self.btnStartSimulation.clicked.connect(self.start_simulation)
        self.btnNextStep.clicked.connect(self.next_step)
        self.btnReset.clicked.connect(self.reset)
        self.btnTranslate.clicked.connect(self.translate_address)
        self.txtLogicalAddress.returnPressed.connect(self.translate_address)
        self.btnBackToDashboard.clicked.connect(self.close)

    def _configuration_changed(self, _value=None):
        if not self._loading_inputs:
            self._refresh_configuration()

    def _refresh_configuration(self):
        process_size = self.process_size.value()
        page_size = self.page_size.value()
        physical_size = self.physical_memory_size.value()
        self.page_count, self.frame_count, unused = calculate_page_counts(
            process_size, page_size, physical_size
        )
        self.page_to_frame = {page: None for page in range(self.page_count)}
        self.processed_pages.clear()
        self.step_index = 0
        self.current_page = None
        self.current_frame = None
        self.simulation_started = False
        self.btnNextStep.setEnabled(False)

        self.lblPageCount.setText("Pages: %d" % self.page_count)
        self.lblFrameCount.setText("Frames: %d" % self.frame_count)
        self.lblUnusedMemory.setText("Unused memory: %d bytes" % unused)
        self.lblTranslationResult.setText(
            "Enter an address to see its page, offset, and physical location."
        )
        self._populate_page_table()
        self._populate_frames()
        if self.frame_count:
            self.lblStepExplanation.setText(
                "Start the simulation to map pages to available frames."
            )
        else:
            self.lblStepExplanation.setText(
                "No complete frame fits in physical memory. Pages cannot be mapped "
                "until the memory size or page size changes."
            )

    def _populate_page_table(self):
        self._updating_page_table = True
        try:
            self.page_table.setRowCount(self.page_count)
            process_size = self.process_size.value()
            page_size = self.page_size.value()
            for page in range(self.page_count):
                start = page * page_size
                end = min(start + page_size, process_size) - 1
                frame = self.page_to_frame[page]
                if frame is not None:
                    status = "Mapped"
                    frame_text = str(frame)
                elif page in self.processed_pages:
                    status = "No frame"
                    frame_text = "—"
                else:
                    status = "Waiting" if self.simulation_started else "Not started"
                    frame_text = "—"

                values = [
                    str(page),
                    "%d - %d" % (start, end),
                    frame_text,
                    status,
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if page == self.current_page:
                        item.setBackground(QColor("#F2A9C0"))
                    self.page_table.setItem(page, column, item)

            if self.current_page is not None:
                self.page_table.setCurrentCell(self.current_page, 0)
            else:
                self.page_table.setCurrentCell(-1, -1)
        finally:
            self._updating_page_table = False

    def _clear_frame_grid(self):
        while self.frame_grid.count():
            item = self.frame_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.frame_labels.clear()

    def _populate_frames(self):
        self._clear_frame_grid()
        if not self.frame_count:
            message = QLabel("No complete frames fit in physical memory.")
            message.setWordWrap(True)
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.frame_grid.addWidget(message, 0, 0)
            return

        for frame in range(self.frame_count):
            label = QLabel()
            label.setObjectName("memoryFrame")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumSize(86, 58)
            self.frame_grid.addWidget(label, frame // 4, frame % 4)
            self.frame_labels[frame] = label
        self._refresh_frames()

    def _refresh_frames(self):
        assigned_frames = {
            frame: page
            for page, frame in self.page_to_frame.items()
            if frame is not None
        }
        for frame, label in self.frame_labels.items():
            page = assigned_frames.get(frame)
            label.setText(
                "Frame %d\n%s" % (
                    frame,
                    "Page %d" % page if page is not None else "Free",
                )
            )
            current = frame == self.current_frame
            background = (
                "#F2A9C0" if current
                else "#FFDCE6" if page is not None
                else "#FFFAFC"
            )
            border = "#C45B7A" if current else "#EABAC9"
            label.setStyleSheet(
                'background-color: %s; color: #704653; border: 2px solid %s;'
                ' border-radius: 8px; font-family: "Nunito";'
                " font-size: 10pt; font-weight: 600;"
                % (background, border)
            )

    def _page_selected(self, row, _column, _previous_row, _previous_column):
        if self._updating_page_table or row < 0:
            return
        self.current_page = row
        self.current_frame = self.page_to_frame.get(row)
        self._populate_page_table()
        self._refresh_frames()

    def start_simulation(self):
        self.page_to_frame = {page: None for page in range(self.page_count)}
        self.processed_pages.clear()
        self.step_index = 0
        self.current_page = 0 if self.page_count else None
        self.current_frame = 0 if self.frame_count else None
        self.simulation_started = True
        self.btnNextStep.setEnabled(bool(self.page_count))
        self.lblStepExplanation.setText(
            "Ready: Page 0 is selected, and the first free frame is highlighted. "
            "Click Next Step to assign it."
            if self.page_count else "There are no pages to simulate."
        )
        self.lblTranslationResult.setText(
            "Enter an address to see its page, offset, and physical location."
        )
        self._populate_page_table()
        self._refresh_frames()

    def next_step(self):
        if not self.simulation_started or self.step_index >= self.page_count:
            self.btnNextStep.setEnabled(False)
            return

        page = self.step_index
        free_frames = [
            frame for frame in range(self.frame_count)
            if frame not in self.page_to_frame.values()
        ]
        self.processed_pages.add(page)
        self.current_page = page
        if free_frames:
            frame = free_frames[0]
            self.page_to_frame[page] = frame
            self.current_frame = frame
            explanation = (
                "Page %d was loaded into Frame %d. The page table now stores this "
                "mapping for address translation." % (page, frame)
            )
        else:
            self.current_frame = None
            explanation = (
                "Page %d has no free frame, so it remains unallocated. Its logical "
                "addresses cannot be translated yet." % page
            )

        self.step_index += 1
        if self.step_index == self.page_count:
            mapped = sum(frame is not None for frame in self.page_to_frame.values())
            unmapped = self.page_count - mapped
            if free_frames:
                explanation = (
                    "Page %d was loaded into Frame %d. Simulation complete: "
                    "%d page(s) mapped and %d without a frame."
                    % (page, frame, mapped, unmapped)
                )
            else:
                explanation = (
                    "Page %d could not be assigned because no frames remain. "
                    "Simulation complete: %d page(s) mapped and %d without a frame."
                    % (page, mapped, unmapped)
                )
            self.btnNextStep.setEnabled(False)

        self.lblStepExplanation.setText(explanation)
        self._populate_page_table()
        self._refresh_frames()

    def translate_address(self):
        text = self.txtLogicalAddress.text().strip()
        try:
            if not text:
                raise ValueError("Enter a logical address in bytes.")
            try:
                logical_address = int(text)
            except ValueError:
                raise ValueError("Enter a whole-number logical address.")
            page, offset, frame, physical_address = translate_logical_address(
                logical_address,
                self.process_size.value(),
                self.page_size.value(),
                self.physical_memory_size.value(),
                self.page_to_frame,
            )
        except ValueError as error:
            self.lblTranslationResult.setText(str(error))
            return

        self.current_page = page
        self.current_frame = frame
        self._populate_page_table()
        self._refresh_frames()
        self.lblTranslationResult.setText(
            "Logical address %d = Page %d × %d + offset %d. "
            "Page %d is in Frame %d, so the physical address is "
            "%d × %d + %d = %d."
            % (
                logical_address,
                page,
                self.page_size.value(),
                offset,
                page,
                frame,
                frame,
                self.page_size.value(),
                offset,
                physical_address,
            )
        )

    def reset(self):
        self._loading_inputs = True
        self.process_size.setValue(DEFAULT_PROCESS_SIZE)
        self.page_size.setValue(DEFAULT_PAGE_SIZE)
        self.physical_memory_size.setValue(DEFAULT_PHYSICAL_MEMORY_SIZE)
        self.txtLogicalAddress.clear()
        self._loading_inputs = False
        self._refresh_configuration()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from module.typography import load_application_fonts

    load_application_fonts(app)
    window = PagingWindow()
    window.show()
    sys.exit(app.exec())
