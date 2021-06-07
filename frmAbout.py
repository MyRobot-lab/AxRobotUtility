# -*- coding: utf-8 -*-
# /*
#  *********************************************************************************
#  *     Copyright (c) 2021 ASIX Electronics Corporation All rights reserved.
#  *
#  *     This is unpublished proprietary source code of ASIX Electronics Corporation
#  *
#  *     The copyright notice above does not evidence any actual or intended
#  *     publication of such source code.
#  *********************************************************************************
#  */
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from ui.frmAboutUi import *
from AxRobotData import *

class frmAbout(QWidget,Ui_FormAbout):

    def __init__(self, MotionCtrl):
        super(frmAbout, self).__init__()
        # Init UI components
        self.setupUi(self)

        # Init normal data
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(2)
        self.setWindowIcon(QtGui.QIcon(dctAPP_CFIG["IMG_PATH"]+"asix.ico"))
        self.lbInfoIcon.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"infoIcon.png"))

        self.lbTitle.setText("AxRobot Motion Control Utility")
        strInfo = ""
        strInfo += "Version: {}\r\n".format(dctAPP_CFIG["APP_VER"])
        strInfo += "VCP Identification {}\r\n".format(dctAPP_CFIG["USB_CDC_IDENTIFY"])
        strInfo += "OS: Windows10 x64\r\n"
        # strInfo += "@ 2021 ASIX Electronics Corporation.\r\n"
        # strInfo += "All rights reserved.\r\n\n"
        self.lbInfo.setText(strInfo)

        self.lbAsixLink.setText("ASIX Web: <A href='https://www.asix.com.tw/'>https://www.asix.com.tw/</a>")
        self.lbAsixLink.setOpenExternalLinks(True)


        # Connect signal&slot paire
        self.btnCloseAbout.clicked.connect(self.click)

    def click(self):
        self.close()

#End of Class frmAbout





