"""Interactive Banker’s Algorithm safety-check visualization."""

import random

from PySide6.QtCore import QEasingCurve, QEvent, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QIntValidator, QPalette
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
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


class AnimatedButton(QPushButton):
    """A button with a short, consistent color fade on hover."""

    def __init__(self, text):
        super().__init__(text)
        self._base_background = QColor("#FFFAFC")
        self._base_foreground = QColor("#704653")
        self._base_border = QColor("#EABAC9")
        self._hover_background = QColor("#FFDCE6")
        self._hover_foreground = QColor("#704653")
        self._hover_border = QColor("#C45B7A")
        self._hover_progress = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._apply_hover_progress)
        self._apply_hover_progress(0.0)

    def set_color_scheme(
        self,
        background,
        foreground,
        border,
        hover_background=None,
        hover_foreground=None,
        hover_border=None,
    ):
        self._base_background = QColor(background)
        self._base_foreground = QColor(foreground)
        self._base_border = QColor(border)
        self._hover_background = QColor(
            hover_background if hover_background is not None else QColor(0, 0, 0, 0)
        )
        self._hover_foreground = QColor(
            hover_foreground if hover_foreground is not None else foreground
        )
        self._hover_border = QColor(
            hover_border if hover_border is not None else border
        )
        self._apply_hover_progress(self._hover_progress)

    def enterEvent(self, event):
        if self.isEnabled():
            self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.0)
        super().leaveEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._animate_to(0.0)

    def _animate_to(self, progress):
        self._animation.stop()
        self._animation.setStartValue(self._hover_progress)
        self._animation.setEndValue(progress)
        self._animation.start()

    def _apply_hover_progress(self, progress):
        self._hover_progress = float(progress)
        if self.isEnabled():
            background = self._blend(
                self._base_background, self._hover_background, self._hover_progress
            )
            foreground = self._blend(
                self._base_foreground, self._hover_foreground, self._hover_progress
            )
            border = self._blend(
                self._base_border, self._hover_border, self._hover_progress
            )
        else:
            background = self._base_background
            foreground = self._base_foreground
            border = self._base_border
        self.setStyleSheet(
            "background-color: rgba(%d, %d, %d, %d); color: %s; border-color: %s;"
            % (
                background.red(),
                background.green(),
                background.blue(),
                background.alpha(),
                foreground.name(),
                border.name(),
            )
        )

    @staticmethod
    def _blend(start, end, progress):
        return QColor(
            round(start.red() + (end.red() - start.red()) * progress),
            round(start.green() + (end.green() - start.green()) * progress),
            round(start.blue() + (end.blue() - start.blue()) * progress),
            round(start.alpha() + (end.alpha() - start.alpha()) * progress),
        )


class ResourceSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFAFC"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#704653"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#F2A9C0"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#704653"))
        self.setPalette(palette)
        self.lineEdit().setPalette(palette)
        self.lineEdit().setStyleSheet(
            "QLineEdit {"
            " background-color: #FFFAFC; color: #704653;"
            " border: 1px solid #EABAC9; border-radius: 6px;"
            ' padding: 2px 4px; font-family: "Nunito";'
            " font-size: 12pt; font-weight: 600;"
            " selection-background-color: #F2A9C0;"
            " selection-color: #704653;"
            "}"
            "QLineEdit:focus { border: 2px solid #C45B7A; }"
        )

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.lineEdit().deselect()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.lineEdit().deselect()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.lineEdit().deselect()

    def stepBy(self, steps):
        super().stepBy(steps)
        self.lineEdit().deselect()


