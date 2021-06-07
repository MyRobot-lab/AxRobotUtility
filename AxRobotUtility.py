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
import os, sys, time, copy, logging, json, datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot, Qt, QSize, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMessageBox, QLabel, QFrame, QProgressDialog
from PyQt5.QtGui import QIcon
from ui.AxRobotUtilityUi import *
# Create motion data object
from MotionFunction import *
from simu.Robot3dModel import Robot3dModel
from frmStartUp import frmStartUp
from frmParamViewer import frmParamViewer
from frmJogControl import frmJogControl
from frmPointEditor import frmPointEditor
from frmScriptEditor import frmScriptEditor
from frmMotionTuner import frmMotionTuner
from frmUpgrade import frmUpgrade
from frmInformation import frmInformation
from Monitor import MotionMonitor
from frmAbout import frmAbout

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

DEF_APP_CFIG_FILE_PATH = "./def.appcfg"

# Fixed monitor resolution issue
if hasattr(Qt, 'AA_DisableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# /*
#  * ----------------------------------------------------------------------------
#  * Function Name: Main()
#  * Purpose: AxRobot Utility Program Entry
#  * Note:	
#  * ----------------------------------------------------------------------------
#  */
class Main(QMainWindow, Ui_MainWindow, QWidget):
    sigEventHandler = pyqtSignal(dict)

    def __init__(self,parent=None):
        super(Main,self).__init__(parent)

        # Init normal data
        self.QuitRequest = 0

        # Init main form UI
        self.setupUi(self)
            # Prepare progress dialog
        self.ProgressBox = QProgressDialog("", "", 0, 100, self)
        self.ProgressBox.setWindowModality(Qt.WindowModal)
        self.ProgressBox.setAutoReset(True)
        self.ProgressBox.setAutoClose(True)
        self.ProgressBox.setMinimum(0)
        self.ProgressBox.setMaximum(100)
        self.ProgressBox.setValue(0)
        self.ProgressBox.setMinimumWidth(400)
        self.ProgressBox.setMinimumHeight(100)
        self.ProgressBox.setWindowFlags(self.ProgressBox.windowFlags()|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
        self.ProgressBox.setCancelButton(None)#Remove cancel button
        self.ProgressBox.setStyleSheet("background-color: rgb(126,202,242);")
        self.ProgressBox.show()
        self.ProgressBox.hide()
            # Init status bar
        qs = QSize()
        qs.setHeight(30)
        qs.setWidth(150)
        self.lbConnStatus = QLabel("")
        self.lbConnStatus.setMinimumSize(qs)
        self.sbMainWin.addPermanentWidget(QLabel("Connection Status: "))
        self.sbMainWin.addPermanentWidget(self.lbConnStatus)
        qs.setWidth(150)
        self.lbConnTime = QLabel("")
        self.lbConnTime.setMinimumSize(qs)
        self.sbMainWin.addPermanentWidget(QLabel("Connection Time: "))
        self.sbMainWin.addPermanentWidget(self.lbConnTime)
        qs.setWidth(100)
        self.lbOnlineDevices = QLabel("")
        self.lbOnlineDevices.setMinimumSize(qs)
        self.sbMainWin.addPermanentWidget(QLabel("Online Servos/Devices: "))
        self.sbMainWin.addPermanentWidget(self.lbOnlineDevices)
        qs.setWidth(70)
        self.lbServoStatus = QLabel("")
        self.lbServoStatus.setMinimumSize(qs)
        self.sbMainWin.addPermanentWidget(QLabel("Servo Status: "))
        self.sbMainWin.addPermanentWidget(self.lbServoStatus)
        qs.setWidth(70)
        self.lbExtForceStatus = QLabel("")
        self.lbExtForceStatus.setMinimumSize(qs)
        self.sbMainWin.addPermanentWidget(QLabel("extForce Status: "))
        self.sbMainWin.addPermanentWidget(self.lbExtForceStatus)

        # Start motion controller as thread
        self.MotionData = MotionData()
        self.MotionCtrl = MotionCtrl(self.MotionData)
        self.MotionCtrlThread = QThread()
        self.MotionCtrl.moveToThread(self.MotionCtrlThread)
        self.MotionCtrlThread.start()
        self.MotionCtrl.sigMainWinEventHandler.connect(self.sltEventHandler)

        # Start motion monitor as thread
        self.MotionMonitor = MotionMonitor(self.MotionCtrl)
        self.MotionMonitorThread = QThread()
        self.MotionMonitor.moveToThread(self.MotionMonitorThread)
        self.MotionMonitorThread.start()
        self.MotionMonitor.sigMainWinEventHandler.connect(self.sltEventHandler)
        self.MotionCtrl.BindMotionMonitor(self.MotionMonitor)

        # Init 3D-Modle viewer
        self.Modle3dViewer = Robot3dModel()
        self.tabWidget.addTab(self.Modle3dViewer.canva, "3D Robot Monitor")
        self.tabWidget.removeTab(0)
        self.show()
        self.Modle3dViewer.arm_init()
        self.Modle3dViewer.sigMainWinEventHandler.connect(self.sltEventHandler)
        self.MotionMonitor.BindModle3dViewer(self.Modle3dViewer)

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())

        # Load application configuration
        self.LoadAppConfig(DEF_APP_CFIG_FILE_PATH)
            # Set main window title
        self.setWindowTitle(dctAPP_CFIG["APP_NAME"]+"_"+dctAPP_CFIG["APP_VER"])

        # Init function selector
            # StartUp page
        self.StartUp = frmStartUp(self.MotionCtrl)
        self.MotionCtrl.BindStartUp(self.StartUp)
        self.stkwFunctionArea.addWidget(self.StartUp)
            # Load parameter viewer page
        self.ParamViewer = frmParamViewer(self.MotionCtrl)
        self.MotionCtrl.BindParamViewer(self.ParamViewer)
        self.stkwFunctionArea.addWidget(self.ParamViewer)
            # Load jog control page
        self.JogControl = frmJogControl(self.MotionCtrl)
        self.MotionCtrl.BindJogControl(self.JogControl)
        self.stkwFunctionArea.addWidget(self.JogControl)
            # Load point editor page
        self.PointEditor = frmPointEditor(self.MotionCtrl)
        self.MotionCtrl.BindPointEditor(self.PointEditor)
        self.stkwFunctionArea.addWidget(self.PointEditor)
            # Load script editor page
        self.ScriptEditor = frmScriptEditor(self.MotionCtrl)
        self.MotionCtrl.BindScriptEditor(self.ScriptEditor)
        self.stkwFunctionArea.addWidget(self.ScriptEditor)
            # Load motion tuner page
        self.MotionTuner = frmMotionTuner(self.MotionCtrl)
        self.MotionCtrl.BindMotionTuner(self.MotionTuner)
        self.stkwFunctionArea.addWidget(self.MotionTuner)
            # Load upgrade page
        self.Upgrade = frmUpgrade(self.MotionCtrl)
        self.MotionCtrl.BindUpgrade(self.Upgrade)
        self.stkwFunctionArea.addWidget(self.Upgrade)
            # Load information page
        self.Information = frmInformation(self.MotionCtrl)
        self.MotionCtrl.BindInformation(self.Information)
        self.stkwFunctionArea.addWidget(self.Information)
            # Load about information
        self.AboutInfo = frmAbout(self.MotionCtrl)

        # Init Real time status viewer
        self.RealTimeStatusInit()
        
        # Connect signal&slot paire
            # Internal event handler conncetion
        self.sigEventHandler.connect(self.sltEventHandler)
        self.mnuImportScriptFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuImportPointFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuExit.triggered.connect(self.sltPushButtonHandler)
        self.mnuExportScriptFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuExportPointFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuExportMotionReportFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuExportServoReportFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuExportServoParameterFile.triggered.connect(self.sltPushButtonHandler)
        self.mnuCommConn.triggered.connect(self.sltPushButtonHandler)
        self.mnuCommClose.triggered.connect(self.sltPushButtonHandler)
        self.mnuDownloadFirmware.triggered.connect(self.sltPushButtonHandler)
        self.mnuDownloadParameter.triggered.connect(self.sltPushButtonHandler)
        self.mnuAxRobotUserGuide.triggered.connect(self.sltPushButtonHandler)
        self.mnuAbout.triggered.connect(self.sltPushButtonHandler)
        self.btnRealTimeStatusExpandAll.clicked.connect(self.sltPushButtonHandler)
            # Bind handler function for Function tree clicked event
        self.lstwFunctionSelector.itemClicked.connect(self.sltFunctionSelectorClicked)

        # Initial actions
        self.sigEventHandler.emit({"StatusChange":[0,0,0]})
        # Trigger event and show first page
        self.lstwFunctionSelector.itemClicked.emit(self.lstwFunctionSelector.item(0))
        # Start up monitor time task
        self.MotionMonitor.StartTimeTickTask(100)

    def closeEvent(self, event):
        if self.QuitApplication(1) == 0:
            event.ignore()
        else:
            event.accept()

    def QuitApplication(self, ReportResultOnly):
        # Save application config file
        self.SaveAppConfig(DEF_APP_CFIG_FILE_PATH)
        if self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
            rsp = QMessageBox.question(self, \
                                    "Quit AxRobotUtility", \
                                    "Are you sure you want to exit the application ?", \
                                    QMessageBox.Yes | QMessageBox.No, \
                                    QMessageBox.No)

            if rsp == QMessageBox.Yes:
                # Turn off servo
                if self.MotionData.SystemState >= dctSYSTEM_STATE["SERVO_ON"]:
                    self.StartUp.sigEventHandler.emit({"ServoOff":[""]}) 
                self.QuitRequest = 1

                # Disconnection
                self.StartUp.sigEventHandler.emit({"Disconnect":[""]})
            return 0
        else:
            if ReportResultOnly == 0:
                QCoreApplication.instance().quit()
            return 1

    def sltFunctionSelectorClicked(self, item):
        # Switching function pages
        if item.text() == "StartUp":
            # Reload serial port list every time the StartUp page be clicked
            self.StartUp.sigEventHandler.emit({"ReloadSerialPort":[""]})
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.StartUp))
        elif item.text() == "Parameter Viewer":
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.ParamViewer))
        elif item.text() == "Jog Control":
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.JogControl))
        elif item.text() == "Point Editor":
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.PointEditor))
        elif item.text() == "Script Editor":
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.ScriptEditor))
        elif item.text() == "Motion Tuner":
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.MotionTuner))
        elif item.text() == "Upgrade":
            # Reload serial port list every time the StartUp page be clicked
            self.Upgrade.sigEventHandler.emit({"ReloadUpgradeTarget":[""]})
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.Upgrade))
        elif item.text() == "Information":
            self.stkwFunctionArea.setCurrentIndex(self.stkwFunctionArea.indexOf(self.Information))

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()
        # Forwarding menu button event to general event handler
        if btn.objectName() == "mnuImportScriptFile":
            self.ScriptEditor.sigEventHandler.emit({"LoadScriptFromFile":[""]})
        elif btn.objectName() == "mnuImportPointFile":
            self.PointEditor.sigEventHandler.emit({"LoadPointsFromFile":[""]})
        elif btn.objectName() == "mnuExit":
            self.QuitApplication(0)
        elif btn.objectName() == "mnuExportScriptFile":
            self.ScriptEditor.sigEventHandler.emit({"SaveScriptToFile":[""]})
        elif btn.objectName() == "mnuExportPointFile":
            self.PointEditor.sigEventHandler.emit({"SavePointsToFile":[""]})
        elif btn.objectName() == "mnuExportMotionReportFile":
            self.ParamViewer.sigEventHandler.emit({"SaveAsMotionReportFile":[""]})
        elif btn.objectName() == "mnuExportServoReportFile":
            self.ParamViewer.sigEventHandler.emit({"SaveAsServoReportFile":[""]})
        elif btn.objectName() == "mnuExportServoParameterFile":
            self.ParamViewer.sigEventHandler.emit({"SaveAsServoConfigFile":[""]})
        elif btn.objectName() == "mnuCommConn":
            self.StartUp.sigEventHandler.emit({"Connect":[""]})
        elif btn.objectName() == "mnuCommClose":
            self.StartUp.sigEventHandler.emit({"Disconnect":[""]})
        elif btn.objectName() == "mnuDownloadFirmware":
            self.StartUp.sigEventHandler.emit({"DownloadFirmware":[""]})
        elif btn.objectName() == "mnuDownloadParameter":
            self.StartUp.sigEventHandler.emit({"DownloadParameter":[""]})
        elif btn.objectName() == "mnuAxRobotUserGuide":
            os.startfile(dctAPP_CFIG["USER_GUIDE_PATH"])
        elif btn.objectName() == "mnuAbout":
            self.sigEventHandler.emit({"ShowAboutInfo":[""]})
        elif btn.objectName() == "btnRealTimeStatusExpandAll":
            if self.btnRealTimeStatusExpandAll.text() == "Expand All":
                self.sigEventHandler.emit({"ExpandAll":[""]})
            else:
                self.sigEventHandler.emit({"CollapseAll":[""]})

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        # General Event Handler
        for k, v in dctEvents.items():
            # Filter out debug log
            if k != "SetProgressBox" and k != "RealTimeStatusUpdate" and k != "SetStatusBar":
                log.debug("RxEvent:%s, %s\r\n", k, str(v))

            if k == "StatusChange":
                self.SetStatusBar(self.MotionData.SystemState)
                self.StatusChange(self.MotionData.SystemState)
            elif k == "SetStatusBar":
                self.SetStatusBar(self.MotionData.SystemState)
            elif k == "RealTimeStatusUpdate":
                self.RealTimeStatusUpdate()
                self.UpdateIndicatorLED(v[0], v[1])
            elif k == "SetMsgBox":
                if v[0] == "Information":
                    QMessageBox.information(self, v[0], v[1], QMessageBox.Close)
                elif v[0] == "Warning":
                    QMessageBox.warning(self, v[0], v[1], QMessageBox.Close)
                else:
                    QMessageBox.critical(self, v[0], v[1], QMessageBox.Close)

            elif k == "SetProgressBox":
                self.SetProgressBox(v)

            elif k == "CollapseAll":
                self.trwRealTimeStatus.collapseAll()
                self.btnRealTimeStatusExpandAll.setText("Expand All")

            elif k == "ExpandAll":
                log.debug("ExpandAll...\r\n")
                self.trwRealTimeStatus.expandAll()
                self.btnRealTimeStatusExpandAll.setText("Collapse All")

            elif k == "ShowAboutInfo":
                self.AboutInfo.show()

    def SetProgressBox(self, lstEvent):
        if lstEvent[0] == "Open":
            self.ProgressBox.setLabelText(lstEvent[1])
            self.ProgressBox.setValue(0)
            self.ProgressBox.show()
        elif lstEvent[0] == "SetText":
            self.ProgressBox.setLabelText(lstEvent[1])
        elif lstEvent[0] == "SetValue":
            self.ProgressBox.setValue(lstEvent[1])
        elif lstEvent[0] == "Close":
            self.ProgressBox.hide()

    def SetStatusBar(self, status):
        if status >= dctSYSTEM_STATE["SERVO_ON"]:
            self.lbConnStatus.setText("Connected@"+self.StartUp.ConnectedPortName)
            deltaTime = datetime.datetime.now()-self.StartUp.ConnectStartTime
            self.lbConnTime.setText(str(deltaTime))
            self.lbOnlineDevices.setText(str(self.StartUp.OnlineServoCount)+"/"+str(self.StartUp.OnlineDeviceCount))
            self.lbServoStatus.setText("ON")
        elif status >= dctSYSTEM_STATE["CONNECTED"]:
            self.lbConnStatus.setText("Connected@"+self.StartUp.ConnectedPortName)
            deltaTime = datetime.datetime.now()-self.StartUp.ConnectStartTime
            self.lbConnTime.setText(str(deltaTime))
            self.lbOnlineDevices.setText(str(self.StartUp.OnlineServoCount)+"/"+str(self.StartUp.OnlineDeviceCount))
            self.lbServoStatus.setText("OFF")
        else:
            self.lbConnStatus.setText("Disconnected")
            self.lbConnTime.setText("")
            self.lbOnlineDevices.setText(str(self.StartUp.OnlineServoCount)+"/"+str(self.StartUp.OnlineDeviceCount))
            self.lbServoStatus.setText("OFF")

        if self.MotionData.extForceEnabled == 0:
            self.lbExtForceStatus.setText("OFF")
        else:
            self.lbExtForceStatus.setText("ON")

    def StatusChange(self, status):
        if  status >= dctSYSTEM_STATE["RUN_TUNER"]:
            # Change function selector status
            self.StartUp.setEnabled(True)
            self.ParamViewer.setEnabled(False)
            self.JogControl.setEnabled(False)
            self.PointEditor.setEnabled(True)
            self.ScriptEditor.setEnabled(False)
            self.MotionTuner.setEnabled(True)
            self.Upgrade.setEnabled(False)
            self.Information.setEnabled(True)
        elif  status >= dctSYSTEM_STATE["RUN_SCRIPT"]:
            # Change function selector status
            self.StartUp.setEnabled(True)
            self.ParamViewer.setEnabled(False)
            self.JogControl.setEnabled(False)
            self.PointEditor.setEnabled(False)
            self.ScriptEditor.setEnabled(True)
            self.MotionTuner.setEnabled(False)
            self.Upgrade.setEnabled(False)
            self.Information.setEnabled(True)
        elif  status >= dctSYSTEM_STATE["RUN_JOG"]:
            # Change function selector status
            self.StartUp.setEnabled(True)
            self.ParamViewer.setEnabled(False)
            self.JogControl.setEnabled(True)
            self.PointEditor.setEnabled(True)
            self.ScriptEditor.setEnabled(False)
            self.MotionTuner.setEnabled(False)
            self.Upgrade.setEnabled(False)
            self.Information.setEnabled(True)
        elif status >= dctSYSTEM_STATE["SERVO_ON"]:
            # Change menu bar button status
            self.mnuImportScriptFile.setEnabled(True)
            self.mnuImportPointFile.setEnabled(True)
            self.mnuExportScriptFile.setEnabled(True)
            self.mnuExportPointFile.setEnabled(True)
            self.mnuExportMotionReportFile.setEnabled(True)
            self.mnuExportServoReportFile.setEnabled(True)
            self.mnuExportServoParameterFile.setEnabled(True)
            self.mnuCommConn.setEnabled(False)
            self.mnuCommClose.setEnabled(False)
            self.mnuDownloadFirmware.setEnabled(False)
            self.mnuDownloadParameter.setEnabled(False)
            # Change function selector status
            self.StartUp.setEnabled(True)
            self.ParamViewer.setEnabled(True)
            self.JogControl.setEnabled(True)
            self.PointEditor.setEnabled(True)
            self.ScriptEditor.setEnabled(True)
            self.MotionTuner.setEnabled(True)
            self.Upgrade.setEnabled(False)
            self.Information.setEnabled(True)
        elif self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
            # Change menu bar button status
            self.mnuImportScriptFile.setEnabled(True)
            self.mnuImportPointFile.setEnabled(False)
            self.mnuExportScriptFile.setEnabled(True)
            self.mnuExportPointFile.setEnabled(True)
            self.mnuExportMotionReportFile.setEnabled(True)
            self.mnuExportServoReportFile.setEnabled(True)
            self.mnuExportServoParameterFile.setEnabled(True)
            self.mnuCommConn.setEnabled(False)
            self.mnuCommClose.setEnabled(True)
            self.mnuDownloadFirmware.setEnabled(True)
            self.mnuDownloadParameter.setEnabled(True)
            # Change function selector status
            self.StartUp.setEnabled(True)
            self.ParamViewer.setEnabled(True)
            self.JogControl.setEnabled(False)
            self.PointEditor.setEnabled(False)
            self.ScriptEditor.setEnabled(False)
            self.MotionTuner.setEnabled(False)
            self.Upgrade.setEnabled(True)
            self.Information.setEnabled(True)
        else:# dctSYSTEM_STATE["DISCONNECTED"]
            # Change menu bar button status
            self.mnuImportScriptFile.setEnabled(True)
            self.mnuImportPointFile.setEnabled(False)
            self.mnuExportScriptFile.setEnabled(True)
            self.mnuExportPointFile.setEnabled(True)
            self.mnuExportMotionReportFile.setEnabled(False)
            self.mnuExportServoReportFile.setEnabled(False)
            self.mnuExportServoParameterFile.setEnabled(False)
            self.mnuCommConn.setEnabled(True)
            self.mnuCommClose.setEnabled(False)
            self.mnuDownloadFirmware.setEnabled(False)
            self.mnuDownloadParameter.setEnabled(False)
            # Change function selector status
            self.StartUp.setEnabled(True)
            self.ParamViewer.setEnabled(False)
            self.JogControl.setEnabled(False)
            self.PointEditor.setEnabled(False)
            self.ScriptEditor.setEnabled(False)
            self.MotionTuner.setEnabled(False)
            self.Upgrade.setEnabled(False)
            self.Information.setEnabled(True)
            # Change LED status
            self.UpdateIndicatorLED(0, "")
            # Quit application if need
            if self.QuitRequest != 0:
                QCoreApplication.instance().quit()

    def LoadAppConfig(self, filePath):
        dctCfg = dict()
        chkok = 0
        try:
            # Found application configuration file
            with open(filePath,'r') as f:
                dctCfg = json.load(f)
                f.close()
            chkok = 1
            # Check app config is available
            for k in dctAPP_CFIG:
                if k not in dctCfg:
                    chkok = 0
                    break
        except Exception as e:
            pass
            
        if chkok == 1:
            for k in dctCfg:
                dctAPP_CFIG[k] = dctCfg[k]
            log.debug("Load %s file ok\r\n", filePath)
        else:
            log.debug("Create new %s file\r\n", filePath)
            # If execution path contains "Binary_", 
            # that indicate performing binary file and MUST adjust related file path.
            log.debug("os.path.dirname(os.path.realpath(__file__)):%s\r\n", os.path.dirname(os.path.realpath(__file__)))
            if os.path.dirname(os.path.realpath(__file__)).find("\Binary") >= 0:
                log.debug("Startup from binary, adjust the resource path\r\n")
                dctAPP_CFIG["ECAT_MASTER_FW_PATH"] = "../"+dctAPP_CFIG["ECAT_MASTER_FW_PATH"]
                dctAPP_CFIG["SERVO_FW_PATH"] = "../"+dctAPP_CFIG["SERVO_FW_PATH"]
                dctAPP_CFIG["USER_GUIDE_PATH"] = "..\\"+dctAPP_CFIG["USER_GUIDE_PATH"]

            self.SaveAppConfig(filePath)

    def SaveAppConfig(self, filePath):
        try:
            log.debug("Save %s file ok, %s\r\n", filePath, str(dctAPP_CFIG))
            with open(filePath,'w') as f:
                json.dump(dctAPP_CFIG, f, ensure_ascii = False, indent = 4)
                f.close()
        except Exception as e:
            log.debug("Exception: %s\r\n", str(e))
        finally:
            pass

    def RealTimeStatusInit(self):
        qtrw = self.trwRealTimeStatus
        qtrw.setColumnWidth(0, 140)
        qtrw.setColumnWidth(1, 90)
        hdr = qtrw.header()
        hdr.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        # Create RtStatus tree view content
        for i in self.MotionData.lstRtStatusShowItems:
            # Create top level
            qtop = QtWidgets.QTreeWidgetItem(qtrw)
            qtop.setText(0, i)
            
            # Create child
            if i in self.MotionData.dctMotionParam:
                k = self.MotionData.dctMotionParam[i]
            elif i in self.MotionData.dctRtStatus:
                k = self.MotionData.dctRtStatus[i]
            elif i in self.MotionData.dctServoParam:
                k = self.MotionData.dctServoParam[i]
            else:
                continue
            
            if len(k["Value"]) == 1:
                qtop.setToolTip(0, k["Note"])
                continue
            lstUnit = k["Unit"].split()
            if "Item" in k:
                lstItem = k["Item"].split()
            for j in range(len(k["Value"])):
                qchd = QtWidgets.QTreeWidgetItem(qtop)
                if "Item" in k:
                    qchd.setText(0, lstItem[j])
                else:
                    qchd.setText(0, "J"+str(j+1))
                log.debug("len(lstUnit[%d]): %d\r\n", j, len(lstUnit))
                if len(lstUnit) > 1:
                # if isinstance(lstUnit, list):
                    qchd.setText(2, lstUnit[j])
                else:
                    qchd.setText(2, lstUnit[0])
            qtop.setToolTip(0, k["Note"])

    def RealTimeStatusUpdate(self):
        qtrw = self.trwRealTimeStatus

        #Update parameter tree data status
        for i in range(qtrw.topLevelItemCount()):
            qtop = qtrw.topLevelItem(i)
            if qtop.text(0) in self.MotionData.dctMotionParam:
                k = self.MotionData.dctMotionParam[qtop.text(0)]
            elif qtop.text(0) in self.MotionData.dctRtStatus:
                k = self.MotionData.dctRtStatus[qtop.text(0)]
            elif qtop.text(0) in self.MotionData.dctServoParam:
                k = self.MotionData.dctServoParam[qtop.text(0)]
            else:
                continue

            if qtrw.topLevelItem(i).childCount() == 0:
                qtop.setText(1, "{}".format(k["Value"]))
                continue
            for j in range(qtrw.topLevelItem(i).childCount()):
                val = k["Value"][j]
                qtop.child(j).setText(1, "{}".format(val))

    def UpdateIndicatorLED(self, ledStatus, strMotionStatus):
        if ledStatus & 0x04:
            self.ledGreen.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"CircleGreen.png"))
        else:
            self.ledGreen.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"CircleGrey.png"))

        if ledStatus & 0x02:
            self.ledYellow.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"CircleYellow.png"))
        else:
            self.ledYellow.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"CircleGrey.png"))

        if ledStatus & 0x01:
            self.ledRed.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"CircleRed.png"))
        else:
            self.ledRed.setPixmap(QtGui.QPixmap(dctAPP_CFIG["IMG_PATH"]+"CircleGrey.png"))

        self.lblMotionStatus.setText(strMotionStatus)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())





