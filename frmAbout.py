# -*- coding: utf-8 -*-
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

        # Load icon
        if os.path.isfile(dctAPP_CFIG["ABOUT_ICON"]) == True:
            self.setWindowIcon(QtGui.QIcon(dctAPP_CFIG["ABOUT_ICON"]))

        # Build up information
        self.lbAboutTitle.setText("AxRobot Motion Control Utility")
        strInfo = ""
        strInfo += "Version: {}\r\n".format(dctAPP_CFIG["APP_VER"])
        strInfo += "VCP Identification {}\r\n".format(dctAPP_CFIG["USB_CDC_IDENTIFY"])
        strInfo += "OS: Windows7/10 x64\r\n"
        self.lbInfo.setText(strInfo)

        # Build up hyper link
        self.lbHyperLink_1.setText("{}: <A href='{}'>{}</a>" \
            .format(dctAPP_CFIG["LINK_TITLE_1"], dctAPP_CFIG["HYPER_LINK_1"], dctAPP_CFIG["HYPER_LINK_1"]))
        self.lbHyperLink_1.setOpenExternalLinks(True)

        # Connect signal&slot paire
        self.btnCloseAbout.clicked.connect(self.click)

    def click(self):
        self.close()

#End of Class frmAbout