class ResourceField(QLineEdit):
    """Plain numeric input used for the Allocation and Max table cells.

    A QLineEdit is used instead of a QSpinBox because a spinbox's internal line
    edit ignores the dialog stylesheet (dark-mode palette text ends up white on
    white), which is what made the table values vanish until they were clicked.
    A line edit styled directly always renders its text. The API mirrors the
    parts of QSpinBox the simulator uses (value, setValue, valueChanged).
    """

    valueChanged = Signal(int)

    def __init__(self, minimum=0, maximum=999):
        super().__init__("0")
        self._minimum = minimum
        self._maximum = maximum
        self._value = minimum
        self.setValidator(QIntValidator(minimum, maximum, self))
        self.setMaxLength(len(str(maximum)))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textEdited.connect(self._text_edited)
        self.set_highlighted(False)

    def value(self):
        return self._value

    def setValue(self, value):
        value = max(self._minimum, min(self._maximum, int(value)))
        text = str(value)
        if self.text() != text:
            self.setText(text)
        self._set_value(value)

    def stepUp(self):
        self.setValue(self._value + 1)

    def stepDown(self):
        self.setValue(self._value - 1)

    def set_highlighted(self, highlighted):
        """Pink outline marks the most recently changed value; otherwise plain."""
        border = "#C45B7A" if highlighted else "#EABAC9"
        self.setStyleSheet(
            "QLineEdit {"
            " background: #FFFAFC; color: #704653;"
            " border: 2px solid %s; border-radius: 7px;"
            ' padding: 0 2px; font-family: "Nunito";'
            " font-size: 12pt; font-weight: 600;"
            " selection-background-color: #F2A9C0; selection-color: #704653;"
            "}"
            "QLineEdit:focus { border: 2px solid #C45B7A; }" % border
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.stepUp()
        elif event.key() == Qt.Key.Key_Down:
            self.stepDown()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setText(str(self._value))  # tidy up an empty or partial entry

    def _text_edited(self, text):
        self._set_value(int(text) if text else self._minimum)

    def _set_value(self, value):
        if value != self._value:
            self._value = value
            self.valueChanged.emit(value)


RESOURCE_NAMES = ("A", "B", "C")
SAMPLE_ALLOCATION = (
    (0, 1, 0),
    (2, 0, 0),
    (3, 0, 2),
    (2, 1, 1),
    (0, 0, 2),
)
SAMPLE_MAXIMUM = (
    (7, 5, 3),
    (3, 2, 2),
    (9, 0, 2),
    (2, 2, 2),
    (4, 3, 3),
)
SAMPLE_AVAILABLE = (3, 3, 2)


def find_safe_sequence(allocation, maximum, available):
    """Return a safe sequence, or None when the state is unsafe."""
    process_count = len(allocation)
    if process_count != len(maximum):
        raise ValueError("Allocation and maximum must have the same process count.")
    if len(available) != len(RESOURCE_NAMES):
        raise ValueError("Exactly three available resource values are required.")

    work = list(available)
    needs = []
    for held, claim in zip(allocation, maximum):
        if len(held) != len(RESOURCE_NAMES) or len(claim) != len(RESOURCE_NAMES):
            raise ValueError("Each process must have exactly three resource values.")
        if any(value < 0 for value in (*held, *claim)):
            raise ValueError("Resource values cannot be negative.")
        if any(held_value > claim_value for held_value, claim_value in zip(held, claim)):
            raise ValueError("Allocation cannot exceed a process's maximum claim.")
        needs.append([claim_value - held_value for held_value, claim_value in zip(held, claim)])

    if any(value < 0 for value in work):
        raise ValueError("Available resource values cannot be negative.")

    finished = [False] * process_count
    sequence = []
    while len(sequence) < process_count:
        for process in range(process_count):
            if not finished[process] and all(
                need <= amount for need, amount in zip(needs[process], work)
            ):
                work = [
                    amount + held
                    for amount, held in zip(work, allocation[process])
                ]
                finished[process] = True
                sequence.append(process)
                break
        else:
            return None

    return sequence


class BankersWindow(QDialog):
    """A step-by-step, editable Banker’s Algorithm safety simulator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Banker's Algorithm | OS Simulator")
        self.setFixedSize(1060, 820)
        self.setStyleSheet(
            """
            QDialog {
                background: #FFF0F3;
                color: #704653;
                font-family: "Nunito";
                font-size: 10pt;
            }
            QWidget { font-family: "Nunito"; }
            QWidget#content { background: #FFF0F3; }
            QLabel { color: #704653; font-size: 10pt; }
            QLabel#eyebrow {
                color: #C45B7A;
                font-size: 11pt;
                font-weight: 700;
            }
            QLabel#title {
                color: #C45B7A;
                font-size: 24pt;
                font-weight: 700;
            }
            QLabel#muted {
                color: #704653;
                font-size: 10pt;
            }
            QLabel#ruleText {
                color: #704653;
                font-size: 10pt;
                font-weight: 700;
            }
            QLabel#detail {
                background: #FFDCE6;
                color: #704653;
                border-left: 4px solid #C45B7A;
                padding: 7px;
                font-size: 10pt;
            }
            QFrame#panel {
                background: #FFFAFC;
                border: 1px solid #EABAC9;
                border-radius: 12px;
            }
            QFrame#panel QLabel,
            QFrame#accentPanel QLabel { color: #704653; }
            QFrame#availablePanel {
                background: transparent;
                border: none;
            }
            QFrame#availablePanel QLabel { color: #C45B7A; }
            QFrame#accentPanel {
                background: #FFFAFC;
                border: 1px solid #C45B7A;
                border-radius: 12px;
            }
            QTableWidget {
                background: #FFFAFC;
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
                background: #FFDCE6;
                color: #704653;
                padding: 6px 4px;
                border: 0;
                border-right: 1px solid #EABAC9;
                border-bottom: 2px solid #EABAC9;
                font-weight: 700;
                font-size: 10pt;
            }
            QSpinBox QLineEdit {
                background: #FFFAFC;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 7px;
                padding: 0 2px;
                min-height: 28px;
                font-size: 10pt;
                font-weight: 600;
                selection-background-color: #F2A9C0;
                selection-color: #704653;
            }
            QSpinBox QLineEdit:focus { border: 1px solid #C45B7A; }
            QPushButton {
                background: #FFDCE6;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 10px;
                min-height: 38px;
                padding: 7px 16px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover { background: #F2A9C0; }
            QPushButton:focus { border: 2px solid #C45B7A; }
            QPushButton:disabled {
                background: #FFF0F3;
                color: #704653;
                border-color: #EABAC9;
            }
            QPushButton#primary {
                background: #C45B7A;
                color: #FFFAFC;
                border-color: #C45B7A;
            }
            QPushButton#primary:hover {
                background: #F2A9C0;
                color: #704653;
                border-color: #C45B7A;
            }
            QPushButton#primary:disabled {
                background: #FFF0F3;
                color: #704653;
                border-color: #EABAC9;
            }
            QPushButton#resourceStep {
                border-radius: 8px;
                padding: 0;
                min-height: 28px;
                font-size: 10pt;
            }
            """
        )

        self.available_inputs = []
        self.allocation_inputs = []
        self.maximum_inputs = []
        self.process_tiles = []
        self.work_values = list(SAMPLE_AVAILABLE)
        self.completed_processes = set()
        self.sequence = []
        self._refreshing = False
        self._highlighted_fields = []  # cells holding the most recent change

        content = QWidget()
        content.setObjectName("content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(10)
        self._build_header(layout)
        self._build_available_panel(layout)
        self._build_matrix_panel(layout)
        self._build_simulation_panel(layout)
        self._build_controls(layout)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(content)
        self._load_sample()

    def _build_header(self, parent_layout):
        header = QVBoxLayout()
        header.setSpacing(2)
        title = QLabel("Banker's Algorithm")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("A visual check for safe resource allocation")
        subtitle.setObjectName("muted")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(title)
        header.addWidget(subtitle)
        parent_layout.addLayout(header)

    def _build_available_panel(self, parent_layout):
        panel = QFrame()
        panel.setObjectName("availablePanel")
        row = QHBoxLayout(panel)
        row.setContentsMargins(0, 4, 0, 4)

        intro = QVBoxLayout()
        label = QLabel("Available resources")
        label.setObjectName("eyebrow")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.addWidget(label)
        row.addLayout(intro, 1)

        for resource in RESOURCE_NAMES:
            resource_layout = QVBoxLayout()
            name = QLabel(resource)
            name.setObjectName("eyebrow")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value = ResourceSpinBox()
            value.setRange(0, 999)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            value.setFrame(False)
            value.setFixedWidth(64)
            value.setFixedHeight(34)
            value.setAccessibleName("Available Resource " + resource)
            value.setToolTip("Number of free units of Resource " + resource)
            value.valueChanged.connect(self._other_input_changed)
            self.available_inputs.append(value)
            controls = QHBoxLayout()
            controls.setSpacing(5)
            decrease = self._resource_step_button("-", "Decrease", resource)
            increase = self._resource_step_button("+", "Increase", resource)
            decrease.clicked.connect(value.stepDown)
            increase.clicked.connect(value.stepUp)
            controls.addStretch(1)
            controls.addWidget(decrease)
            controls.addWidget(value)
            controls.addWidget(increase)
            controls.addStretch(1)
            resource_layout.addWidget(name)
            resource_layout.addLayout(controls)
            row.addLayout(resource_layout, 1)
        parent_layout.addWidget(panel)

    @staticmethod
    def _resource_step_button(text, action, resource):
        button = AnimatedButton(text)
        button.setObjectName("resourceStep")
        button.setAccessibleName("%s available Resource %s" % (action, resource))
        button.setToolTip("%s available units of Resource %s" % (action, resource))
        button.setFixedSize(28, 32)
        button.set_color_scheme(
            "#FFDCE6", "#704653", "#EABAC9",
            "#F2A9C0", "#704653", "#C45B7A",
        )
        return button

    def _build_matrix_panel(self, parent_layout):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 10, 14, 10)
        title_row = QHBoxLayout()
        title = QLabel("Resources")
        title.setObjectName("eyebrow")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.addWidget(title)
        layout.addLayout(title_row)

        group_headers = QHBoxLayout()
        process_header = QLabel("Process")
        process_header.setFixedWidth(105)
        group_headers.addWidget(process_header)
        allocation_header = QLabel("Allocation")
        group_headers.addWidget(allocation_header, 1)
        maximum_header = QLabel("Max")
        group_headers.addWidget(maximum_header, 1)
        need_header = QLabel("Need")
        group_headers.addWidget(need_header, 1)
        for label in (
            process_header,
            allocation_header,
            maximum_header,
            need_header,
        ):
            label.setObjectName("eyebrow")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                'font-family: "Nunito"; font-size: 10pt;'
                " font-weight: 700;"
                + (" color: #C45B7A;" if label is need_header else "")
            )
        layout.addLayout(group_headers)

        self.table = QTableWidget(5, 10)
        self.table.setHorizontalHeaderLabels(
            ["PID", "A", "B", "C", "A", "B", "C", "A", "B", "C"]
        )
        self.table.setAccessibleName("Banker's Algorithm resource ledger")
        self.table.setAccessibleDescription(
            "Allocation, maximum claim, and remaining need for five processes."
        )
        self.table.setVerticalHeaderLabels([""] * 5)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(0, 105)

        for process in range(5):
            process_item = QTableWidgetItem("P%d" % process)
            process_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            process_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(process, 0, process_item)
            self.allocation_inputs.append([])
            self.maximum_inputs.append([])
            for resource in range(3):
                allocation = ResourceField()
                maximum = ResourceField()
                allocation.setAccessibleName(
                    "Allocation for process P%d, Resource %s"
                    % (process, RESOURCE_NAMES[resource])
                )
                maximum.setAccessibleName(
                    "Maximum claim for process P%d, Resource %s"
                    % (process, RESOURCE_NAMES[resource])
                )
                allocation.setToolTip("Currently allocated units")
                maximum.setToolTip("Maximum units this process may request")
                allocation.valueChanged.connect(
                    lambda _value, p=process, r=resource: self._allocation_changed(p, r)
                )
                maximum.valueChanged.connect(self._other_input_changed)
                self.allocation_inputs[process].append(allocation)
                self.maximum_inputs[process].append(maximum)
                self.table.setCellWidget(
                    process, 1 + resource, self._input_cell(allocation)
                )
                self.table.setCellWidget(
                    process, 4 + resource, self._input_cell(maximum)
                )
                need_item = QTableWidgetItem("0")
                need_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                need_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(process, 7 + resource, need_item)

        self.table.setFixedHeight(224)
        layout.addWidget(self.table)
        parent_layout.addWidget(panel)

    def _build_simulation_panel(self, parent_layout):
        panel = QFrame()
        panel.setObjectName("panel")
        row = QHBoxLayout(panel)
        row.setContentsMargins(14, 12, 14, 12)

        progress = QVBoxLayout()
        progress_heading = QHBoxLayout()
        progress_title = QLabel("SAFETY CHECK")
        progress_title.setObjectName("eyebrow")
        self.state_label = QLabel("READY")
        self.state_label.setAccessibleName("Safety-check status")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setMinimumWidth(84)
        progress_heading.addWidget(progress_title)
        progress_heading.addStretch(1)
        progress_heading.addWidget(self.state_label)
        progress.addLayout(progress_heading)
        tiles = QHBoxLayout()
        for process in range(5):
            tile = QLabel("P%d\nWAITING" % process)
            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile.setMinimumSize(82, 54)
            tile.setStyleSheet(
                "background: #FFFAFC; border: 1px solid #EABAC9; "
                "border-radius: 8px; color: #704653; "
                'font-family: "Nunito"; font-size: 10pt;'
                " font-weight: 700;"
            )
            self.process_tiles.append(tile)
            tiles.addWidget(tile)
        progress.addLayout(tiles)
        self.progress_label = QLabel("Completed: 0 / 5  ·  Order: —")
        self.progress_label.setObjectName("muted")
        progress.addWidget(self.progress_label)
        self.status_label = QLabel("Edit the inputs, then step through or run the check.")
        self.status_label.setObjectName("detail")
        self.status_label.setWordWrap(True)
        progress.addWidget(self.status_label)
        row.addLayout(progress, 3)

        work_panel = QFrame()
        work_panel.setObjectName("accentPanel")
        work_layout = QVBoxLayout(work_panel)
        work_layout.setContentsMargins(12, 10, 12, 10)
        work_title = QLabel("Work")
        work_title.setObjectName("eyebrow")
        work_layout.addWidget(work_title)
        self.work_label = QLabel("A  3      B  3      C  2")
        self.work_label.setStyleSheet(
            'font-family: "Nunito"; font-size: 12pt; '
            "font-weight: 600; color: #704653;"
        )
        work_layout.addWidget(self.work_label)
        row.addWidget(work_panel, 1)
        parent_layout.addWidget(panel)

    def _build_controls(self, parent_layout):
        row = QHBoxLayout()
        self.step_button = AnimatedButton("Check next step")
        self.step_button.set_color_scheme(
            "#FFDCE6", "#704653", "#EABAC9",
            "#F2A9C0", "#704653", "#C45B7A",
        )
        self.step_button.setFixedHeight(42)
        self.step_button.setAccessibleName("Check next safety step")
        self.step_button.setToolTip("Advance the safety check by one eligible process.")
        self.step_button.clicked.connect(self._step)
        row.addWidget(self.step_button)
        self.run_button = AnimatedButton("Run check")
        self.run_button.setObjectName("primary")
        self.run_button.set_color_scheme(
            "#C45B7A", "#FFFAFC", "#C45B7A",
            "#F2A9C0", "#704653", "#C45B7A",
        )
        self.run_button.setFixedHeight(42)
        self.run_button.setAccessibleName("Run full safety check")
        self.run_button.setToolTip("Complete the safety check and show the result.")
        self.run_button.clicked.connect(self._run_all)
        self.reset_button = AnimatedButton("Reset")
        self.reset_button.set_color_scheme(
            "#FFDCE6", "#704653", "#EABAC9",
            "#F2A9C0", "#704653", "#C45B7A",
        )
        self.reset_button.setFixedHeight(42)
        self.reset_button.setAccessibleName("Load sample values")
        self.reset_button.setToolTip(
            "Restore the built-in five-process example and restart the check."
        )
        self.reset_button.clicked.connect(self._load_sample)
        row.addWidget(self.reset_button)
        self.random_button = AnimatedButton("Random example")
        self.random_button.set_color_scheme(
            "#FFDCE6", "#704653", "#EABAC9",
            "#F2A9C0", "#704653", "#C45B7A",
        )
        self.random_button.setFixedHeight(42)
        self.random_button.setAccessibleName("Load random example")
        self.random_button.setToolTip(
            "Generate random Available, Max and Allocation values and restart the check."
        )
        self.random_button.clicked.connect(self._random_example)
        row.addWidget(self.random_button)
        row.addWidget(self.run_button)
        parent_layout.addLayout(row)
        self.dashboard_button = AnimatedButton("Back to Dashboard")
        self.dashboard_button.set_color_scheme(
            "#FFDCE6", "#704653", "#EABAC9",
            "#F2A9C0", "#704653", "#C45B7A",
        )
        self.dashboard_button.setFixedHeight(42)
        self.dashboard_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.dashboard_button.setAccessibleName("Back to Dashboard")
        self.dashboard_button.setToolTip("Close this simulator and return to the dashboard.")
        self.dashboard_button.clicked.connect(self.close)
        parent_layout.addStretch(1)
        parent_layout.addWidget(self.dashboard_button)

    @staticmethod
    def _input_cell(field):
        """Place a field in a table cell with padding so outlines never touch."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(3, 2, 3, 2)
        layout.addWidget(field)
        return container

    def _set_highlight(self, fields):
        """Pink-outline `fields` (the latest change) and un-highlight the rest."""
        for field in self._highlighted_fields:
            field.set_highlighted(False)
        self._highlighted_fields = list(fields)
        for field in self._highlighted_fields:
            field.set_highlighted(True)

    def _allocation_changed(self, process, resource):
        if not self._refreshing:
            self._set_highlight([self.allocation_inputs[process][resource]])
        self._inputs_changed()

    def _other_input_changed(self, _value=None):
        # Available or Max changed: the check restarts, so drop any old highlight.
        if not self._refreshing:
            self._set_highlight([])
        self._inputs_changed()

    def _load_sample(self):
        self._apply_example(SAMPLE_AVAILABLE, SAMPLE_ALLOCATION, SAMPLE_MAXIMUM)

    def _apply_example(self, available, allocation, maximum):
        self._set_highlight([])
        self._refreshing = True
        for index, value in enumerate(available):
            self.available_inputs[index].setValue(value)
        for process in range(5):
            for resource in range(3):
                self.allocation_inputs[process][resource].setValue(
                    allocation[process][resource]
                )
                self.maximum_inputs[process][resource].setValue(
                    maximum[process][resource]
                )
        self._refreshing = False
        self._restart_simulation()

    def _random_example(self):
        """Load a random valid example (Allocation never exceeds Max).

        Most examples are retried until the safety check finds a safe order, so
        the walkthrough is usually clean; about one in four is kept as-is so
        unsafe states show up too. Work, Need and the result follow from the
        inputs, exactly as in the real algorithm.
        """
        keep_unsafe = random.random() < 0.25
        for _ in range(500):
            maximum = [[random.randint(0, 9) for _ in range(3)] for _ in range(5)]
            allocation = [
                [random.randint(0, claim) for claim in row] for row in maximum
            ]
            available = [random.randint(0, 5) for _ in range(3)]
            if keep_unsafe or find_safe_sequence(allocation, maximum, available):
                break
        self._apply_example(available, allocation, maximum)

    def _inputs_changed(self, _value=None):
        if self._refreshing:
            return
        self._restart_simulation()

    def _restart_simulation(self):
        self.completed_processes.clear()
        self.sequence.clear()
        self.work_values = [value.value() for value in self.available_inputs]
        valid = True
        for process in range(5):
            for resource in range(3):
                held = self.allocation_inputs[process][resource].value()
                claim = self.maximum_inputs[process][resource].value()
                item = self.table.item(process, 7 + resource)
                if held > claim:
                    new_text = "!"
                    item.setForeground(QColor("#C45B7A"))
                    valid = False
                else:
                    new_text = str(claim - held)
                    item.setForeground(QColor("#704653"))
                if item.text() != new_text:
                    item.setText(new_text)
        self._update_visuals()
        if valid:
            self.status_label.setText(
                "Inputs ready. Run one step at a time or complete the full safety check."
            )
            self._set_state("READY", "ready")
        else:
            self.status_label.setText(
                "Invalid input: Allocation cannot exceed Max. Correct the marked Need cells."
            )
            self._set_state("INVALID", "invalid")
        self.step_button.setEnabled(valid)
        self.run_button.setEnabled(valid)

    def _step(self):
        if not self._inputs_are_valid():
            return
        for process in range(5):
            if process in self.completed_processes:
                continue
            needs = self._need_for(process)
            if all(need <= work for need, work in zip(needs, self.work_values)):
                previous_work = list(self.work_values)
                released = [
                    value.value() for value in self.allocation_inputs[process]
                ]
                self.work_values = [
                    work + held for work, held in zip(self.work_values, released)
                ]
                self.completed_processes.add(process)
                self.sequence.append(process)
                # This step's Allocation and Max are the most recent change.
                self._set_highlight(
                    self.allocation_inputs[process] + self.maximum_inputs[process]
                )
                self._update_visuals()
                self.status_label.setText(
                    "P%d is eligible: Need %s ≤ Work %s. When it finishes, "
                    "Allocation %s returns to Work."
                    % (
                        process,
                        self._vector(needs),
                        self._vector(previous_work),
                        self._vector(released),
                    )
                )
                self._set_state("IN PROGRESS", "progress")
                if len(self.completed_processes) == 5:
                    self.status_label.setText(
                        "SAFE STATE. Every process can finish in this order: %s."
                        % "  →  ".join("P%d" % item for item in self.sequence)
                    )
                    self._set_state("SAFE", "safe")
                    self.step_button.setEnabled(False)
                    self.run_button.setEnabled(False)
                return

        blocked = [
            "P%d" % process
            for process in range(5)
            if process not in self.completed_processes
        ]
        self.status_label.setText(
            "UNSAFE STATE. No remaining process satisfies Need ≤ Work. Waiting: %s."
            % ", ".join(blocked)
        )
        self._set_state("UNSAFE", "unsafe")
        self.step_button.setEnabled(False)
        self.run_button.setEnabled(False)

    def _run_all(self):
        while self.step_button.isEnabled() and len(self.completed_processes) < 5:
            self._step()

    def _inputs_are_valid(self):
        for process in range(5):
            for resource in range(3):
                if (
                    self.allocation_inputs[process][resource].value()
                    > self.maximum_inputs[process][resource].value()
                ):
                    self.status_label.setText(
                        "Invalid input: Allocation cannot exceed Max."
                    )
                    self._set_state("INVALID", "invalid")
                    return False
        return True

    def _need_for(self, process):
        return [
            self.maximum_inputs[process][resource].value()
            - self.allocation_inputs[process][resource].value()
            for resource in range(3)
        ]

    def _update_visuals(self):
        for process, tile in enumerate(self.process_tiles):
            if process in self.completed_processes:
                order = self.sequence.index(process) + 1
                color, text_color, state = "#C45B7A", "#FFFAFC", "DONE · %d" % order
            else:
                color, text_color, state = "#FFFAFC", "#704653", "WAITING"
            tile.setText("P%d\n%s" % (process, state))
            tile.setStyleSheet(
                "background: %s; border: 1px solid #EABAC9; "
                'color: %s; font-family: "Nunito";'
                " font-size: 10pt; font-weight: 700;"
                % (color, text_color)
            )
        order = " > ".join("P%d" % process for process in self.sequence)
        self.progress_label.setText(
            "Completed: %d / 5  ·  Order: %s"
            % (len(self.completed_processes), order or "—")
        )
        self.work_label.setText(
            "A  %d      B  %d      C  %d" % tuple(self.work_values)
        )

    def _set_state(self, text, kind):
        palette = {
            "ready": ("#FFFAFC", "#704653", "#EABAC9"),
            "progress": ("#FFDCE6", "#704653", "#EABAC9"),
            "safe": ("#C45B7A", "#FFFAFC", "#C45B7A"),
            "unsafe": ("#C45B7A", "#FFFAFC", "#C45B7A"),
            "invalid": ("#C45B7A", "#FFFAFC", "#C45B7A"),
        }
        background, foreground, border = palette[kind]
        self.state_label.setText(text)
        self.state_label.setStyleSheet(
            "background: %s; color: %s; border: 1px solid %s; "
            'padding: 4px 8px; font-family: "Nunito";'
            " font-size: 10pt; font-weight: 700;"
            % (background, foreground, border)
        )

    @staticmethod
    def _vector(values):
        return "[%s]" % ", ".join(str(value) for value in values)


__all__ = ["BankersWindow", "find_safe_sequence"]