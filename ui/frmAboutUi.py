# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/frmAbout.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FormAbout(object):
    def setupUi(self, FormAbout):
        FormAbout.setObjectName("FormAbout")
        FormAbout.resize(682, 393)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FormAbout.sizePolicy().hasHeightForWidth())
        FormAbout.setSizePolicy(sizePolicy)
        FormAbout.setMinimumSize(QtCore.QSize(682, 393))
        FormAbout.setMaximumSize(QtCore.QSize(682, 393))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        FormAbout.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(FormAbout)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbAboutTitle = QtWidgets.QLabel(FormAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbAboutTitle.sizePolicy().hasHeightForWidth())
        self.lbAboutTitle.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.lbAboutTitle.setFont(font)
        self.lbAboutTitle.setScaledContents(False)
        self.lbAboutTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.lbAboutTitle.setObjectName("lbAboutTitle")
        self.verticalLayout.addWidget(self.lbAboutTitle)
        self.groupBox = QtWidgets.QGroupBox(FormAbout)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lbInfo = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lbInfo.setFont(font)
        self.lbInfo.setText("")
        self.lbInfo.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbInfo.setObjectName("lbInfo")
        self.verticalLayout_2.addWidget(self.lbInfo)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(FormAbout)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lbHyperLink_1 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lbHyperLink_1.setFont(font)
        self.lbHyperLink_1.setText("")
        self.lbHyperLink_1.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbHyperLink_1.setObjectName("lbHyperLink_1")
        self.verticalLayout_3.addWidget(self.lbHyperLink_1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnCloseAbout = QtWidgets.QPushButton(FormAbout)
        self.btnCloseAbout.setMinimumSize(QtCore.QSize(0, 50))
        self.btnCloseAbout.setObjectName("btnCloseAbout")
        self.horizontalLayout.addWidget(self.btnCloseAbout)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FormAbout)
        QtCore.QMetaObject.connectSlotsByName(FormAbout)

    def retranslateUi(self, FormAbout):
        _translate = QtCore.QCoreApplication.translate
        FormAbout.setWindowTitle(_translate("FormAbout", "About"))
        self.lbAboutTitle.setText(_translate("FormAbout", "About Title"))
        self.groupBox.setTitle(_translate("FormAbout", "Information"))
        self.groupBox_2.setTitle(_translate("FormAbout", "External Link"))
        self.btnCloseAbout.setText(_translate("FormAbout", "OK"))
