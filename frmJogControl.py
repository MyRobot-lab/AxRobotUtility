# -*- coding: utf-8 -*-
import sys, logging
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ui.frmJogControlUi import *

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmJogControl(QWidget, Ui_Form):
    sigJogProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent = None):
        super(frmJogControl, self).__init__(parent)

        # Init normal data
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())
        
        # Init UI components
        self.setupUi(self)
        
        self.cboMode.addItems(["Axis","TCP"])
        self.cboSpeed.addItems(["1","5","10","20","100","200","300"])
        self.cboSpeed.setCurrentText("1")
        self.cboDistance.addItems(["0.1","1","5","10","30","60","90"])
        self.cboDistance.setCurrentText("0.1")

        # Connect signal&slot paire
        self.cboMode.currentTextChanged.connect(self.sltModeClicked)
        self.sigJogProcess.connect(self.MotionCtrl.sltJogProcess)# Establish JogProcess connection
            # For Joint jog
        self.btnJ1Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ2Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ3Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ4Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ5Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ6Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ7Add.clicked.connect(self.sltJointJogClicked)
        self.btnJ1Sub.clicked.connect(self.sltJointJogClicked)
        self.btnJ2Sub.clicked.connect(self.sltJointJogClicked)
        self.btnJ3Sub.clicked.connect(self.sltJointJogClicked)
        self.btnJ4Sub.clicked.connect(self.sltJointJogClicked)
        self.btnJ5Sub.clicked.connect(self.sltJointJogClicked)
        self.btnJ6Sub.clicked.connect(self.sltJointJogClicked)
        self.btnJ7Sub.clicked.connect(self.sltJointJogClicked)

            # For TCP jog
        self.btnTcpXAdd.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpYAdd.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpZAdd.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpRxAdd.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpRyAdd.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpRzAdd.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpXSub.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpYSub.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpZSub.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpRxSub.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpRySub.clicked.connect(self.sltTcpJogClicked)
        self.btnTcpRzSub.clicked.connect(self.sltTcpJogClicked)

    @pyqtSlot(str)
    def sltModeClicked(self, currText):
        if currText == "Axis":
            self.stkwJogControl.setCurrentIndex(0)

        elif currText == "TCP":
            self.stkwJogControl.setCurrentIndex(1)

    @pyqtSlot()
    def sltJointJogClicked(self):
        lstJogOffset = [0]*self.MotionData.AxisNumber
        
        btnName = str(self.sender().objectName())
        for j in range(self.MotionData.AxisNumber):
            if btnName == "btnJ"+str(j+1)+"Add":
                lstJogOffset[j] = float(self.cboDistance.currentText())
            elif btnName == "btnJ"+str(j+1)+"Sub":
                lstJogOffset[j] = -float(self.cboDistance.currentText())

        dctJogCmd = {"Cmd":"Joint", "JogOffset":lstJogOffset, "Speed": int(self.cboSpeed.currentText())}
        self.sigJogProcess.emit(dctJogCmd)
        log.debug("sltJointJogClicked: %s\r\n", str(dctJogCmd))

    @pyqtSlot()
    def sltTcpJogClicked(self):
        lstJogOffset = [0]*self.MotionData.AxisNumber
        
        btnName = str(self.sender().objectName())
        if btnName == "btnTcpXAdd":
            lstJogOffset[0] = float(self.cboDistance.currentText())
        elif btnName == "btnTcpYAdd":
            lstJogOffset[1] = float(self.cboDistance.currentText())
        elif btnName == "btnTcpZAdd":
            lstJogOffset[2] = float(self.cboDistance.currentText())
        elif btnName == "btnTcpRxAdd":
            lstJogOffset[3] = float(self.cboDistance.currentText())
        elif btnName == "btnTcpRyAdd":
            lstJogOffset[4] = float(self.cboDistance.currentText())
        elif btnName == "btnTcpRzAdd":
            lstJogOffset[5] = float(self.cboDistance.currentText())
        if btnName == "btnTcpXSub":
            lstJogOffset[0] = -float(self.cboDistance.currentText())
        elif btnName == "btnTcpYSub":
            lstJogOffset[1] = -float(self.cboDistance.currentText())
        elif btnName == "btnTcpZSub":
            lstJogOffset[2] = -float(self.cboDistance.currentText())
        elif btnName == "btnTcpRxSub":
            lstJogOffset[3] = -float(self.cboDistance.currentText())
        elif btnName == "btnTcpRySub":
            lstJogOffset[4] = -float(self.cboDistance.currentText())
        elif btnName == "btnTcpRzSub":
            lstJogOffset[5] = -float(self.cboDistance.currentText())

        dctJogCmd = {"Cmd":"TCP", "JogOffset":lstJogOffset, "Speed": int(self.cboSpeed.currentText())}
        self.sigJogProcess.emit(dctJogCmd)
        log.debug("sltJointJogClicked: %s\r\n", str(dctJogCmd))

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

#End of Class frmJogControl




