# -*- coding: utf-8 -*-
import sys, logging, time
import numpy as np
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QFileInfo, pyqtSlot, pyqtSignal
from ui.frmUpgradeUi import *
from AxRobotData import *

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmUpgrade(QWidget, Ui_Form):
    sigEventHandler = pyqtSignal(dict)
    sigUpgradeProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent=None):
        super(frmUpgrade, self).__init__(parent)

        # Init object point
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())
        
        # Init UI components
        self.setupUi(self)
            # Init firmware target selector
        self.ReloadFirmwareTargetSelector()
            # Init parameter target selector
        self.ReloadParameterTargetSelector()

        # Connect signal&slot paire
            # Internal event handling
        self.sigEventHandler.connect(self.sltEventHandler)
            # Establish UpgradeProcess connection
        self.sigUpgradeProcess.connect(self.MotionCtrl.sltUpgradeProcess)
        self.btnDownloadFirmware.clicked.connect(self.sltPushButtonHandler)
        self.btnBrowseEcatMasterFirmware.clicked.connect(self.sltPushButtonHandler)
        self.btnBrowseServoFirmware.clicked.connect(self.sltPushButtonHandler)
        self.btnDownloadParameter.clicked.connect(self.sltPushButtonHandler)
        self.btnBrowseServoParameter.clicked.connect(self.sltPushButtonHandler)
        self.cboParameterPathSelector.currentTextChanged.connect(self.sltCurrentTextChanged)
        self.leEcatMasterFirmwarePath.editingFinished.connect(self.sltEditingFinished)
        self.leServoFirmwarePath.editingFinished.connect(self.sltEditingFinished)
        self.leServoParameterPath.editingFinished.connect(self.sltEditingFinished)

        # Init GUI status
        self.sigEventHandler.emit({"StatusChange":["Ready"]})

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()
        if btn.objectName() == "btnDownloadFirmware":
            self.sigEventHandler.emit({"DownloadFirmware":[""]})

        elif btn.objectName() == "btnBrowseEcatMasterFirmware":
            self.sigEventHandler.emit({"BrowseEcatMasterFirmware":[""]})

        elif btn.objectName() == "btnBrowseServoFirmware":
            self.sigEventHandler.emit({"BrowseServoFirmware":[""]})

        elif btn.objectName() == "btnDownloadParameter":
            self.sigEventHandler.emit({"DownloadParameter":[""]})

        elif btn.objectName() == "btnBrowseServoParameter":
            self.sigEventHandler.emit({"BrowseServoParameter":[""]})

        elif btn.objectName() == "cboParameterTargetSelector":
            self.sigEventHandler.emit({"ParameterTargetSelector":[""]})

    @pyqtSlot(str)
    def sltCurrentTextChanged(self, currText):
        inst = self.sender()
        log.debug("sltCurrentTextChanged:%s\r\n", inst.objectName())

        if inst.objectName() == "cboParameterPathSelector":
            i = self.cboParameterPathSelector.currentIndex()
            if i < len(dctAPP_CFIG["SERVO_PARAM_PATH"]):
                self.leServoParameterPath.setText(dctAPP_CFIG["SERVO_PARAM_PATH"][i])
                
    @pyqtSlot()
    def sltEditingFinished(self):
        inst = self.sender()

        if inst.objectName() == "leEcatMasterFirmwarePath":
            dctAPP_CFIG["ECAT_MASTER_FW_PATH"] = self.leEcatMasterFirmwarePath.text()
            log.debug("leEcatMasterFirmwarePath:%s\r\n", dctAPP_CFIG["ECAT_MASTER_FW_PATH"])

        elif inst.objectName() == "leServoFirmwarePath":
            dctAPP_CFIG["SERVO_FW_PATH"] = self.leServoFirmwarePath.text()
            log.debug("leServoFirmwarePath:%s\r\n", dctAPP_CFIG["SERVO_FW_PATH"])

        elif inst.objectName() == "leServoParameterPath":
            i = self.cboParameterPathSelector.currentIndex()
            if i < len(dctAPP_CFIG["SERVO_PARAM_PATH"]):
                dctAPP_CFIG["SERVO_PARAM_PATH"][i] = self.leServoParameterPath.text()
                log.debug("leServoParameterPath:%s\r\n", dctAPP_CFIG["SERVO_PARAM_PATH"][i])

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("sltEventHandler:%s, %s\r\n", k, str(v))

            if k == "DownloadFirmware":
                if self.cboFirmwareTargetSelector.currentIndex() <= 1:
                    if self.leEcatMasterFirmwarePath.text() == "":
                        self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Error", "AxRobot Controller firmware path is empty"]})
                        break
                if self.cboFirmwareTargetSelector.currentIndex() > 0:
                    if self.leServoFirmwarePath.text() == "":
                        self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Error", "AxRobot Servo Drive firmware path is empty"]})
                        break
                self.sigUpgradeProcess.emit({"DownloadFirmware": \
                    [self.cboFirmwareTargetSelector.currentIndex(), \
                    self.cboFirmwareTargetSelector.currentText()]})

            elif k == "BrowseEcatMasterFirmware":
                filePath = self.GetPathFromFileBrowser("Select Master Firmware File", \
                                            dctAPP_CFIG["ECAT_MASTER_FW_PATH"], \
                                            "binary file (*.bin)", \
                                            ".bin")
                if filePath != "":
                    self.leEcatMasterFirmwarePath.setText(filePath)
                    dctAPP_CFIG["ECAT_MASTER_FW_PATH"] = filePath
            elif k == "BrowseServoFirmware":
                p = dctAPP_CFIG["SERVO_FW_PATH"].split(".")
                if len(p) > 1:
                    p = p[0]
                filePath = self.GetPathFromFileBrowser("Select Servo Firmware File", \
                                            p, \
                                            "binary file (*.bin)", \
                                            ".bin")
                filePath = filePath.strip(" ")
                if filePath != "":
                    dctAPP_CFIG["SERVO_FW_PATH"] = filePath
                    self.leServoFirmwarePath.setText(filePath)
            elif k == "DownloadParameter":
                self.sigUpgradeProcess.emit({"DownloadParameter": \
                    [self.cboParameterTargetSelector.currentIndex(), \
                    self.cboParameterTargetSelector.currentText()]})
            elif k == "BrowseServoParameter":
                i = self.cboParameterPathSelector.currentIndex()
                p = dctAPP_CFIG["SERVO_PARAM_PATH"][i].split(".")
                if len(p) > 1:
                    p = p[0]
                filePath = self.GetPathFromFileBrowser("Select Servo Parameter File", \
                                            p, \
                                            "servo parameter file (*.txt)", \
                                            ".txt")
                filePath = filePath.strip(" ")
                if filePath != "":
                    dctAPP_CFIG["SERVO_PARAM_PATH"][i] = filePath
                    self.leServoParameterPath.setText(filePath)
            elif k == "ReloadUpgradeTarget":
                self.ReloadFirmwareTargetSelector()
                self.ReloadParameterTargetSelector()
            elif k == "StatusChange":
                self.StatusChange(v[0])

    def GetPathFromFileBrowser(self, title, defPath, extFilter, fileExt):
        filePath = ""# Clear file path
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getOpenFileName(self, title, defPath, extFilter, options=opt)
            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Select file from path:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += fileExt
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", str(e)]})
        finally:
            return filePath

    def ReloadFirmwareTargetSelector(self):
        self.cboFirmwareTargetSelector.clear()
        self.cboFirmwareTargetSelector.addItem("Controller")
        if self.MotionCtrl.StartUp.OnlineServoCount != 0:
            self.cboFirmwareTargetSelector.addItem("Controller + All Servo Drives")
            self.cboFirmwareTargetSelector.addItem("All Servo Drives")
            for i in range(self.MotionCtrl.StartUp.OnlineServoCount):
                self.cboFirmwareTargetSelector.addItem("Servo Drive "+str(i+1))

    def ReloadParameterTargetSelector(self):
        self.cboParameterTargetSelector.clear()
        self.cboParameterPathSelector.clear()
        if self.MotionCtrl.StartUp.OnlineServoCount != 0:
            self.cboParameterTargetSelector.addItem("All Servo Drives")
            for i in range(self.MotionCtrl.StartUp.OnlineServoCount):
                self.cboParameterTargetSelector.addItem("Servo Drive "+str(i+1))
                self.cboParameterPathSelector.addItem("Servo Drive "+str(i+1))

    def StatusChange(self, status):
        if status == "Ready":
            self.btnDownloadFirmware.setEnabled(True)
            self.btnBrowseEcatMasterFirmware.setEnabled(True)
            self.btnBrowseServoFirmware.setEnabled(True)
            if self.MotionCtrl.StartUp.OnlineServoCount == 0:
                self.btnDownloadParameter.setEnabled(False)
            else:
                self.btnDownloadParameter.setEnabled(True)
            self.btnBrowseServoParameter.setEnabled(True)
            self.leEcatMasterFirmwarePath.setText(dctAPP_CFIG["ECAT_MASTER_FW_PATH"])
            self.leServoFirmwarePath.setText(dctAPP_CFIG["SERVO_FW_PATH"])
            self.leServoParameterPath.setText(dctAPP_CFIG["SERVO_PARAM_PATH"] \
                [self.cboParameterPathSelector.currentIndex()])

        elif status == "Upgrading":
            self.btnDownloadFirmware.setEnabled(False)
            self.btnBrowseEcatMasterFirmware.setEnabled(False)
            self.btnBrowseServoFirmware.setEnabled(False)
            self.btnDownloadParameter.setEnabled(False)
            self.btnBrowseServoParameter.setEnabled(False)
#End of Class frmUpgrade




