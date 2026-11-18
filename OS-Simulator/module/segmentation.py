"""Interactive Memory Segmentation simulator and physical map visualizer."""

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
)
from PySide6.QtGui import QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt

from algorithms.segmentation import translate_segment_address

SEGMENT_COLORS = [
    "#F6B6C8",  # Rose
    "#B9DDE8",  # Soft Cyan
    "#C7E6C0",  # Mint Green
    "#E5D0F2",  # Lavender
    "#F8D99A",  # Peach
    "#BFC9F5",  # Periwinkle
]


class SegmentationWindow(QDialog):
    """Full-featured Segmentation simulator window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Segmentation - OS Simulator")
        self.setFixedSize(1000, 750)
        self.center_window()

        self._build_ui()
        self._apply_stylesheet()
        self._load_default_segments()
        self.translate()

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
        title = QLabel("Memory Segmentation Simulator")
        title.setObjectName("lblTitle")
        main_layout.addWidget(title)

        subtitle = QLabel("Manage variable-sized memory segments and test logical-to-physical address translation.")
        subtitle.setObjectName("lblSubtitle")
        main_layout.addWidget(subtitle)

        # Central 2-Column Split
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Left Column: Segment Table & Translation Controls
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        # Segment Table Header & Actions
        table_bar = QHBoxLayout()
        table_bar.addWidget(QLabel("Segment Table:"))
        table_bar.addStretch(1)

        btnAdd = QPushButton("+ Add Segment")
        btnAdd.clicked.connect(self._add_row)
        btnRemove = QPushButton("- Remove")
        btnRemove.clicked.connect(self._remove_row)
        btnReset = QPushButton("Reset Example")
        btnReset.clicked.connect(self._load_default_segments)

        table_bar.addWidget(btnAdd)
        table_bar.addWidget(btnRemove)
        table_bar.addWidget(btnReset)
        left_col.addLayout(table_bar)

        self.tblSegments = QTableWidget(0, 4)
        self.tblSegments.setHorizontalHeaderLabels(["Seg #", "Segment Name", "Base Address", "Limit (Size)"])
        self.tblSegments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tblSegments.itemChanged.connect(lambda: self._draw_memory_bar())
        left_col.addWidget(self.tblSegments, 3)

        # Logical Address Input Card
        input_card = QWidget()
        input_card.setObjectName("cardPanel")
        card_layout = QVBoxLayout(input_card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)

        row = QHBoxLayout()
        row.addWidget(QLabel("Segment Number (s):"))
        self.txtSegNum = QLineEdit("2")
        self.txtSegNum.setPlaceholderText("e.g. 2")
        row.addWidget(self.txtSegNum)

        row.addWidget(QLabel("Offset (d):"))
        self.txtOffset = QLineEdit("53")
        self.txtOffset.setPlaceholderText("e.g. 53")
        row.addWidget(self.txtOffset)
        card_layout.addLayout(row)

        self.btnTranslate = QPushButton("Translate Logical Address")
        self.btnTranslate.clicked.connect(self.translate)
        card_layout.addWidget(self.btnTranslate)

        # Result Banner
        self.lblResult = QLabel("Translation output will appear here.")
        self.lblResult.setObjectName("lblResult")
        self.lblResult.setWordWrap(True)
        card_layout.addWidget(self.lblResult)

        left_col.addWidget(input_card, 2)
        body_layout.addLayout(left_col, 3)

        # Right Column: Physical Memory Stack Visualizer
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Physical Memory Map:"))
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setObjectName("graphView")
        right_col.addWidget(self.view)
        body_layout.addLayout(right_col, 2)

        main_layout.addLayout(body_layout, 1)

        # Footer Back Button
        btnBack = QPushButton("Back to Dashboard")
        btnBack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btnBack.clicked.connect(self.close)
        main_layout.addWidget(btnBack)

    def _load_default_segments(self):
        """Standard operating systems textbook segmentation example."""
        defaults = [
            (0, "Code / Subroutine", 1400, 1000),
            (1, "Main Program", 6300, 400),
            (2, "Stack", 4300, 400),
            (3, "Heap / Data", 3200, 1100),
            (4, "Symbol Table", 4700, 1000),
        ]
        self.tblSegments.blockSignals(True)
        self.tblSegments.setRowCount(len(defaults))
        for r, (seg, name, base, lim) in enumerate(defaults):
            self.tblSegments.setItem(r, 0, QTableWidgetItem(str(seg)))
            self.tblSegments.setItem(r, 1, QTableWidgetItem(name))
            self.tblSegments.setItem(r, 2, QTableWidgetItem(str(base)))
            self.tblSegments.setItem(r, 3, QTableWidgetItem(str(lim)))
        self.tblSegments.blockSignals(False)
        self._draw_memory_bar()

    def _get_segment_dict(self):
        segments = {}
        for r in range(self.tblSegments.rowCount()):
            s_item = self.tblSegments.item(r, 0)
            n_item = self.tblSegments.item(r, 1)
            b_item = self.tblSegments.item(r, 2)
            l_item = self.tblSegments.item(r, 3)
            if not all([s_item, b_item, l_item]):
                continue
            try:
                s = int(s_item.text().strip())
                base = int(b_item.text().strip())
                lim = int(l_item.text().strip())
                name = n_item.text().strip() if n_item else f"Seg {s}"
                segments[s] = {"name": name, "base": base, "limit": lim}
            except ValueError:
                continue
        return segments

    def translate(self):
        try:
            seg_num = int(self.txtSegNum.text().strip())
            offset = int(self.txtOffset.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Segment number and offset must be whole integers.")
            return

        table = self._get_segment_dict()
        res = translate_segment_address(table, seg_num, offset)

        if res["success"]:
            self.lblResult.setStyleSheet(
                "background-color: #EBF8EE; color: #2E6B3E; "
                "border: 1px solid #B6E5C2; border-radius: 8px; padding: 10px; font-weight: 600;"
            )
            self.lblResult.setText(f"✅ {res['message']}")
            self._draw_memory_bar(highlight_addr=res["physical_address"], highlight_seg=seg_num)
        else:
            self.lblResult.setStyleSheet(
                "background-color: #FFF0F0; color: #C43D43; "
                "border: 1px solid #F5B5B7; border-radius: 8px; padding: 10px; font-weight: 600;"
            )
            self.lblResult.setText(f"❌ {res['message']}")
            self._draw_memory_bar(highlight_seg=seg_num, fault=True)

    def _draw_memory_bar(self, highlight_addr=None, highlight_seg=None, fault=False):
        """Draws a vertical memory stack showing where each segment is allocated."""
        self.scene.clear()
        table = self._get_segment_dict()
        if not table:
            return

        max_mem = max(item["base"] + item["limit"] for item in table.values()) + 600
        vw = max(self.view.viewport().width() - 40, 260)
        vh = max(self.view.viewport().height() - 40, 480)
        self.scene.setSceneRect(0, 0, vw, vh)

        bar_x = 55
        bar_w = 110
        scale = (vh - 40) / max_mem if max_mem > 0 else 1.0

        # Draw outer RAM container
        self.scene.addRect(bar_x, 20, bar_w, vh - 40, QPen(QColor("#EABAC9")), QBrush(QColor("#FFFAFC")))

        # Top 0 mark
        t0 = self.scene.addText("0", QFont("Nunito", 8))
        t0.setDefaultTextColor(QColor("#87475D"))
        t0.setPos(20, 10)

        # Draw segment blocks
        for idx, (s, info) in enumerate(table.items()):
            y = 20 + info["base"] * scale
            h = max(info["limit"] * scale, 16)
            color = QColor(SEGMENT_COLORS[idx % len(SEGMENT_COLORS)])

            is_target = (s == highlight_seg)
            border_pen = QPen(QColor("#C45B7A"), 2.5) if is_target else QPen(QColor("#B77C8E"), 1)
            self.scene.addRect(bar_x, y, bar_w, h, border_pen, QBrush(color))

            # Segment label inside block
            txt = self.scene.addText(f"Seg {s}: {info['name']}", QFont("Nunito", 8, QFont.Weight.Bold))
            txt.setDefaultTextColor(QColor("#704653"))
            txt.setPos(bar_x + 4, y + 1)

            # Base address on the left
            base_txt = self.scene.addText(str(info["base"]), QFont("Nunito", 8))
            base_txt.setDefaultTextColor(QColor("#87475D"))
            base_txt.setPos(5, y - 6)

        # Highlight accessed physical address
        if highlight_addr is not None and not fault:
            addr_y = 20 + highlight_addr * scale
            pin_pen = QPen(QColor("#C43D43"), 2)
            self.scene.addLine(bar_x - 15, addr_y, bar_x + bar_w + 15, addr_y, pin_pen)
            p_txt = self.scene.addText(f"▶ PA: {highlight_addr}", QFont("Nunito", 9, QFont.Weight.Bold))
            p_txt.setDefaultTextColor(QColor("#C43D43"))
            p_txt.setPos(bar_x + bar_w + 18, addr_y - 10)

    def _add_row(self):
        r = self.tblSegments.rowCount()
        self.tblSegments.insertRow(r)
        self.tblSegments.setItem(r, 0, QTableWidgetItem(str(r)))
        self.tblSegments.setItem(r, 1, QTableWidgetItem(f"Segment {r}"))
        self.tblSegments.setItem(r, 2, QTableWidgetItem("0"))
        self.tblSegments.setItem(r, 3, QTableWidgetItem("500"))
        self._draw_memory_bar()

    def _remove_row(self):
        curr = self.tblSegments.currentRow()
        if curr >= 0:
            self.tblSegments.removeRow(curr)
            self._draw_memory_bar()

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
            QWidget#cardPanel {
                background-color: #FFFAFC;
                border: 1px solid #EABAC9;
                border-radius: 12px;
            }
            QLabel#lblResult {
                background-color: #FFFFFF;
                color: #704653;
                border: 1px solid #EABAC9;
                border-radius: 8px;
                padding: 10px;
                font-size: 10pt;
            }
            QLineEdit {
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
