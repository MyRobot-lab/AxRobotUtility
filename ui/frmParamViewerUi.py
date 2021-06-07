# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/frmParamViewer.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        Form.resize(831, 724)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tbwParamEditor = QtWidgets.QTabWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbwParamEditor.sizePolicy().hasHeightForWidth())
        self.tbwParamEditor.setSizePolicy(sizePolicy)
        self.tbwParamEditor.setMinimumSize(QtCore.QSize(0, 0))
        self.tbwParamEditor.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.tbwParamEditor.setFont(font)
        self.tbwParamEditor.setAcceptDrops(False)
        self.tbwParamEditor.setDocumentMode(False)
        self.tbwParamEditor.setObjectName("tbwParamEditor")
        self.MotionControl = QtWidgets.QWidget()
        self.MotionControl.setObjectName("MotionControl")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.MotionControl)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.trvMotionParam = QtWidgets.QTreeWidget(self.MotionControl)
        self.trvMotionParam.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.trvMotionParam.sizePolicy().hasHeightForWidth())
        self.trvMotionParam.setSizePolicy(sizePolicy)
        self.trvMotionParam.setMinimumSize(QtCore.QSize(0, 0))
        self.trvMotionParam.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.trvMotionParam.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.trvMotionParam.setAutoScroll(True)
        self.trvMotionParam.setObjectName("trvMotionParam")
        self.horizontalLayout_2.addWidget(self.trvMotionParam)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 80, -1, -1)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnUploadMotionParam = QtWidgets.QPushButton(self.MotionControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnUploadMotionParam.sizePolicy().hasHeightForWidth())
        self.btnUploadMotionParam.setSizePolicy(sizePolicy)
        self.btnUploadMotionParam.setMinimumSize(QtCore.QSize(0, 45))
        self.btnUploadMotionParam.setObjectName("btnUploadMotionParam")
        self.verticalLayout.addWidget(self.btnUploadMotionParam)
        self.btnSaveAsMotionReportFile = QtWidgets.QPushButton(self.MotionControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSaveAsMotionReportFile.sizePolicy().hasHeightForWidth())
        self.btnSaveAsMotionReportFile.setSizePolicy(sizePolicy)
        self.btnSaveAsMotionReportFile.setMinimumSize(QtCore.QSize(0, 45))
        self.btnSaveAsMotionReportFile.setObjectName("btnSaveAsMotionReportFile")
        self.verticalLayout.addWidget(self.btnSaveAsMotionReportFile)
        self.btnExpandCollapseAllMotionParam = QtWidgets.QPushButton(self.MotionControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExpandCollapseAllMotionParam.sizePolicy().hasHeightForWidth())
        self.btnExpandCollapseAllMotionParam.setSizePolicy(sizePolicy)
        self.btnExpandCollapseAllMotionParam.setMinimumSize(QtCore.QSize(0, 45))
        self.btnExpandCollapseAllMotionParam.setObjectName("btnExpandCollapseAllMotionParam")
        self.verticalLayout.addWidget(self.btnExpandCollapseAllMotionParam)
        spacerItem = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.tbwParamEditor.addTab(self.MotionControl, "")
        self.ServoDrive = QtWidgets.QWidget()
        self.ServoDrive.setObjectName("ServoDrive")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.ServoDrive)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.trvServoParam = QtWidgets.QTreeWidget(self.ServoDrive)
        self.trvServoParam.setMinimumSize(QtCore.QSize(0, 0))
        self.trvServoParam.setObjectName("trvServoParam")
        self.horizontalLayout_3.addWidget(self.trvServoParam)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 80, -1, -1)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btnUploadServoParam = QtWidgets.QPushButton(self.ServoDrive)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnUploadServoParam.sizePolicy().hasHeightForWidth())
        self.btnUploadServoParam.setSizePolicy(sizePolicy)
        self.btnUploadServoParam.setMinimumSize(QtCore.QSize(0, 45))
        self.btnUploadServoParam.setObjectName("btnUploadServoParam")
        self.verticalLayout_2.addWidget(self.btnUploadServoParam)
        self.btnSaveAsServoReportFile = QtWidgets.QPushButton(self.ServoDrive)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSaveAsServoReportFile.sizePolicy().hasHeightForWidth())
        self.btnSaveAsServoReportFile.setSizePolicy(sizePolicy)
        self.btnSaveAsServoReportFile.setMinimumSize(QtCore.QSize(0, 45))
        self.btnSaveAsServoReportFile.setObjectName("btnSaveAsServoReportFile")
        self.verticalLayout_2.addWidget(self.btnSaveAsServoReportFile)
        self.btnSaveAsServoConfigFile = QtWidgets.QPushButton(self.ServoDrive)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSaveAsServoConfigFile.sizePolicy().hasHeightForWidth())
        self.btnSaveAsServoConfigFile.setSizePolicy(sizePolicy)
        self.btnSaveAsServoConfigFile.setMinimumSize(QtCore.QSize(0, 45))
        self.btnSaveAsServoConfigFile.setObjectName("btnSaveAsServoConfigFile")
        self.verticalLayout_2.addWidget(self.btnSaveAsServoConfigFile)
        self.btnExpandCollapseAllServoParam = QtWidgets.QPushButton(self.ServoDrive)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExpandCollapseAllServoParam.sizePolicy().hasHeightForWidth())
        self.btnExpandCollapseAllServoParam.setSizePolicy(sizePolicy)
        self.btnExpandCollapseAllServoParam.setMinimumSize(QtCore.QSize(0, 45))
        self.btnExpandCollapseAllServoParam.setObjectName("btnExpandCollapseAllServoParam")
        self.verticalLayout_2.addWidget(self.btnExpandCollapseAllServoParam)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.tbwParamEditor.addTab(self.ServoDrive, "")
        self.horizontalLayout.addWidget(self.tbwParamEditor)

        self.retranslateUi(Form)
        self.tbwParamEditor.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Parameter Viewer"))
        self.trvMotionParam.headerItem().setText(0, _translate("Form", "Index"))
        self.trvMotionParam.headerItem().setText(1, _translate("Form", "Name"))
        self.trvMotionParam.headerItem().setText(2, _translate("Form", "Value"))
        self.trvMotionParam.headerItem().setText(3, _translate("Form", "Unit"))
        self.trvMotionParam.headerItem().setText(4, _translate("Form", "Flag"))
        self.btnUploadMotionParam.setText(_translate("Form", "Upload"))
        self.btnSaveAsMotionReportFile.setText(_translate("Form", "Save as Report File"))
        self.btnExpandCollapseAllMotionParam.setText(_translate("Form", "Expand All"))
        self.tbwParamEditor.setTabText(self.tbwParamEditor.indexOf(self.MotionControl), _translate("Form", "MotionControl"))
        self.trvServoParam.headerItem().setText(0, _translate("Form", "Index"))
        self.trvServoParam.headerItem().setText(1, _translate("Form", "Name"))
        self.trvServoParam.headerItem().setText(2, _translate("Form", "Value"))
        self.trvServoParam.headerItem().setText(3, _translate("Form", "Unit"))
        self.trvServoParam.headerItem().setText(4, _translate("Form", "Flag"))
        self.btnUploadServoParam.setText(_translate("Form", "Upload"))
        self.btnSaveAsServoReportFile.setText(_translate("Form", "Save as Report File"))
        self.btnSaveAsServoConfigFile.setText(_translate("Form", "Save as Config. File"))
        self.btnExpandCollapseAllServoParam.setText(_translate("Form", "Expand All"))
        self.tbwParamEditor.setTabText(self.tbwParamEditor.indexOf(self.ServoDrive), _translate("Form", "ServoDrive"))
