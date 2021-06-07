# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/frmPointEditor.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(829, 706)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tblPointEditor = QtWidgets.QTableWidget(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.tblPointEditor.setFont(font)
        self.tblPointEditor.setInputMethodHints(QtCore.Qt.ImhNone)
        self.tblPointEditor.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.tblPointEditor.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.tblPointEditor.setLineWidth(1)
        self.tblPointEditor.setMidLineWidth(0)
        self.tblPointEditor.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tblPointEditor.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tblPointEditor.setAlternatingRowColors(False)
        self.tblPointEditor.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tblPointEditor.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tblPointEditor.setGridStyle(QtCore.Qt.SolidLine)
        self.tblPointEditor.setWordWrap(False)
        self.tblPointEditor.setCornerButtonEnabled(False)
        self.tblPointEditor.setObjectName("tblPointEditor")
        self.tblPointEditor.setColumnCount(3)
        self.tblPointEditor.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblPointEditor.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblPointEditor.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblPointEditor.setHorizontalHeaderItem(2, item)
        self.tblPointEditor.horizontalHeader().setVisible(True)
        self.tblPointEditor.horizontalHeader().setHighlightSections(True)
        self.tblPointEditor.horizontalHeader().setSortIndicatorShown(False)
        self.tblPointEditor.horizontalHeader().setStretchLastSection(True)
        self.tblPointEditor.verticalHeader().setVisible(False)
        self.tblPointEditor.verticalHeader().setHighlightSections(True)
        self.horizontalLayout.addWidget(self.tblPointEditor)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 80, -1, -1)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnAddPoint = QtWidgets.QToolButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAddPoint.sizePolicy().hasHeightForWidth())
        self.btnAddPoint.setSizePolicy(sizePolicy)
        self.btnAddPoint.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btnAddPoint.setFont(font)
        self.btnAddPoint.setObjectName("btnAddPoint")
        self.verticalLayout.addWidget(self.btnAddPoint)
        self.btnRemovePoint = QtWidgets.QToolButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRemovePoint.sizePolicy().hasHeightForWidth())
        self.btnRemovePoint.setSizePolicy(sizePolicy)
        self.btnRemovePoint.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btnRemovePoint.setFont(font)
        self.btnRemovePoint.setObjectName("btnRemovePoint")
        self.verticalLayout.addWidget(self.btnRemovePoint)
        self.btnClearAll = QtWidgets.QToolButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClearAll.sizePolicy().hasHeightForWidth())
        self.btnClearAll.setSizePolicy(sizePolicy)
        self.btnClearAll.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btnClearAll.setFont(font)
        self.btnClearAll.setObjectName("btnClearAll")
        self.verticalLayout.addWidget(self.btnClearAll)
        self.btnLoadPointsFromFile = QtWidgets.QToolButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnLoadPointsFromFile.sizePolicy().hasHeightForWidth())
        self.btnLoadPointsFromFile.setSizePolicy(sizePolicy)
        self.btnLoadPointsFromFile.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btnLoadPointsFromFile.setFont(font)
        self.btnLoadPointsFromFile.setObjectName("btnLoadPointsFromFile")
        self.verticalLayout.addWidget(self.btnLoadPointsFromFile)
        self.btnSavePointsToFile = QtWidgets.QToolButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSavePointsToFile.sizePolicy().hasHeightForWidth())
        self.btnSavePointsToFile.setSizePolicy(sizePolicy)
        self.btnSavePointsToFile.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btnSavePointsToFile.setFont(font)
        self.btnSavePointsToFile.setObjectName("btnSavePointsToFile")
        self.verticalLayout.addWidget(self.btnSavePointsToFile)
        self.cboBase = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboBase.sizePolicy().hasHeightForWidth())
        self.cboBase.setSizePolicy(sizePolicy)
        self.cboBase.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.cboBase.setFont(font)
        self.cboBase.setObjectName("cboBase")
        self.verticalLayout.addWidget(self.cboBase)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.tblPointEditor.setSortingEnabled(False)
        item = self.tblPointEditor.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Name"))
        item = self.tblPointEditor.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Base"))
        item = self.tblPointEditor.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Value"))
        self.btnAddPoint.setText(_translate("Form", "Add Point"))
        self.btnRemovePoint.setText(_translate("Form", "Remove Point"))
        self.btnClearAll.setText(_translate("Form", "Clear All"))
        self.btnLoadPointsFromFile.setText(_translate("Form", "Load Points From File"))
        self.btnSavePointsToFile.setText(_translate("Form", "Save Points To File"))
