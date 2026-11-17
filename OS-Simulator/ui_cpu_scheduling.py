# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cpu_scheduling.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGraphicsView,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(900, 820)
        Dialog.setStyleSheet(u"\n"
"QDialog { background-color: #FFF0F3; color: #704653; font-family: \"Nunito\"; font-size: 10pt; }\n"
"QWidget { font-family: \"Nunito\"; }\n"
"QLabel { color: #704653; background: transparent; font-size: 10pt; }\n"
"QLabel#lblTitle { color: #C45B7A; font-size: 24pt; font-weight: 700; }\n"
"QLabel#lblInput, QLabel#lblResults, QLabel#lblGantt { color: #C45B7A; font-size: 13pt; font-weight: 700; }\n"
"QPushButton { background-color: #FFDCE6; color: #87475D; border: 1px solid #F3B5C8; border-radius: 9px; padding: 8px; font-size: 10pt; font-weight: 600; }\n"
"QPushButton:hover { background-color: #FFC4D6; }\n"
"QPushButton:pressed { background-color: #F2A9C0; }\n"
"QTableWidget { background-color: #FFFAFC; alternate-background-color: #FFF0F4; color: #704653; gridline-color: #F0C6D3; border: 1px solid #EABAC9; border-radius: 8px; font-size: 10pt; }\n"
"QHeaderView::section { background-color: #F8D4E0; color: #784254; padding: 7px; border: none; font-size: 10pt; font-weight: 700; }\n"
"QComboBox, QSpinBox { backg"
                        "round-color: #FFFAFC; color: #704653; border: 1px solid #EABAC9; border-radius: 8px; padding: 6px; font-size: 10pt; }\n"
"QComboBox QAbstractItemView { background-color: #FFFAFC; color: #704653; selection-background-color: #F2A9C0; selection-color: #704653; outline: 0; }\n"
"QComboBox QAbstractItemView::item { color: #704653; min-height: 28px; padding: 5px; }\n"
"   ")
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.algorithmLayout = QHBoxLayout()
        self.algorithmLayout.setObjectName(u"algorithmLayout")
        self.lblTitle = QLabel(Dialog)
        self.lblTitle.setObjectName(u"lblTitle")

        self.algorithmLayout.addWidget(self.lblTitle)

        self.cmbAlgorithm = QComboBox(Dialog)
        self.cmbAlgorithm.setObjectName(u"cmbAlgorithm")

        self.algorithmLayout.addWidget(self.cmbAlgorithm)

        self.lblQuantum = QLabel(Dialog)
        self.lblQuantum.setObjectName(u"lblQuantum")

        self.algorithmLayout.addWidget(self.lblQuantum)

        self.spinQuantum = QSpinBox(Dialog)
        self.spinQuantum.setObjectName(u"spinQuantum")
        self.spinQuantum.setMinimum(1)
        self.spinQuantum.setMaximum(1000000)
        self.spinQuantum.setValue(2)

        self.algorithmLayout.addWidget(self.spinQuantum)


        self.verticalLayout.addLayout(self.algorithmLayout)

        self.lblInput = QLabel(Dialog)
        self.lblInput.setObjectName(u"lblInput")

        self.verticalLayout.addWidget(self.lblInput)

        self.tblInput = QTableWidget(Dialog)
        if (self.tblInput.columnCount() < 4):
            self.tblInput.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tblInput.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tblInput.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tblInput.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tblInput.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tblInput.setObjectName(u"tblInput")
        self.tblInput.setMinimumSize(QSize(0, 120))
        self.tblInput.setColumnCount(4)

        self.verticalLayout.addWidget(self.tblInput)

        self.processButtons = QHBoxLayout()
        self.processButtons.setObjectName(u"processButtons")
        self.btnAddProcess = QPushButton(Dialog)
        self.btnAddProcess.setObjectName(u"btnAddProcess")

        self.processButtons.addWidget(self.btnAddProcess)

        self.btnRemoveProcess = QPushButton(Dialog)
        self.btnRemoveProcess.setObjectName(u"btnRemoveProcess")

        self.processButtons.addWidget(self.btnRemoveProcess)


        self.verticalLayout.addLayout(self.processButtons)

        self.simulationButtons = QHBoxLayout()
        self.simulationButtons.setObjectName(u"simulationButtons")
        self.btnCalculate = QPushButton(Dialog)
        self.btnCalculate.setObjectName(u"btnCalculate")

        self.simulationButtons.addWidget(self.btnCalculate)

        self.btnStepByStep = QPushButton(Dialog)
        self.btnStepByStep.setObjectName(u"btnStepByStep")

        self.simulationButtons.addWidget(self.btnStepByStep)

        self.btnReset = QPushButton(Dialog)
        self.btnReset.setObjectName(u"btnReset")

        self.simulationButtons.addWidget(self.btnReset)

        self.btnClearAll = QPushButton(Dialog)
        self.btnClearAll.setObjectName(u"btnClearAll")

        self.simulationButtons.addWidget(self.btnClearAll)


        self.verticalLayout.addLayout(self.simulationButtons)

        self.lblResults = QLabel(Dialog)
        self.lblResults.setObjectName(u"lblResults")

        self.verticalLayout.addWidget(self.lblResults)

        self.tblResults = QTableWidget(Dialog)
        if (self.tblResults.columnCount() < 8):
            self.tblResults.setColumnCount(8)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(4, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(5, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(6, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tblResults.setHorizontalHeaderItem(7, __qtablewidgetitem11)
        self.tblResults.setObjectName(u"tblResults")
        self.tblResults.setMinimumSize(QSize(0, 120))
        self.tblResults.setColumnCount(8)

        self.verticalLayout.addWidget(self.tblResults)

        self.averagesLayout = QHBoxLayout()
        self.averagesLayout.setObjectName(u"averagesLayout")
        self.lblAvgWaiting = QLabel(Dialog)
        self.lblAvgWaiting.setObjectName(u"lblAvgWaiting")

        self.averagesLayout.addWidget(self.lblAvgWaiting)

        self.lblAvgTurnaround = QLabel(Dialog)
        self.lblAvgTurnaround.setObjectName(u"lblAvgTurnaround")

        self.averagesLayout.addWidget(self.lblAvgTurnaround)


        self.verticalLayout.addLayout(self.averagesLayout)

        self.lblGantt = QLabel(Dialog)
        self.lblGantt.setObjectName(u"lblGantt")

        self.verticalLayout.addWidget(self.lblGantt)

        self.ganttView = QGraphicsView(Dialog)
        self.ganttView.setObjectName(u"ganttView")
        self.ganttView.setMinimumSize(QSize(0, 125))
        self.ganttView.setMaximumHeight(180)
        self.ganttView.setStyleSheet(u"QGraphicsView { background-color: #FFFAFC; border: 1px solid #EABAC9; border-radius: 8px; }")

        self.verticalLayout.addWidget(self.ganttView)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"CPU Scheduling", None))
        self.lblTitle.setText(QCoreApplication.translate("Dialog", u"CPU Scheduling", None))
        self.lblQuantum.setText(QCoreApplication.translate("Dialog", u"Quantum:", None))
        self.lblInput.setText(QCoreApplication.translate("Dialog", u"Process Input", None))
        ___qtablewidgetitem = self.tblInput.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog", u"Process ID", None))
        ___qtablewidgetitem1 = self.tblInput.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"Arrival Time", None))
        ___qtablewidgetitem2 = self.tblInput.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"Burst Time", None))
        ___qtablewidgetitem3 = self.tblInput.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"Priority (lower = higher)", None))
        self.btnAddProcess.setText(QCoreApplication.translate("Dialog", u"Add Process", None))
        self.btnRemoveProcess.setText(QCoreApplication.translate("Dialog", u"Remove Process", None))
        self.btnCalculate.setText(QCoreApplication.translate("Dialog", u"Run Simulation", None))
        self.btnStepByStep.setText(QCoreApplication.translate("Dialog", u"Step-by-Step", None))
        self.btnReset.setText(QCoreApplication.translate("Dialog", u"Reset", None))
        self.btnClearAll.setText(QCoreApplication.translate("Dialog", u"Clear All", None))
        self.lblResults.setText(QCoreApplication.translate("Dialog", u"Scheduling Results", None))
        ___qtablewidgetitem4 = self.tblResults.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog", u"Process ID", None))
        ___qtablewidgetitem5 = self.tblResults.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dialog", u"Arrival", None))
        ___qtablewidgetitem6 = self.tblResults.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Dialog", u"Burst", None))
        ___qtablewidgetitem7 = self.tblResults.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Dialog", u"Priority", None))
        ___qtablewidgetitem8 = self.tblResults.horizontalHeaderItem(4)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Dialog", u"First Start", None))
        ___qtablewidgetitem9 = self.tblResults.horizontalHeaderItem(5)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Dialog", u"Finish", None))
        ___qtablewidgetitem10 = self.tblResults.horizontalHeaderItem(6)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dialog", u"Waiting", None))
        ___qtablewidgetitem11 = self.tblResults.horizontalHeaderItem(7)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dialog", u"Turnaround", None))
        self.lblAvgWaiting.setText(QCoreApplication.translate("Dialog", u"Average Waiting Time: \u2014", None))
        self.lblAvgTurnaround.setText(QCoreApplication.translate("Dialog", u"Average Turnaround Time: \u2014", None))
        self.lblGantt.setText(QCoreApplication.translate("Dialog", u"Gantt Chart \u2014 Execution Order", None))
    # retranslateUi

