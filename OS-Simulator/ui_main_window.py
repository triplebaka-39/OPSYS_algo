# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(488, 467)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"\n"
"/* ===== MAIN WINDOW ===== */\n"
"\n"
"QMainWindow,\n"
"QDialog {\n"
"    background-color: #FFF0F3;\n"
"    color: #704653;\n"
"    font-family: \"Segoe UI\";\n"
"    font-size: 10pt;\n"
"}\n"
"\n"
"/* ===== MAIN CONTENT ===== */\n"
"\n"
"QWidget#centralwidget {\n"
"    background-color: #FFF0F3;\n"
"}\n"
"\n"
"/* ===== HEADINGS ===== */\n"
"\n"
"QLabel {\n"
"    color: #704653;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"QLabel#lblTitle {\n"
"    color: #C45B7A;\n"
"    font-size: 25pt;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QLabel#lblSubtitle {\n"
"    color: #A77987;\n"
"    font-size: 11pt;\n"
"}\n"
"\n"
"/* ===== MODULE BUTTONS ===== */\n"
"\n"
"QPushButton {\n"
"    background-color: #FFDCE6;\n"
"    color: #87475D;\n"
"    border: 2px solid #F3B5C8;\n"
"    border-radius: 14px;\n"
"    padding: 14px;\n"
"    min-height: 48px;\n"
"    font-size: 11pt;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #FFC4D6;\n"
"    border: 2"
                        "px solid #E994B1;\n"
"    color: #78364D;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #F2A9C0;\n"
"    border: 2px solid #DF87A6;\n"
"    padding-top: 16px;\n"
"}\n"
"\n"
"/* ===== INPUT FIELDS ===== */\n"
"\n"
"QLineEdit,\n"
"QSpinBox,\n"
"QDoubleSpinBox,\n"
"QComboBox,\n"
"QTextEdit,\n"
"QPlainTextEdit {\n"
"    background-color: #FFFAFC;\n"
"    color: #704653;\n"
"    border: 1px solid #EABAC9;\n"
"    border-radius: 8px;\n"
"    padding: 7px;\n"
"    selection-background-color: #ECA3BB;\n"
"}\n"
"\n"
"/* ===== TABLES ===== */\n"
"\n"
"QTableWidget,\n"
"QTableView {\n"
"    background-color: #FFFAFC;\n"
"    alternate-background-color: #FFF0F4;\n"
"    color: #704653;\n"
"    gridline-color: #F0C6D3;\n"
"    border: 1px solid #EABAC9;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background-color: #F8D4E0;\n"
"    color: #784254;\n"
"    padding: 8px;\n"
"    border: none;\n"
"    font-weight: bold;\n"
"}\n"
"")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 0, 461, 411))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.lblTitle = QLabel(self.verticalLayoutWidget)
        self.lblTitle.setObjectName(u"lblTitle")

        self.verticalLayout.addWidget(self.lblTitle)

        self.lblSubtitle = QLabel(self.verticalLayoutWidget)
        self.lblSubtitle.setObjectName(u"lblSubtitle")

        self.verticalLayout.addWidget(self.lblSubtitle)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.btnPaging = QPushButton(self.verticalLayoutWidget)
        self.btnPaging.setObjectName(u"btnPaging")

        self.gridLayout.addWidget(self.btnPaging, 1, 0, 1, 1)

        self.btnPageReplacement = QPushButton(self.verticalLayoutWidget)
        self.btnPageReplacement.setObjectName(u"btnPageReplacement")

        self.gridLayout.addWidget(self.btnPageReplacement, 1, 1, 1, 1)

        self.btnBankers = QPushButton(self.verticalLayoutWidget)
        self.btnBankers.setObjectName(u"btnBankers")

        self.gridLayout.addWidget(self.btnBankers, 0, 1, 1, 1)

        self.btnSegmentation = QPushButton(self.verticalLayoutWidget)
        self.btnSegmentation.setObjectName(u"btnSegmentation")

        self.gridLayout.addWidget(self.btnSegmentation, 2, 0, 1, 1)

        self.btnCpuScheduling = QPushButton(self.verticalLayoutWidget)
        self.btnCpuScheduling.setObjectName(u"btnCpuScheduling")

        self.gridLayout.addWidget(self.btnCpuScheduling, 0, 0, 1, 1)

        self.btnFragmentation = QPushButton(self.verticalLayoutWidget)
        self.btnFragmentation.setObjectName(u"btnFragmentation")

        self.gridLayout.addWidget(self.btnFragmentation, 2, 1, 1, 1)

        self.btnDiskScheduling = QPushButton(self.verticalLayoutWidget)
        self.btnDiskScheduling.setObjectName(u"btnDiskScheduling")

        self.gridLayout.addWidget(self.btnDiskScheduling, 3, 0, 1, 1)

        self.btnMultiprogramming = QPushButton(self.verticalLayoutWidget)
        self.btnMultiprogramming.setObjectName(u"btnMultiprogramming")

        self.gridLayout.addWidget(self.btnMultiprogramming, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lblTitle.setText(QCoreApplication.translate("MainWindow", u"OS Simulator", None))
        self.lblSubtitle.setText(QCoreApplication.translate("MainWindow", u"Operating Systems Learning Lab", None))
        self.btnPaging.setText(QCoreApplication.translate("MainWindow", u"Paging", None))
        self.btnPageReplacement.setText(QCoreApplication.translate("MainWindow", u"Page Replacement", None))
        self.btnBankers.setText(QCoreApplication.translate("MainWindow", u"Banker's Algorithm", None))
        self.btnSegmentation.setText(QCoreApplication.translate("MainWindow", u"Segmentation", None))
        self.btnCpuScheduling.setText(QCoreApplication.translate("MainWindow", u"CPU Scheduling", None))
        self.btnFragmentation.setText(QCoreApplication.translate("MainWindow", u"Fragmentation", None))
        self.btnDiskScheduling.setText(QCoreApplication.translate("MainWindow", u"Disk Scheduling", None))
        self.btnMultiprogramming.setText(QCoreApplication.translate("MainWindow", u"Multiprogramming", None))
    # retranslateUi

