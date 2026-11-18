"""Interactive Multiprogramming simulator (Degree of Multiprogramming, Memory Admittance, and CPU Utilization)."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QGraphicsScene,
    QGraphicsView,
    QWidget,
    QSizePolicy,
    QSpinBox,
    QDoubleSpinBox,
)
from PySide6.QtGui import QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt

from algorithms.multiprogramming import simulate_multiprogramming, calculate_cpu_utilization

JOB_COLORS = [
    "#F6B6C8",  # Rose
    "#B9DDE8",  # Soft Cyan
    "#C7E6C0",  # Mint Green
    "#E5D0F2",  # Lavender
    "#F8D99A",  # Peach
    "#BFC9F5",  # Periwinkle
]


class MultiprogrammingWindow(QDialog):
    """Full-featured Multiprogramming simulator window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Multiprogramming - OS Simulator")
        self.setFixedSize(1020, 780)
        self.center_window()

        self.last_result = None

        self._build_ui()
        self._apply_stylesheet()
        self._load_defaults()
        self.calculate()

    def center_window(self):
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # Header Title
        title = QLabel("Multiprogramming Simulator")
        title.setObjectName("lblTitle")
        main_layout.addWidget(title)

        subtitle = QLabel("Simulate Degree of Multiprogramming (DOM), concurrent job memory admittance, and CPU utilization.")
        subtitle.setObjectName("lblSubtitle")
        main_layout.addWidget(subtitle)

        # Control Panel Card
        ctrl_card = QWidget()
        ctrl_card.setObjectName("cardPanel")
        ctrl_layout = QVBoxLayout(ctrl_card)
        ctrl_layout.setContentsMargins(14, 12, 14, 12)
        ctrl_layout.setSpacing(10)

        # Row 1: System Parameters
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Total RAM (KB):"))
        self.spinTotalRam = QSpinBox()
        self.spinTotalRam.setRange(256, 65536)
        self.spinTotalRam.setValue(1024)
        row1.addWidget(self.spinTotalRam, 1)

        row1.addWidget(QLabel("OS Reserved (KB):"))
        self.spinOsRam = QSpinBox()
        self.spinOsRam.setRange(0, 32768)
        self.spinOsRam.setValue(256)
        row1.addWidget(self.spinOsRam, 1)

        row1.addWidget(QLabel("Max Degree (DOM):"))
        self.spinMaxDom = QSpinBox()
        self.spinMaxDom.setRange(1, 32)
        self.spinMaxDom.setValue(4)
        row1.addWidget(self.spinMaxDom, 1)

        row1.addWidget(QLabel("I/O Wait Ratio (p):"))
        self.spinIoRatio = QDoubleSpinBox()
        self.spinIoRatio.setRange(0.0, 0.99)
        self.spinIoRatio.setSingleStep(0.05)
        self.spinIoRatio.setValue(0.60)
        row1.addWidget(self.spinIoRatio, 1)

        ctrl_layout.addLayout(row1)

        # Row 2: Job Table Actions
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Job Pool (Ready to Admit):"))
        row2.addStretch(1)

        btnAddJob = QPushButton("+ Add Job")
        btnAddJob.clicked.connect(self._add_job)
        btnRemoveJob = QPushButton("- Remove Job")
        btnRemoveJob.clicked.connect(self._remove_job)
        btnReset = QPushButton("Reset Example")
        btnReset.clicked.connect(self._load_defaults)

        row2.addWidget(btnAddJob)
        row2.addWidget(btnRemoveJob)
        row2.addWidget(btnReset)
        ctrl_layout.addLayout(row2)

        # Job Table
        self.tblJobs = QTableWidget(0, 4)
        self.tblJobs.setHorizontalHeaderLabels(["Job ID", "Arrival Time", "RAM Required (KB)", "Burst Time (ms)"])
        self.tblJobs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        ctrl_layout.addWidget(self.tblJobs)

        # Buttons
        row_btn = QHBoxLayout()
        self.btnSimulate = QPushButton("Run Multiprogramming Simulation")
        self.btnSimulate.clicked.connect(self.calculate)
        row_btn.addWidget(self.btnSimulate, 3)

        self.btnStepByStep = QPushButton("Step-by-Step")
        self.btnStepByStep.clicked.connect(self.show_step_by_step)
        row_btn.addWidget(self.btnStepByStep, 1)
        ctrl_layout.addLayout(row_btn)

        main_layout.addWidget(ctrl_card)

        # Metrics KPI Banner
        self.lblMetrics = QLabel("Average CPU Utilization: - | Avg Degree of Multiprogramming: - | Total Time: -")
        self.lblMetrics.setObjectName("lblMetrics")
        main_layout.addWidget(self.lblMetrics)

        # Results & Timeline Split View
        bot_layout = QHBoxLayout()
        bot_layout.setSpacing(12)

        # Completed Jobs Results Table
        self.tblResults = QTableWidget(0, 6)
        self.tblResults.setHorizontalHeaderLabels(["Job", "RAM", "Arrival", "Admitted", "Finished", "Turnaround"])
        self.tblResults.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tblResults.setFixedWidth(420)
        bot_layout.addWidget(self.tblResults)

        # Timeline Canvas (QGraphicsView)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setObjectName("graphView")
        bot_layout.addWidget(self.view, 1)

        main_layout.addLayout(bot_layout, 1)

        # Footer Back Button
        btnBack = QPushButton("Back to Dashboard")
        btnBack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btnBack.clicked.connect(self.close)
        main_layout.addWidget(btnBack)

    def _load_defaults(self):
        defaults = [
            ("J1", 0, 180, 8),
            ("J2", 1, 240, 6),
            ("J3", 2, 300, 10),
            ("J4", 3, 150, 4),
            ("J5", 5, 200, 7),
            ("J6", 6, 250, 5),
        ]
        self.tblJobs.setRowCount(len(defaults))
        for r, (jid, arr, ram, burst) in enumerate(defaults):
            self.tblJobs.setItem(r, 0, QTableWidgetItem(jid))
            self.tblJobs.setItem(r, 1, QTableWidgetItem(str(arr)))
            self.tblJobs.setItem(r, 2, QTableWidgetItem(str(ram)))
            self.tblJobs.setItem(r, 3, QTableWidgetItem(str(burst)))

    def _get_jobs(self):
        jobs = []
        for r in range(self.tblJobs.rowCount()):
            j_item = self.tblJobs.item(r, 0)
            a_item = self.tblJobs.item(r, 1)
            r_item = self.tblJobs.item(r, 2)
            b_item = self.tblJobs.item(r, 3)
            if not all([j_item, a_item, r_item, b_item]):
                continue
            jid = j_item.text().strip()
            try:
                arr = int(a_item.text().strip())
                size = int(r_item.text().strip())
                burst = int(b_item.text().strip())
            except ValueError:
                raise ValueError(f"Row {r + 1} has non-integer numerical values.")

            if arr < 0 or size <= 0 or burst <= 0:
                raise ValueError(f"Row {r + 1} has invalid negative or zero size/burst values.")
            jobs.append({"jid": jid, "arrival": arr, "size": size, "burst": burst})

        if not jobs:
            raise ValueError("Please add at least one job to the table.")
        return jobs

    def calculate(self):
        try:
            jobs = self._get_jobs()
            total_ram = self.spinTotalRam.value()
            os_ram = self.spinOsRam.value()
            max_dom = self.spinMaxDom.value()
            io_ratio = self.spinIoRatio.value()

            res = simulate_multiprogramming(jobs, total_ram, os_ram, max_dom, io_ratio)
            self.last_result = res
            self._display_results(res)
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def _display_results(self, res):
        self.lblMetrics.setText(
            f"Avg CPU Utilization: {res['avg_cpu_util']:.1f}% (Model: 1 - pⁿ)  |  "
            f"Avg DOM: {res['avg_dom']:.1f} jobs in RAM  |  "
            f"Avg Turnaround: {res['avg_tat']:.2f} ms  |  "
            f"Total Time: {res['total_time']} ms"
        )

        completed = res["completed"]
        self.tblResults.setRowCount(len(completed))
        for r, c in enumerate(completed):
            self.tblResults.setItem(r, 0, QTableWidgetItem(c["jid"]))
            self.tblResults.setItem(r, 1, QTableWidgetItem(f"{c['size']} KB"))
            self.tblResults.setItem(r, 2, QTableWidgetItem(str(c["arrival"])))
            self.tblResults.setItem(r, 3, QTableWidgetItem(str(c["admitted_at"])))
            self.tblResults.setItem(r, 4, QTableWidgetItem(str(c["finish_time"])))
            self.tblResults.setItem(r, 5, QTableWidgetItem(f"{c['turnaround']} ms"))

        self._draw_dom_timeline(res["timeline"], res["total_time"])

    def _draw_dom_timeline(self, timeline, total_time):
        self.scene.clear()
        if not timeline:
            return

        vw = max(self.view.viewport().width() - 40, 480)
        vh = max(self.view.viewport().height() - 40, 320)
        self.scene.setSceneRect(0, 0, vw, vh)

        max_dom = self.spinMaxDom.value()
        margin_left = 40
        margin_top = 30
        graph_w = vw - margin_left - 30
        graph_h = vh - margin_top - 40

        # Draw Coordinate Axes
        axis_pen = QPen(QColor("#704653"), 1.5)
        self.scene.addLine(margin_left, margin_top, margin_left, margin_top + graph_h, axis_pen)
        self.scene.addLine(margin_left, margin_top + graph_h, margin_left + graph_w, margin_top + graph_h, axis_pen)

        font_label = QFont("Nunito", 8)
        font_val = QFont("Nunito", 8, QFont.Weight.Bold)

        # Y-Axis marks (DOM levels 0, 1, 2, ... max_dom)
        for dom_level in range(max_dom + 1):
            y = margin_top + graph_h - (dom_level / max_dom) * graph_h
            self.scene.addLine(margin_left - 4, y, margin_left, y, axis_pen)
            lbl = self.scene.addText(str(dom_level), font_label)
            lbl.setDefaultTextColor(QColor("#704653"))
            lbl.setPos(margin_left - 24, y - 10)

        y_title = self.scene.addText("DOM", font_val)
        y_title.setDefaultTextColor(QColor("#C45B7A"))
        y_title.setPos(5, margin_top - 20)

        # Plot Step Chart of active Degree of Multiprogramming over time
        if total_time <= 0:
            return

        points = []
        for snapshot in timeline:
            x = margin_left + (snapshot["time"] / total_time) * graph_w
            y = margin_top + graph_h - (snapshot["dom"] / max_dom) * graph_h
            points.append((x, y, snapshot))

        line_pen = QPen(QColor("#C45B7A"), 2)
        brush_point = QBrush(QColor("#FFDCE6"))

        for i in range(len(points)):
            px, py, snap = points[i]
            # Draw step line to next point
            if i + 1 < len(points):
                next_px = points[i + 1][0]
                self.scene.addLine(px, py, next_px, py, line_pen)
                next_py = points[i + 1][1]
                self.scene.addLine(next_px, py, next_px, next_py, line_pen)

            self.scene.addEllipse(px - 4, py - 4, 8, 8, line_pen, brush_point)
            t_txt = self.scene.addText(f"T{snap['time']}", font_label)
            t_txt.setDefaultTextColor(QColor("#87475D"))
            t_txt.setPos(px - 10, margin_top + graph_h + 4)

            # Active Jobs tag
            if snap["active_jids"]:
                tag = ",".join(snap["active_jids"])
                tag_txt = self.scene.addText(tag, font_label)
                tag_txt.setDefaultTextColor(QColor("#704653"))
                tag_txt.setPos(px + 2, py - 16)

    def show_step_by_step(self):
        if not self.last_result:
            return
        res = self.last_result
        lines = [
            "=== Multiprogramming Execution Breakdown ===",
            f"Total RAM: {self.spinTotalRam.value()} KB | OS Reserved: {self.spinOsRam.value()} KB",
            f"Available for User Jobs: {res['available_ram']} KB",
            f"Max Degree of Multiprogramming: {self.spinMaxDom.value()}",
            f"Process I/O Wait Ratio (p): {self.spinIoRatio.value():.2f}",
            f"Average CPU Utilization: {res['avg_cpu_util']:.1f}%\n",
            "Timeline of Memory Admittance & Concurrency:"
        ]
        for t in res["timeline"]:
            active = ", ".join(t["active_jids"]) if t["active_jids"] else "None (Idle)"
            waiting = ", ".join(t["waiting_jids"]) if t["waiting_jids"] else "Empty"
            lines.append(
                f"Time {t['time']} ms: DOM = {t['dom']} | RAM Used = {t['ram_used']} KB | "
                f"Active in RAM = [{active}] | Waiting in Disk Queue = [{waiting}] | "
                f"CPU Util = {t['cpu_util']:.1f}%"
            )
        QMessageBox.information(self, "Multiprogramming Step-by-Step", "\n".join(lines))

    def _add_job(self):
        r = self.tblJobs.rowCount()
        self.tblJobs.insertRow(r)
        self.tblJobs.setItem(r, 0, QTableWidgetItem(f"J{r + 1}"))
        self.tblJobs.setItem(r, 1, QTableWidgetItem(str(r * 2)))
        self.tblJobs.setItem(r, 2, QTableWidgetItem("200"))
        self.tblJobs.setItem(r, 3, QTableWidgetItem("6"))

    def _remove_job(self):
        curr = self.tblJobs.currentRow()
        if curr >= 0:
            self.tblJobs.removeRow(curr)

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
                font-family: "Nunito";
                font-size: 10pt;
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
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #FFFFFF;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 6px;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #FFDCE6;
                color: #87475D;
                border: 1.5px solid #F3B5C8;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 10pt;
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
