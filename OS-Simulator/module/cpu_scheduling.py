from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsScene,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidgetItem,
)

from algorithms.cpu_scheduling import fcfs, priority_scheduling, round_robin, sjf
from ui_cpu_scheduling import Ui_Dialog


ALGORITHMS = {
    "FCFS": fcfs,
    "SJF": sjf,
    "Priority (Non-preemptive)": priority_scheduling,
}
PROCESS_COLORS = ["#F6B6C8", "#B9DDE8", "#C7E6C0", "#E5D0F2", "#F8D99A", "#BFC9F5"]


def setup_tables(dialog):
    dialog.ui.tblInput.setHorizontalHeaderLabels([
        "Process ID", "Arrival Time", "Burst Time", "Priority (lower = higher)"
    ])
    dialog.ui.tblInput.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )
    dialog.ui.tblResults.setHorizontalHeaderLabels([
        "Process ID", "Arrival", "Burst", "Priority", "First Start", "Finish",
        "Waiting", "Turnaround",
    ])
    dialog.ui.tblResults.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )


class CpuSchedulingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.btnBackToDashboard = QPushButton("Back to Dashboard", self)
        self.btnBackToDashboard.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.ui.verticalLayout.addStretch(1)
        self.ui.verticalLayout.addWidget(self.btnBackToDashboard)
        self.setWindowTitle("CPU Scheduling")
        self.resize(1000, 850)
        self.center_window()
        self.last_output = None

        self.ui.cmbAlgorithm.addItems([
            "FCFS", "SJF", "Priority (Non-preemptive)", "Round Robin"
        ])
        setup_tables(self)
        self.ui.cmbAlgorithm.currentTextChanged.connect(self.update_quantum_visibility)
        self.ui.btnAddProcess.clicked.connect(self.add_process)
        self.ui.btnRemoveProcess.clicked.connect(self.remove_process)
        self.ui.btnCalculate.clicked.connect(self.calculate)
        self.ui.btnStepByStep.clicked.connect(self.show_step_by_step)
        self.ui.btnReset.clicked.connect(self.reset)
        self.ui.btnClearAll.clicked.connect(self.clear_all)
        self.btnBackToDashboard.clicked.connect(self.close)

        self.add_process("P1", "0", "10", "2")
        self.add_process("P2", "0", "5", "1")
        self.add_process("P3", "0", "8", "3")
        self.update_quantum_visibility(self.ui.cmbAlgorithm.currentText())

    def center_window(self):
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())

    def add_process(self, pid=None, arrival=None, burst=None, priority=None):
        table = self.ui.tblInput
        row = table.rowCount()
        table.insertRow(row)
        values = [pid or f"P{row + 1}", arrival if arrival is not None else "0",
                  burst or "", priority if priority is not None else "1"]
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(str(value)))
        self.clear_output()

    def remove_process(self):
        row = self.ui.tblInput.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Select a process to remove.")
            return
        self.ui.tblInput.removeRow(row)
        self.clear_output()

    def update_quantum_visibility(self, algorithm):
        is_round_robin = algorithm == "Round Robin"
        self.ui.lblQuantum.setVisible(is_round_robin)
        self.ui.spinQuantum.setVisible(is_round_robin)

    def read_processes(self):
        processes = []
        needs_priority = self.ui.cmbAlgorithm.currentText() == "Priority (Non-preemptive)"
        for row in range(self.ui.tblInput.rowCount()):
            values = []
            for column in range(3):
                item = self.ui.tblInput.item(row, column)
                value = item.text().strip() if item else ""
                if not value:
                    raise ValueError(f"Complete all fields in row {row + 1}.")
                values.append(value)

            priority_item = self.ui.tblInput.item(row, 3)
            priority_text = priority_item.text().strip() if priority_item else ""
            if needs_priority and not priority_text:
                raise ValueError(f"Priority is required for {values[0]}.")
            if not priority_text:
                priority_text = "0"
            pid, arrival_text, burst_text = values
            if any(process["pid"] == pid for process in processes):
                raise ValueError(f"Duplicate Process ID: {pid}")
            try:
                arrival, burst, priority = map(
                    int, (arrival_text, burst_text, priority_text)
                )
            except ValueError:
                raise ValueError(f"Arrival, burst, and priority values for {pid} must be whole numbers.")
            if arrival < 0:
                raise ValueError(f"Arrival Time for {pid} cannot be negative.")
            if burst <= 0:
                raise ValueError(f"Burst Time for {pid} must be greater than zero.")
            processes.append({
                "pid": pid, "arrival": arrival, "burst": burst, "priority": priority
            })
        if not processes:
            raise ValueError("Add at least one process before running the simulation.")
        return processes

    def calculate(self):
        try:
            processes = self.read_processes()
            algorithm = self.ui.cmbAlgorithm.currentText()
            if algorithm == "Round Robin":
                output = round_robin(processes, self.ui.spinQuantum.value())
            else:
                output = ALGORITHMS[algorithm](processes)
            self.last_output = output
            self.display_results(output)
            return output
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Input", str(error))
            return None

    def display_results(self, output):
        table = self.ui.tblResults
        rows = output["results"]
        table.setRowCount(len(rows))
        for row, process in enumerate(rows):
            values = [process["pid"], process["arrival"], process["burst"],
                      process["priority"], process["start"], process["finish"],
                      process["waiting"], process["turnaround"]]
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(str(value)))
        self.ui.lblAvgWaiting.setText(
            f"Average Waiting Time: {output['average_waiting']:.2f}"
        )
        self.ui.lblAvgTurnaround.setText(
            f"Average Turnaround Time: {output['average_turnaround']:.2f}"
        )
        self.draw_gantt(output["schedule"])

    def draw_gantt(self, schedule):
        scene = QGraphicsScene(self)
        view = self.ui.ganttView
        view.setScene(scene)
        if not schedule:
            return

        left, top, right_margin = 16, 22, 16
        width = max(view.viewport().width(), 650) - left - right_margin
        total_time = max(segment["finish"] for segment in schedule)
        total_time = max(total_time, 1)
        scale = width / total_time
        block_height = 40
        font = QFont("Nunito", 9)
        font.setWeight(QFont.Weight.Bold)
        time_font = QFont("Nunito", 9)
        time_pen = QPen(QColor("#704653"))
        colors = {pid: QColor(PROCESS_COLORS[index % len(PROCESS_COLORS)])
                  for index, pid in enumerate(dict.fromkeys(
                      segment["pid"] for segment in schedule if segment["pid"]
                  ))}

        for segment in schedule:
            x = left + segment["start"] * scale
            block_width = max((segment["finish"] - segment["start"]) * scale, 1)
            if segment["pid"] is None:
                brush = QBrush(QColor("#E8E1E3"))
                label = "Idle"
            else:
                brush = QBrush(colors[segment["pid"]])
                label = segment["pid"]
            scene.addRect(x, top, block_width, block_height, QPen(QColor("#B77C8E")), brush)
            text = scene.addText(label, font)
            text.setDefaultTextColor(QColor("#704653"))
            text.setPos(x + max((block_width - text.boundingRect().width()) / 2, 2), top + 9)
            start_label = scene.addText(str(segment["start"]), time_font)
            start_label.setDefaultTextColor(QColor("#704653"))
            start_label.setPos(x - 4, top + block_height + 5)

        end_label = scene.addText(str(schedule[-1]["finish"]), time_font)
        end_label.setDefaultTextColor(QColor("#704653"))
        end_label.setPos(left + total_time * scale - 4, top + block_height + 5)
        scene.setSceneRect(0, 0, left + width + right_margin,
                           top + block_height + 28)
        view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show_step_by_step(self):
        output = self.calculate()
        if output is None:
            return
        algorithm = self.ui.cmbAlgorithm.currentText()
        lines = [f"Algorithm: {algorithm}"]
        if algorithm == "Round Robin":
            lines.append(f"Time quantum: {self.ui.spinQuantum.value()}")
        lines.append("\nExecution order:")
        for number, segment in enumerate(output["schedule"], start=1):
            label = segment["pid"] or "CPU Idle"
            duration = segment["finish"] - segment["start"]
            lines.append(
                f"{number}. Time {segment['start']} to {segment['finish']}: "
                f"{label} runs for {duration} time unit(s)."
            )
        lines.append("\nPer-process results:")
        for process in output["results"]:
            lines.append(
                f"{process['pid']}: arrived at {process['arrival']}, "
                f"first started at {process['start']}, finished at {process['finish']}; "
                f"waiting time {process['waiting']}, "
                f"turnaround time {process['turnaround']}."
            )
        lines.extend([
            f"\nAverage waiting time: {output['average_waiting']:.2f}",
            f"Average turnaround time: {output['average_turnaround']:.2f}",
        ])
        message = QMessageBox(self)
        message.setWindowTitle("Step-by-Step Execution")
        message.setIcon(QMessageBox.Icon.Information)
        message.setText("Scheduling simulation steps")
        message.setInformativeText("\n".join(lines))
        message.setTextFormat(Qt.TextFormat.PlainText)
        message.setStandardButtons(QMessageBox.StandardButton.Ok)
        message.exec()

    def clear_output(self):
        self.last_output = None
        self.ui.tblResults.setRowCount(0)
        self.ui.lblAvgWaiting.setText("Average Waiting Time: —")
        self.ui.lblAvgTurnaround.setText("Average Turnaround Time: —")
        self.ui.ganttView.setScene(QGraphicsScene(self))

    def clear_all(self):
        self.ui.tblInput.setRowCount(0)
        self.clear_output()

    def reset(self):
        self.ui.cmbAlgorithm.setCurrentIndex(0)
        self.ui.spinQuantum.setValue(2)
        self.ui.tblInput.setRowCount(0)
        self.add_process("P1", "0", "10", "2")
        self.add_process("P2", "0", "5", "1")
        self.add_process("P3", "0", "8", "3")
        self.clear_output()


CPUSchedulingWindow = CpuSchedulingWindow
