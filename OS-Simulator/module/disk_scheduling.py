"""Interactive Disk Scheduling simulator and seek trajectory visualizer."""

import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsScene,
    QGraphicsView,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from algorithms.disk_scheduling import (
    fcfs,
    sstf,
    scan,
    c_scan,
    look,
    c_look,
)
from module.theme import style_dashboard_button
from module.window_utils import (
    center_adaptive_window,
    make_window_adaptive,
    wrap_in_scroll_area,
)


ALGORITHMS = {
    "FCFS (First-Come, First-Served)": fcfs,
    "SSTF (Shortest Seek Time First)": sstf,
    "SCAN (Elevator)": scan,
    "C-SCAN (Circular SCAN)": c_scan,
    "LOOK": look,
    "C-LOOK (Circular LOOK)": c_look,
}


class DiskSchedulingWindow(QDialog):
    """Window presenting disk scheduling algorithms and seek path graph."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Disk Scheduling - OS Simulator")
        make_window_adaptive(
            self, preferred_width=980, preferred_height=740, min_width=720, min_height=520
        )

        self.last_result = None

        self._build_ui()
        self._apply_stylesheet()
        self.calculate()

    def center_window(self):
        center_adaptive_window(self)

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("container")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(24, 20, 24, 11)
        main_layout.setSpacing(12)

        # Header Title
        title = QLabel("Disk Scheduling Simulator")
        title.setObjectName("lblTitle")
        main_layout.addWidget(title)

        subtitle = QLabel("Simulate seek operations, head movement paths, and compare disk I/O algorithms.")
        subtitle.setObjectName("lblSubtitle")
        main_layout.addWidget(subtitle)

        # Controls Bar
        ctrl_card = QWidget()
        ctrl_card.setObjectName("cardPanel")
        ctrl_layout = QVBoxLayout(ctrl_card)
        ctrl_layout.setContentsMargins(14, 12, 14, 12)
        ctrl_layout.setSpacing(10)

        # Row 1: Algorithm & Direction
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Algorithm:"))
        self.cmbAlgorithm = QComboBox()
        self.cmbAlgorithm.addItems(list(ALGORITHMS.keys()))
        self.cmbAlgorithm.currentTextChanged.connect(self._on_algo_changed)
        row1.addWidget(self.cmbAlgorithm, 3)

        self.lblDirection = QLabel("Direction:")
        self.cmbDirection = QComboBox()
        self.cmbDirection.addItems(["Higher Cylinders (Right)", "Lower Cylinders (Left)"])
        row1.addWidget(self.lblDirection)
        row1.addWidget(self.cmbDirection, 2)
        ctrl_layout.addLayout(row1)

        # Row 2: Head & Disk Size
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Initial Head:"))
        self.spinHead = QSpinBox()
        self.spinHead.setRange(0, 99999)
        self.spinHead.setValue(53)
        row2.addWidget(self.spinHead, 1)

        row2.addWidget(QLabel("Disk Size (Cylinders):"))
        self.spinDiskSize = QSpinBox()
        self.spinDiskSize.setRange(10, 100000)
        self.spinDiskSize.setValue(200)
        row2.addWidget(self.spinDiskSize, 1)

        ctrl_layout.addLayout(row2)

        # Row 3: Request Queue
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Track Requests:"))
        self.txtRequests = QLineEdit("98, 183, 37, 122, 14, 124, 65, 67")
        self.txtRequests.setPlaceholderText("Comma-separated track numbers (e.g., 98, 183, 37)")
        row3.addWidget(self.txtRequests, 4)

        self.btnSimulate = QPushButton("Calculate")
        self.btnSimulate.clicked.connect(self.calculate)
        row3.addWidget(self.btnSimulate, 1)

        self.btnStepByStep = QPushButton("Step-by-Step")
        self.btnStepByStep.clicked.connect(self.show_step_by_step)
        row3.addWidget(self.btnStepByStep, 1)

        ctrl_layout.addLayout(row3)
        main_layout.addWidget(ctrl_card)

        # Metrics Summary Banner
        self.lblMetrics = QLabel("Total Head Movements: - | Average Seek Distance: -")
        self.lblMetrics.setObjectName("lblMetrics")
        main_layout.addWidget(self.lblMetrics)

        # Main Visualization split (Table on left, Seek Chart on right)
        vis_layout = QHBoxLayout()
        vis_layout.setSpacing(12)

        # Step Table
        self.tblSteps = QTableWidget(0, 4)
        self.tblSteps.setHorizontalHeaderLabels(["Step", "From", "To", "Seek Distance"])
        self.tblSteps.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tblSteps.setFixedWidth(340)
        vis_layout.addWidget(self.tblSteps)

        # Seek Trajectory Canvas
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setObjectName("graphView")
        vis_layout.addWidget(self.view, 1)

        main_layout.addLayout(vis_layout, 1)

        # Footer Back Button
        self.btnBackToDashboard = QPushButton("Back to Dashboard")
        style_dashboard_button(self.btnBackToDashboard)
        self.btnBackToDashboard.clicked.connect(self.close)
        main_layout.addWidget(self.btnBackToDashboard)

        scroll = wrap_in_scroll_area(container, self)
        root_layout.addWidget(scroll)

        self._on_algo_changed(self.cmbAlgorithm.currentText())

    def _on_algo_changed(self, algo_name):
        needs_direction = any(k in algo_name for k in ("SCAN", "LOOK"))
        self.lblDirection.setVisible(needs_direction)
        self.cmbDirection.setVisible(needs_direction)

    def _parse_requests(self, max_cyl):
        raw = self.txtRequests.text().strip()
        if not raw:
            raise ValueError("Please enter at least one track request.")
        tokens = re.split(r"[\s,]+", raw)
        requests = []
        for token in tokens:
            if not token:
                continue
            try:
                val = int(token)
            except ValueError:
                raise ValueError(f"'{token}' is not a valid whole track number.")
            if val < 0 or val >= max_cyl:
                raise ValueError(f"Track {val} is outside cylinder range (0 to {max_cyl - 1}).")
            requests.append(val)
        if not requests:
            raise ValueError("No valid track requests found.")
        return requests

    def calculate(self):
        disk_size = self.spinDiskSize.value()
        head = self.spinHead.value()

        if head < 0 or head >= disk_size:
            QMessageBox.warning(self, "Invalid Head", f"Head position must be between 0 and {disk_size - 1}.")
            return

        try:
            requests = self._parse_requests(disk_size)
        except ValueError as err:
            QMessageBox.warning(self, "Invalid Input", str(err))
            return

        algo_key = self.cmbAlgorithm.currentText()
        direction = "high" if "Higher" in self.cmbDirection.currentText() else "low"

        if algo_key in ("SCAN (Elevator)", "C-SCAN (Circular SCAN)"):
            func = ALGORITHMS[algo_key]
            result = func(requests, head, disk_size=disk_size, direction=direction)
        elif algo_key in ("LOOK", "C-LOOK (Circular LOOK)"):
            func = ALGORITHMS[algo_key]
            result = func(requests, head, direction=direction)
        else:
            func = ALGORITHMS[algo_key]
            result = func(requests, head)

        self.last_result = result
        self._display_results(result, head, disk_size)

    def _display_results(self, result, head, disk_size):
        self.lblMetrics.setText(
            f"Total Head Movements: {result['total_seek']} cylinders  |  "
            f"Average Seek Distance: {result['average_seek']:.2f} cylinders  |  "
            f"Path: {' → '.join(map(str, result['sequence']))}"
        )

        steps = result["seek_steps"]
        self.tblSteps.setRowCount(len(steps))
        for row, step in enumerate(steps):
            self.tblSteps.setItem(row, 0, QTableWidgetItem(f"Step {step['step']}"))
            self.tblSteps.setItem(row, 1, QTableWidgetItem(str(step['from'])))
            self.tblSteps.setItem(row, 2, QTableWidgetItem(str(step['to'])))
            self.tblSteps.setItem(row, 3, QTableWidgetItem(f"{step['seek']} cyl"))

        self._draw_trajectory(result["sequence"], disk_size)

    def _draw_trajectory(self, sequence, disk_size):
        self.scene.clear()
        if not sequence:
            return

        vw = max(self.view.viewport().width(), 560)
        margin_left = 30
        margin_right = 30
        margin_top = 40
        step_height = 36
        draw_width = vw - margin_left - margin_right

        total_steps = len(sequence) - 1
        scene_height = margin_top + total_steps * step_height + 50
        self.scene.setSceneRect(0, 0, vw, scene_height)

        # Draw Cylinder Axis Guide (Top line)
        axis_pen = QPen(QColor("#EABAC9"), 1, Qt.PenStyle.DashLine)
        text_pen = QColor("#704653")
        font_axis = QFont("Nunito", 8)
        font_node = QFont("Nunito", 9, QFont.Weight.Bold)

        # Major grid lines at 0, 25%, 50%, 75%, 100%
        for ratio, label_val in [
            (0.0, 0),
            (0.25, int(disk_size * 0.25)),
            (0.5, int(disk_size * 0.5)),
            (0.75, int(disk_size * 0.75)),
            (1.0, disk_size - 1)
        ]:
            gx = margin_left + ratio * draw_width
            self.scene.addLine(gx, margin_top - 15, gx, scene_height - 30, axis_pen)
            t = self.scene.addText(str(label_val), font_axis)
            t.setDefaultTextColor(text_pen)
            t.setPos(gx - (t.boundingRect().width() / 2), margin_top - 36)

        # Compute point coordinates
        points = []
        for step_idx, track in enumerate(sequence):
            px = margin_left + (track / (disk_size - 1 if disk_size > 1 else 1)) * draw_width
            py = margin_top + step_idx * step_height
            points.append((px, py, track))

        # Connect paths with colored lines
        line_pen = QPen(QColor("#C45B7A"), 2)
        for i in range(1, len(points)):
            p1 = points[i - 1]
            p2 = points[i]
            self.scene.addLine(p1[0], p1[1], p2[0], p2[1], line_pen)

        # Draw nodes & values
        node_brush_head = QBrush(QColor("#C45B7A"))
        node_brush_req = QBrush(QColor("#FFDCE6"))
        node_pen = QPen(QColor("#704653"), 1.5)

        for idx, (px, py, track) in enumerate(points):
            brush = node_brush_head if idx == 0 else node_brush_req
            self.scene.addEllipse(px - 5, py - 5, 10, 10, node_pen, brush)

            lbl_txt = f"{track} (start)" if idx == 0 else f"{track} [#{idx}]"
            t = self.scene.addText(lbl_txt, font_node)
            t.setDefaultTextColor(text_pen)
            # Offset text slightly to avoid overlapping line
            offset_x = 8 if px + 50 < vw else -t.boundingRect().width() - 8
            t.setPos(px + offset_x, py - 10)

        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show_step_by_step(self):
        if not self.last_result:
            return
        res = self.last_result
        lines = [
            f"=== {self.cmbAlgorithm.currentText()} Step-by-Step Breakdown ===",
            f"Initial Head: {self.spinHead.value()}",
            f"Request Queue: {self.txtRequests.text()}",
            f"Total Seek Distance: {res['total_seek']} cylinders",
            f"Average Seek Time: {res['average_seek']:.2f} cylinders",
            "\nExecution Steps:"
        ]
        for step in res["seek_steps"]:
            lines.append(
                f"Step {step['step']}: Head moves from {step['from']} → {step['to']} "
                f"({step['seek']} cylinders traveled)."
            )
        QMessageBox.information(self, "Step-by-Step Explanation", "\n".join(lines))

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF0F3;
                color: #704653;
                font-family: "Nunito";
                font-size: 10pt;
            }
            QLabel {
                color: #704653;
                font-size: 10pt;
                font-family: "Nunito";
            }
            QLabel#lblTitle {
                color: #C45B7A;
                font-size: 20pt;
                font-weight: 700;
            }
            QLabel#lblSubtitle {
                color: #A77987;
                font-size: 10pt;
            }
            QLabel#lblMetrics {
                background-color: #FFFAFC;
                color: #87475D;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 10px;
                font-size: 10pt;
                font-weight: 700;
            }
            QWidget#cardPanel {
                background-color: #FFFAFC;
                border: 1px solid #EABAC9;
                border-radius: 12px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #FFFFFF;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 6px;
                font-size: 10pt;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #704653;
                selection-background-color: #FFDCE6;
                selection-color: #704653;
            }
            QPushButton {
                background-color: #FFDCE6;
                color: #87475D;
                border: 1.5px solid #F3B5C8;
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #FFC4D6;
            }
            QPushButton:pressed {
                background-color: #F2A9C0;
            }
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #FFF0F4;
                color: #704653;
                gridline-color: #F0C6D3;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                font-size: 9pt;
            }
            QHeaderView::section {
                background-color: #F8D4E0;
                color: #784254;
                padding: 6px;
                border: none;
                font-weight: 700;
            }
            QGraphicsView#graphView {
                background-color: #FFFFFF;
                border: 1px solid #EABAC9;
                border-radius: 8px;
            }
        """)
