# -*- coding: utf-8 -*-
import sys, logging, serial, serial.tools.list_ports, time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread, QObject, pyqtSlot, pyqtSignal, QTimer, Qt
from ui.frmStartUpUi import *
from AxRobotData import *
import escMotion

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmStartUp(QWidget, Ui_Form):
    sigEventHandler = pyqtSignal(dict)
    sigStartUpProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent=None):
        super(frmStartUp, self).__init__(parent)

        # Init normal data
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData
        self.FoundPortCount = 0
        self.ConnectedPortName = ""
        self.OnlineDeviceCount = 0
        self.OnlineServoCount = 0
        self.ConnectStartTime = None

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())

        # Init UI components
        self.setupUi(self)

        self.ckbSimuEnable.setChecked(True)
        self.ckbCreate3dModel.setChecked(True)
        self.ckbEnbExtForceMode.setChecked(False)
        self.cboJ3AngLimitation.addItems(["No Limit","30","60","90"])
        self.cboJ3AngLimitation.setCurrentIndex(0)

        # Connect signal&slot paire
        self.btnCommControl.clicked.connect(self.sltPushButtonHandler)
        self.btnServoControl.clicked.connect(self.sltPushButtonHandler)
        # self.cboSerialPortSelector.activated[str].connect(lambda s,v=1 :self.cboActivated(s,v))
        self.sigEventHandler.connect(self.sltEventHandler)# Internal event process connection
        self.sigStartUpProcess.connect(self.MotionCtrl.sltStartUpProcess)# Establish StartUpProcess connection

        # self.sigToThrdEventHandler.connect(self.ethercatObj.sltEventHandler)

        self.sigEventHandler.emit({"StatusChange":[""]})

    def ReloadSerialPorts(self, strVID_PID):# Example: "VID:PID=0416:B002"
        # Clear serial port list
        self.cboSerialPortSelector.clear()
        self.FoundPortCount = 0

        # Find out all serial ports with specified VID:PID
        for sp in serial.tools.list_ports.comports():
            log.debug("device=%s, name=%s, hwid=%s\r\n", \
            sp.device, \
            sp.name, \
            sp.hwid)

            if (sp.hwid.find(strVID_PID)>=0 and sp.hwid.find("SER=M")>=0):# Check VID&PID&SerialNumber prefix
                self.cboSerialPortSelector.addItem(sp.device)
                self.FoundPortCount += 1

        # Change button status
        log.debug("Searched ports=%d\r\n", self.FoundPortCount)
        if self.cboSerialPortSelector.count() == 0:
            self.cboSerialPortSelector.addItem("No ports available")

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()
        if self.MotionData.SystemState >= dctSYSTEM_STATE["SERVO_ON"]:
            if btn.objectName() == "btnCommControl":
                self.sigEventHandler.emit({"ServoOff":[""]})  
                self.sigEventHandler.emit({"Disconnect":[""]})
            elif btn.objectName() == "btnServoControl":
                self.sigEventHandler.emit({"ServoOff":[""]})
        elif self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
            if btn.objectName() == "btnCommControl":
                self.sigEventHandler.emit({"Disconnect":[""]})
            elif btn.objectName() == "btnServoControl":
                self.sigEventHandler.emit({"ServoOn":[""]})
        else:
            if btn.objectName() == "btnCommControl":
                self.sigEventHandler.emit({"Connect":[""]})

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

            if k == "Connect" or k == "Reconnect":
                import AxRobotData
                AxRobotData.SimulationModeEnabled = self.ckbSimuEnable.isChecked()
                self.sigStartUpProcess.emit({k:[self.cboSerialPortSelector.currentText(), \
                                                self.MotionCtrl.MotionMonitor.TimeTaskState >= 0, \
                                                AxRobotData.SimulationModeEnabled]})
            elif k == "ServoOn":
                import AxRobotData
                if self.cboJ3AngLimitation.currentText().isnumeric() == True:
                    AxRobotData.Joint3AngLimit = int(self.cboJ3AngLimitation.currentText())
                else:
                    AxRobotData.Joint3AngLimit = 0
                log.debug("Set Joint3AngLimit=%d\r\n", AxRobotData.Joint3AngLimit)
                self.sigStartUpProcess.emit({k:[self.ckbCreate3dModel.isChecked(), self.ckbEnbExtForceMode.isChecked()]})                               
            elif k == "Disconnect" or k == "ServoOff":
                self.sigStartUpProcess.emit({k:""})
            elif k == "ReloadSerialPort":
                self.ReloadSerialPorts(dctAPP_CFIG["USB_CDC_IDENTIFY"])
                self.StatusChange(self.MotionData.SystemState)
            elif k == "StatusChange":
                self.StatusChange(self.MotionData.SystemState)

    def StatusChange(self, status):
        log.debug("StatusChange: %d\r\n", status)
        if status >= dctSYSTEM_STATE["SERVO_ON"]:
            self.ckbSimuEnable.setEnabled(False)
            self.cboSerialPortSelector.setEnabled(False)
            self.btnCommControl.setEnabled(False)

            self.ckbCreate3dModel.setEnabled(False)
            self.ckbEnbExtForceMode.setEnabled(False)
            self.cboJ3AngLimitation.setEnabled(False)
            self.btnServoControl.setEnabled(True)
            self.btnServoControl.setText("ServoOff")


        elif status >= dctSYSTEM_STATE["CONNECTED"]:
            self.ckbSimuEnable.setEnabled(False)
            self.cboSerialPortSelector.setEnabled(False)
            self.btnCommControl.setEnabled(True)
            self.btnCommControl.setText("Disconnect")

            self.ckbCreate3dModel.setEnabled(True)
            self.ckbEnbExtForceMode.setEnabled(True)
            self.cboJ3AngLimitation.setEnabled(True)
            self.btnServoControl.setEnabled(True)
            self.btnServoControl.setText("ServoOn")

        else:
            self.ckbSimuEnable.setEnabled(True)
            self.cboSerialPortSelector.setEnabled(True)
            if self.FoundPortCount == 0:
                self.btnCommControl.setEnabled(False)
            else:
                self.btnCommControl.setEnabled(True)
            self.btnCommControl.setText("Connect")


            self.ckbCreate3dModel.setEnabled(False)
            self.ckbEnbExtForceMode.setEnabled(False)
            self.cboJ3AngLimitation.setEnabled(False)
            self.btnServoControl.setEnabled(False)
            self.btnServoControl.setText("ServoOn")

#End of Class frmStartUp





