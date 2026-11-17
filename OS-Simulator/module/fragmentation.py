"""Interactive memory-fragmentation simulator."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


DEFAULT_BLOCKS = (100, 300, 200)
DEFAULT_PROCESSES = (("P1", 70), ("P2", 180), ("P3", 180), ("P4", 150))
MAX_INPUT_ROWS = 6
MAX_MEMORY_SIZE = 16384


class FragmentationWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fragmentation - OS Simulator")
        self.setFixedSize(1060, 820)
        self._center_window()

        self.block_rows = []
        self.process_rows = []
        self.memory_segments = []
        self.process_status = []
        self.process_status_details = []
        self.process_step = 0
        self.current_process = None
        self.current_block = None
        self.simulation_started = False
        self._loading_inputs = False

        self._build_ui()
        self._apply_stylesheet()
        self._connect_signals()
        self._configuration_changed()

    def _center_window(self):
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 8, 12, 8)
        root_layout.setSpacing(8)

        content = QWidget()
        content.setObjectName("fragmentationContent")
        root_layout.addWidget(content, 1)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        self.lblTitle = QLabel("Fragmentation")
        self.lblTitle.setObjectName("title")
        self.lblIntroduction = QLabel(
            "Internal fragmentation is unused space inside an allocated block. "
            "External fragmentation is free space split across separate regions."
        )
        self.lblIntroduction.setObjectName("subtitle")
        self.lblIntroduction.setWordWrap(True)
        header_layout.addWidget(self.lblTitle)
        header_layout.addWidget(self.lblIntroduction)
        content_layout.addLayout(header_layout)

        columns = QHBoxLayout()
        columns.setSpacing(12)
        content_layout.addLayout(columns, 1)

        left_column = QVBoxLayout()
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setSpacing(7)
        left_stretch, right_stretch = (
            (1, 1) if self.width() < 900 else (3, 2)
        )
        columns.addLayout(left_column, left_stretch)

        memory_group = QGroupBox("Memory Allocation")
        memory_layout = QVBoxLayout(memory_group)
        memory_layout.setSpacing(8)
        self.lblMemoryHint = QLabel(
            "Each block is a separate contiguous memory region."
        )
        self.lblMemoryHint.setObjectName("helperText")
        memory_layout.addWidget(self.lblMemoryHint)

        self.memory_visual_layout = QVBoxLayout()
        self.memory_visual_layout.setContentsMargins(0, 0, 0, 0)
        self.memory_visual_layout.setSpacing(8)
        memory_layout.addLayout(self.memory_visual_layout, 1)

        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(6)
        for text, object_name in (
            ("Allocated", "allocatedLegend"),
            ("Free", "freeLegend"),
            ("Internal waste", "internalLegend"),
        ):
            legend = QLabel(text)
            legend.setObjectName(object_name)
            legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
            legend_layout.addWidget(legend)
        memory_layout.addLayout(legend_layout)
        left_column.addWidget(memory_group, 3)

        self.lblStepExplanation = QLabel(
            "Choose a mode and method, then start the simulation."
        )
        self.lblStepExplanation.setObjectName("stepExplanation")
        self.lblStepExplanation.setWordWrap(True)
        left_column.addWidget(self.lblStepExplanation)

        analysis_group = QGroupBox("Fragmentation Analysis")
        analysis_layout = QGridLayout(analysis_group)
        analysis_layout.setHorizontalSpacing(12)
        analysis_layout.setVerticalSpacing(4)
        self.lblTotalMemory = self._metric_label()
        self.lblAllocatedMemory = self._metric_label()
        self.lblFreeMemory = self._metric_label()
        self.lblInternalFragmentation = self._metric_label()
        self.lblExternalFragmentation = self._metric_label()
        self.lblLargestFreeRegion = self._metric_label()
        for row, labels in enumerate((
            (self.lblTotalMemory, self.lblAllocatedMemory),
            (self.lblFreeMemory, self.lblInternalFragmentation),
            (self.lblExternalFragmentation, self.lblLargestFreeRegion),
        )):
            for column, label in enumerate(labels):
                analysis_layout.addWidget(label, row, column)
        self.lblAnalysisExplanation = QLabel()
        self.lblAnalysisExplanation.setObjectName("helperText")
        self.lblAnalysisExplanation.setWordWrap(True)
        analysis_layout.addWidget(self.lblAnalysisExplanation, 3, 0, 1, 2)
        left_column.addWidget(analysis_group, 1)

        right_panel = QWidget()
        right_panel.setObjectName("controlsPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        columns.addWidget(right_panel, right_stretch)

        self.memory_table = self._create_input_table(
            ("Block", "Size", "Status", "Remove")
        )
        memory_config_group = QGroupBox("Memory Blocks")
        memory_config_layout = QVBoxLayout(memory_config_group)
        memory_config_layout.setSpacing(4)
        memory_config_layout.addWidget(self.memory_table)
        self.btnAddBlock = QPushButton("Add Memory Block")
        self.btnAddBlock.setObjectName("compactButton")
        self.btnAddBlock.setMinimumHeight(24)
        memory_config_layout.addWidget(self.btnAddBlock)
        right_layout.addWidget(memory_config_group)

        self.process_table = self._create_input_table(
            ("Process", "Size", "Status", "Remove")
        )
        process_config_group = QGroupBox("Processes")
        process_config_layout = QVBoxLayout(process_config_group)
        process_config_layout.setSpacing(4)
        process_config_layout.addWidget(self.process_table)
        self.btnAddProcess = QPushButton("Add Process")
        self.btnAddProcess.setObjectName("compactButton")
        self.btnAddProcess.setMinimumHeight(24)
        process_config_layout.addWidget(self.btnAddProcess)
        right_layout.addWidget(process_config_group)

        allocation_group = QGroupBox("Allocation")
        allocation_layout = QGridLayout(allocation_group)
        allocation_layout.setHorizontalSpacing(7)
        allocation_layout.setVerticalSpacing(4)

        mode_label = QLabel("Partition mode")
        mode_label.setObjectName("fieldLabel")
        self.cmbMode = QComboBox()
        self.cmbMode.addItems(("Fixed Partitions", "Variable Partitions"))
        method_label = QLabel("Placement method")
        method_label.setObjectName("fieldLabel")
        self.cmbMethod = QComboBox()
        self.cmbMethod.addItems(("First Fit", "Best Fit", "Worst Fit"))
        allocation_layout.addWidget(mode_label, 0, 0)
        allocation_layout.addWidget(self.cmbMode, 0, 1)
        allocation_layout.addWidget(method_label, 1, 0)
        allocation_layout.addWidget(self.cmbMethod, 1, 1)

        self.btnStartSimulation = QPushButton("Start Simulation")
        self.btnStartSimulation.setObjectName("primaryButton")
        self.btnNextStep = QPushButton("Next Step")
        self.btnNextStep.setObjectName("secondaryButton")
        self.btnNextStep.setEnabled(False)
        self.btnReset = QPushButton("Reset")
        self.btnReset.setObjectName("secondaryButton")
        self.btnStartSimulation.setMinimumHeight(30)
        self.btnNextStep.setMinimumHeight(30)
        self.btnReset.setMinimumHeight(30)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        button_layout.addWidget(self.btnStartSimulation)
        button_layout.addWidget(self.btnNextStep)
        if self.width() >= 900:
            button_layout.addWidget(self.btnReset)
            allocation_layout.addLayout(button_layout, 2, 0, 1, 2)
        else:
            allocation_layout.addLayout(button_layout, 2, 0, 1, 2)
            allocation_layout.addWidget(self.btnReset, 3, 0, 1, 2)
        right_layout.addWidget(allocation_group)

        self.btnBackToDashboard = QPushButton("Back to Dashboard")
        self.btnBackToDashboard.setObjectName("secondaryButton")
        self.btnBackToDashboard.setMinimumHeight(38)
        self.btnBackToDashboard.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        right_layout.addStretch(1)
        right_layout.addWidget(self.btnBackToDashboard)

        for size in DEFAULT_BLOCKS:
            self._add_memory_block(size, refresh=False)
        for name, size in DEFAULT_PROCESSES:
            self._add_process(name, size, refresh=False)

    @staticmethod
    def _metric_label():
        label = QLabel()
        label.setObjectName("statLabel")
        return label

    @staticmethod
    def _create_input_table(headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.verticalHeader().setDefaultSectionSize(30)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.setColumnWidth(3, 64)
        return table

    def _add_memory_block(self, size=100, refresh=True):
        if len(self.block_rows) >= MAX_INPUT_ROWS:
            return
        row = self.memory_table.rowCount()
        self.memory_table.insertRow(row)

        block_item = QTableWidgetItem()
        block_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.memory_table.setItem(row, 0, block_item)

        size_input = self._size_input(size)
        size_input.valueChanged.connect(self._configuration_changed)
        self.memory_table.setCellWidget(row, 1, size_input)

        status = QLabel("Free")
        status.setObjectName("tableStatus")
        status.setWordWrap(True)
        self.memory_table.setCellWidget(row, 2, status)

        remove_button = self._remove_button("memory block")
        remove_button.clicked.connect(
            lambda _checked=False, target=remove_button:
                self._remove_memory_block(target)
        )
        self.memory_table.setCellWidget(row, 3, remove_button)
        self.block_rows.append({
            "size": size_input,
            "status": status,
            "remove": remove_button,
        })
        self._refresh_input_tables()
        if refresh and not self._loading_inputs:
            self._configuration_changed()

    def _add_process(self, name=None, size=50, refresh=True):
        if len(self.process_rows) >= MAX_INPUT_ROWS:
            return
        row = self.process_table.rowCount()
        self.process_table.insertRow(row)

        name_input = QLineEdit(name or "P%d" % (row + 1))
        name_input.setMaxLength(12)
        name_input.setMinimumWidth(0)
        name_input.setFixedHeight(26)
        name_input.textChanged.connect(self._configuration_changed)
        self.process_table.setCellWidget(row, 0, name_input)

        size_input = self._size_input(size)
        size_input.valueChanged.connect(self._configuration_changed)
        self.process_table.setCellWidget(row, 1, size_input)

        status = QLabel("Ready")
        status.setObjectName("tableStatus")
        status.setWordWrap(True)
        self.process_table.setCellWidget(row, 2, status)

        remove_button = self._remove_button("process")
        remove_button.clicked.connect(
            lambda _checked=False, target=remove_button:
                self._remove_process(target)
        )
        self.process_table.setCellWidget(row, 3, remove_button)
        self.process_rows.append({
            "name": name_input,
            "size": size_input,
            "status": status,
            "remove": remove_button,
        })
        self._refresh_input_tables()
        if refresh and not self._loading_inputs:
            self._configuration_changed()

    @staticmethod
    def _size_input(value):
        field = QSpinBox()
        field.setRange(1, MAX_MEMORY_SIZE)
        field.setValue(value)
        field.setSuffix(" B")
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        field.setMinimumWidth(0)
        field.setFixedHeight(26)
        return field

    @staticmethod
    def _remove_button(item_name):
        button = QPushButton("Remove")
        button.setObjectName("rowRemoveButton")
        button.setAccessibleName("Remove " + item_name)
        button.setToolTip("Remove this " + item_name)
        button.setFixedHeight(24)
        return button

    def _refresh_input_tables(self):
        for index, row in enumerate(self.block_rows):
            self.memory_table.item(index, 0).setText("B%d" % (index + 1))
            row["remove"].setEnabled(len(self.block_rows) > 1)
            self.memory_table.setRowHeight(index, 28)
        for index, row in enumerate(self.process_rows):
            self.process_table.setRowHeight(index, 28)
            row["remove"].setEnabled(len(self.process_rows) > 1)
        self._fit_table_height(self.memory_table)
        self._fit_table_height(self.process_table)
        self.btnAddBlock.setEnabled(len(self.block_rows) < MAX_INPUT_ROWS)
        self.btnAddProcess.setEnabled(len(self.process_rows) < MAX_INPUT_ROWS)

    @staticmethod
    def _fit_table_height(table):
        visible_rows = min(table.rowCount(), 4)
        table.setFixedHeight(
            table.horizontalHeader().height() + 2 + visible_rows * 28
        )

    def _remove_memory_block(self, button):
        if len(self.block_rows) <= 1:
            return
        for index, row in enumerate(self.block_rows):
            if row["remove"] is button:
                self.block_rows.pop(index)
                self.memory_table.removeRow(index)
                break
        self._refresh_input_tables()
        self._configuration_changed()

    def _remove_process(self, button):
        if len(self.process_rows) <= 1:
            return
        for index, row in enumerate(self.process_rows):
            if row["remove"] is button:
                self.process_rows.pop(index)
                self.process_table.removeRow(index)
                break
        self._refresh_input_tables()
        self._configuration_changed()

    def _connect_signals(self):
        self.btnAddBlock.clicked.connect(
            lambda: self._add_memory_block()
        )
        self.btnAddProcess.clicked.connect(
            lambda: self._add_process()
        )
        self.cmbMode.currentIndexChanged.connect(self._configuration_changed)
        self.cmbMethod.currentIndexChanged.connect(self._configuration_changed)
        self.btnStartSimulation.clicked.connect(self.start_simulation)
        self.btnNextStep.clicked.connect(self.next_step)
        self.btnReset.clicked.connect(self.reset)
        self.btnBackToDashboard.clicked.connect(self.close)

    def _read_memory_sizes(self):
        return [row["size"].value() for row in self.block_rows]

    def _read_processes(self):
        processes = []
        for index, row in enumerate(self.process_rows):
            name = row["name"].text().strip() or "P%d" % (index + 1)
            processes.append({
                "name": name,
                "size": row["size"].value(),
            })
        return processes

    def _configuration_changed(self, _value=None):
        if self._loading_inputs:
            return
        self._reset_simulation_state()
        self._refresh_all()
        self.lblStepExplanation.setText(
            "Inputs updated. Start the simulation to allocate the processes."
        )

    def _reset_simulation_state(self):
        self.memory_segments = [
            [{"kind": "free", "size": size, "process": None}]
            for size in self._read_memory_sizes()
        ]
        self.process_status = ["Ready"] * len(self.process_rows)
        self.process_status_details = ["Waiting for allocation"] * len(self.process_rows)
        self.process_step = 0
        self.current_process = None
        self.current_block = None
        self.simulation_started = False
        self.btnNextStep.setEnabled(False)

    def _refresh_all(self):
        self._refresh_input_tables()
        self._update_table_status()
        self._render_memory()
        self._update_analysis()

    def _update_table_status(self):
        processes = self._read_processes()
        for block_index, segments in enumerate(self.memory_segments):
            allocated = [
                segment for segment in segments
                if segment["kind"] == "allocated"
            ]
            internal = sum(
                segment["size"] for segment in segments
                if segment["kind"] == "internal"
            )
            free = sum(
                segment["size"] for segment in segments
                if segment["kind"] == "free"
            )
            names = [
                processes[segment["process"]]["name"]
                for segment in allocated
            ]
            parts = names[:]
            if internal:
                parts.append("Internal %d B" % internal)
            if free:
                parts.append("%d B free" % free)
            self.block_rows[block_index]["status"].setText(
                ", ".join(parts) if parts else "Free"
            )
            self.block_rows[block_index]["status"].setToolTip(
                ", ".join(parts) if parts else "Entire block is available"
            )

        for index, row in enumerate(self.process_rows):
            status = self.process_status[index] if index < len(self.process_status) else "Ready"
            row["status"].setText(status)
            detail = (
                self.process_status_details[index]
                if index < len(self.process_status_details) else status
            )
            row["status"].setToolTip(detail)

        self.memory_table.clearSelection()
        self.process_table.clearSelection()
        if self.current_block is not None:
            self.memory_table.selectRow(self.current_block)
        if self.current_process is not None:
            self.process_table.selectRow(self.current_process)

    def _render_memory(self):
        while self.memory_visual_layout.count():
            item = self.memory_visual_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        block_sizes = self._read_memory_sizes()
        processes = self._read_processes()
        for block_index, (block_size, segments) in enumerate(
            zip(block_sizes, self.memory_segments)
        ):
            row = QFrame()
            row.setObjectName(
                "memoryRegionCurrent"
                if block_index == self.current_block else "memoryRegion"
            )
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(7, 5, 7, 5)
            row_layout.setSpacing(9)
            row.setMinimumHeight(64)

            title = QLabel("B%d  |  %d B" % (block_index + 1, block_size))
            title.setObjectName("blockLabel")
            title.setMinimumWidth(84)
            row_layout.addWidget(title)

            bar = QFrame()
            bar.setObjectName("memoryBar")
            bar.setMinimumHeight(56)
            bar_layout = QHBoxLayout(bar)
            bar_layout.setContentsMargins(2, 2, 2, 2)
            bar_layout.setSpacing(2)
            for segment in segments:
                kind = segment["kind"]
                size = segment["size"]
                process_index = segment["process"]
                process_name = (
                    processes[process_index]["name"]
                    if process_index is not None else ""
                )
                fraction = size / block_size if block_size else 0
                if kind == "allocated":
                    text = (
                        "%s\n%d B" % (process_name, size)
                        if fraction >= 0.18 else process_name
                    )
                    tooltip = "%s: %d B allocated" % (process_name, size)
                    background = (
                        "#F2A9C0"
                        if process_index == self.current_process else "#C45B7A"
                    )
                    foreground = (
                        "#704653"
                        if process_index == self.current_process else "#FFFAFC"
                    )
                    border = "#C45B7A"
                elif kind == "internal":
                    text = (
                        "Internal\n%d B" % size if fraction >= 0.18 else "I"
                    )
                    tooltip = "%d B internal fragmentation" % size
                    background = "#F2A9C0"
                    foreground = "#704653"
                    border = "#C45B7A"
                else:
                    text = "Free\n%d B" % size if fraction >= 0.18 else "F"
                    tooltip = "%d B free" % size
                    background = "#FFFAFC"
                    foreground = "#704653"
                    border = "#EABAC9"

                segment_label = QLabel(text)
                segment_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                segment_label.setMinimumWidth(0)
                segment_label.setToolTip(tooltip)
                segment_label.setStyleSheet(
                    "background-color: %s; color: %s; border: 1px solid %s;"
                    " border-radius: 4px; padding: 1px; font-size: 9pt;"
                    " font-weight: 700;"
                    % (background, foreground, border)
                )
                bar_layout.addWidget(segment_label, max(1, size))

            row_layout.addWidget(bar, 1)
            self.memory_visual_layout.addWidget(row, 1)

    def _memory_metrics(self):
        total = sum(self._read_memory_sizes())
        allocated = 0
        internal = 0
        free_regions = []
        for segments in self.memory_segments:
            for segment in segments:
                if segment["kind"] == "allocated":
                    allocated += segment["size"]
                elif segment["kind"] == "internal":
                    internal += segment["size"]
                elif segment["kind"] == "free":
                    free_regions.append(segment["size"])
        free = sum(free_regions)
        largest = max(free_regions, default=0)
        external = max(0, free - largest)
        return total, allocated, free, internal, external, largest

    @staticmethod
    def _bytes(value):
        return "%s B" % format(value, ",")

    def _update_analysis(self):
        total, allocated, free, internal, external, largest = (
            self._memory_metrics()
        )
        self.lblTotalMemory.setText("Total memory: " + self._bytes(total))
        self.lblAllocatedMemory.setText(
            "Allocated memory: " + self._bytes(allocated)
        )
        self.lblFreeMemory.setText("Remaining free: " + self._bytes(free))
        self.lblInternalFragmentation.setText(
            "Internal fragmentation: " + self._bytes(internal)
        )
        self.lblExternalFragmentation.setText(
            "External fragmentation: " + self._bytes(external)
        )
        self.lblLargestFreeRegion.setText(
            "Largest free region: " + self._bytes(largest)
        )

        if self.cmbMode.currentIndex() == 0:
            self.lblAnalysisExplanation.setText(
                "Internal waste is the unused part of allocated partitions. "
                "External fragmentation is free memory outside the largest "
                "unallocated partition."
            )
        else:
            self.lblAnalysisExplanation.setText(
                "Variable partitions avoid internal waste. External fragmentation "
                "is free memory outside the largest contiguous region."
            )

    def _select_candidate(self, candidates):
        method = self.cmbMethod.currentText()
        if method == "Best Fit":
            return min(candidates, key=lambda item: item[2])
        if method == "Worst Fit":
            return max(candidates, key=lambda item: item[2])
        return candidates[0]

    def start_simulation(self):
        self._reset_simulation_state()
        self.simulation_started = True
        self.btnNextStep.setEnabled(bool(self.process_rows))
        self.lblStepExplanation.setText(
            "Simulation started. Select Next Step to allocate the first process."
        )
        self._refresh_all()

    def next_step(self):
        if not self.simulation_started or self.process_step >= len(self.process_rows):
            self.btnNextStep.setEnabled(False)
            return

        processes = self._read_processes()
        process_index = self.process_step
        process = processes[process_index]
        process_name = process["name"]
        process_size = process["size"]
        self.current_process = process_index
        self.current_block = None

        candidates = []
        fixed_partitions = self.cmbMode.currentIndex() == 0
        for block_index, segments in enumerate(self.memory_segments):
            for segment_index, segment in enumerate(segments):
                if segment["kind"] == "free" and segment["size"] >= process_size:
                    if fixed_partitions and (
                        len(segments) != 1 or segment_index != 0
                    ):
                        continue
                    candidates.append(
                        (block_index, segment_index, segment["size"])
                    )

        if candidates:
            block_index, segment_index, region_size = self._select_candidate(
                candidates
            )
            self.current_block = block_index
            if fixed_partitions:
                unused = region_size - process_size
                new_segments = [{
                    "kind": "allocated",
                    "size": process_size,
                    "process": process_index,
                }]
                if unused:
                    new_segments.append({
                        "kind": "internal",
                        "size": unused,
                        "process": process_index,
                    })
                self.memory_segments[block_index] = new_segments
                self.process_status[process_index] = "B%d" % (block_index + 1)
                self.process_status_details[process_index] = (
                    "Allocated to Block %d" % (block_index + 1)
                )
                if unused:
                    explanation = (
                        "%s (%s) was placed in Block %d (%s). %s inside the "
                        "partition is internal fragmentation."
                        % (
                            process_name,
                            self._bytes(process_size),
                            block_index + 1,
                            self._bytes(region_size),
                            self._bytes(unused),
                        )
                    )
                else:
                    explanation = (
                        "%s (%s) exactly fills Block %d. No internal "
                        "fragmentation was created."
                        % (
                            process_name,
                            self._bytes(process_size),
                            block_index + 1,
                        )
                    )
            else:
                segments = self.memory_segments[block_index]
                unused = region_size - process_size
                replacement = [{
                    "kind": "allocated",
                    "size": process_size,
                    "process": process_index,
                }]
                if unused:
                    replacement.append({
                        "kind": "free",
                        "size": unused,
                        "process": None,
                    })
                segments[segment_index:segment_index + 1] = replacement
                self.process_status[process_index] = "B%d" % (block_index + 1)
                self.process_status_details[process_index] = (
                    "Allocated to Block %d" % (block_index + 1)
                )
                explanation = (
                    "%s (%s) was placed in Block %d. %s remains free in that "
                    "region."
                    % (
                        process_name,
                        self._bytes(process_size),
                        block_index + 1,
                        self._bytes(unused),
                    )
                    if unused else
                    "%s (%s) exactly fills its region in Block %d."
                    % (
                        process_name,
                        self._bytes(process_size),
                        block_index + 1,
                    )
                )
        else:
            total, _allocated, free, _internal, _external, largest = (
                self._memory_metrics()
            )
            free_candidates = [
                (block_index, segment_index, segment["size"])
                for block_index, segments in enumerate(self.memory_segments)
                for segment_index, segment in enumerate(segments)
                if segment["kind"] == "free"
            ]
            largest_region = max(free_candidates, key=lambda item: item[2], default=None)
            if largest_region is not None:
                self.current_block = largest_region[0]

            if free >= process_size and largest < process_size:
                self.process_status[process_index] = "External frag."
                self.process_status_details[process_index] = (
                    "External fragmentation: free memory is split across regions."
                )
                explanation = (
                    "%s (%s) could not fit: %s is free, but the largest region "
                    "is %s. The separated free regions demonstrate external "
                    "fragmentation."
                    % (
                        process_name,
                        self._bytes(process_size),
                        self._bytes(free),
                        self._bytes(largest),
                    )
                )
            else:
                self.process_status[process_index] = "Not allocated"
                if fixed_partitions:
                    explanation = (
                        "%s (%s) could not fit because only %s is free in the "
                        "remaining partitions."
                        % (
                            process_name,
                            self._bytes(process_size),
                            self._bytes(free),
                        )
                    )
                else:
                    explanation = (
                        "%s (%s) could not be allocated because only %s is "
                        "free in total."
                        % (
                            process_name,
                            self._bytes(process_size),
                            self._bytes(free),
                        )
                    )
                self.process_status_details[process_index] = explanation

        self.process_step += 1
        if self.process_step >= len(self.process_rows):
            self.btnNextStep.setEnabled(False)
        self.lblStepExplanation.setText(explanation)
        self._refresh_all()

    def reset(self):
        self._loading_inputs = True
        self.memory_table.setRowCount(0)
        self.process_table.setRowCount(0)
        self.block_rows.clear()
        self.process_rows.clear()
        for size in DEFAULT_BLOCKS:
            self._add_memory_block(size, refresh=False)
        for name, size in DEFAULT_PROCESSES:
            self._add_process(name, size, refresh=False)
        self.cmbMode.setCurrentIndex(0)
        self.cmbMethod.setCurrentIndex(0)
        self._loading_inputs = False
        self._configuration_changed()

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog,
            QWidget#fragmentationContent {
                background-color: #FFF0F3;
                color: #704653;
                font-family: "Nunito";
                font-size: 10pt;
            }

            QWidget {
                font-family: "Nunito";
            }

            QLabel {
                background-color: transparent;
                color: #704653;
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
            QLabel#blockLabel {
                color: #C45B7A;
                font-weight: 700;
            }

            QLabel#statLabel {
                font-size: 10pt;
            }

            QLabel#helperText,
            QLabel#stepExplanation {
                color: #704653;
                font-size: 10pt;
            }

            QLabel#stepExplanation {
                background-color: #FFDCE6;
                border-radius: 6px;
                padding: 6px;
                font-weight: 600;
            }

            QGroupBox {
                background-color: #FFFAFC;
                color: #C45B7A;
                border: 1px solid #EABAC9;
                border-radius: 10px;
                margin-top: 7px;
                padding: 7px;
                font-size: 11pt;
                font-weight: 700;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }

            QLineEdit,
            QSpinBox,
            QComboBox {
                background-color: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 2px;
                min-height: 16px;
                font-size: 10pt;
            }

            QLineEdit:focus,
            QSpinBox:focus,
            QComboBox:focus {
                border: 2px solid #F2A9C0;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFAFC;
                color: #704653;
                selection-background-color: #F2A9C0;
                selection-color: #704653;
                border: 1px solid #EABAC9;
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

            QHeaderView::section {
                background-color: #FFDCE6;
                color: #704653;
                padding: 4px;
                border: 1px solid #EABAC9;
                font-size: 10pt;
                font-weight: 700;
            }

            QLabel#tableStatus {
                font-size: 8pt;
            }

            QPushButton {
                background-color: #FFDCE6;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 9px;
                padding: 5px 8px;
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

            QPushButton#rowRemoveButton {
                padding: 1px 3px;
                min-height: 16px;
                font-size: 8pt;
            }

            QPushButton#compactButton {
                padding: 2px 6px;
                min-height: 18px;
            }

            QFrame#memoryRegion {
                background-color: transparent;
                border: none;
            }

            QFrame#memoryRegionCurrent {
                background-color: #FFFAFC;
                border: 2px solid #C45B7A;
                border-radius: 6px;
            }

            QFrame#memoryBar {
                background-color: #FFF0F3;
                border: 1px solid #EABAC9;
                border-radius: 5px;
            }

            QLabel#allocatedLegend {
                background-color: #C45B7A;
                color: #FFFAFC;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 8pt;
                font-weight: 700;
            }

            QLabel#freeLegend {
                background-color: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 8pt;
                font-weight: 700;
            }

            QLabel#internalLegend {
                background-color: #F2A9C0;
                color: #704653;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 8pt;
                font-weight: 700;
            }

            QToolTip {
                background-color: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                font-family: "Nunito";
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from module.typography import load_application_fonts

    load_application_fonts(app)
    window = FragmentationWindow()
    window.show()
    sys.exit(app.exec())
