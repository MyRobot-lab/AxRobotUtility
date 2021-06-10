# -*- coding: utf-8 -*-
import sys, logging
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ui.frmInformationUi import *

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmInformation(QWidget, Ui_Form):
    sigInformationProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent=None):
        super(frmInformation, self).__init__(parent)

        # Init object point
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData
        
        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())
        
        # Init UI components
        self.setupUi(self)

        # Connect signal&slot paire
        self.sigInformationProcess.connect(self.MotionCtrl.sltInformationProcess)# Establish InformationProcess connection

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))


#End of Class frmUpgrade




