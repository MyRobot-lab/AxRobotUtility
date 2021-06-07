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
import sys, logging, serial, serial.tools.list_ports, time, json
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QThread, QObject, pyqtSlot, pyqtSignal, QTimer, Qt, QFileInfo
from ui.frmMotionTunerUi import *
from AxRobotData import *
import escMotion
import matplotlib
import matplotlib.pyplot as plt

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmMotionTuner(QWidget, Ui_Form):
    sigEventHandler = pyqtSignal(dict)
    sigfrmMotionTunerProcess = pyqtSignal(dict)
    sigfrmMotionTunerEvent = pyqtSignal(dict)

    dctDefConfig = {
        # Gravity factor measurement condition
        "Gravity" : { \
                    "ToolWeight": 5, \
                    "SamplingTime": 20, \
                    "SpeedLimit": 5000, \
                    "Speed": 50, \
                    "InitialGravityFactor": [0]*MaxAxisNum, \
                    },

        # Friction factor measurement condition
        "Friction" : { \
                    "SamplingTime": 20, \
                    "SpeedLimit": 5000, \
                    "MinTestSpeed": 20, \
                    "MaxTestSpeed": 200, \
                    "TestSpeedSections": 10, \
                    },

        # extForce Compensation
        "extForce" : { \
                    "SamplingTime": 20, \
                    "Speed": 100, \
                    "DecelerationLimit": 0, \
                    "GravityFactor": [0]*MaxAxisNum, \
                    "StaticFrictionFactor": [0]*MaxAxisNum, \
                    "DynamicFrictionFactor": [0]*MaxAxisNum, \
                    "DraggedStaticFrictionFactor": [0]*MaxAxisNum, \
                    "DraggedDynamicFrictionFactor": [0]*MaxAxisNum, \
                    "ConcentricInertiaFactor": [0]*MaxAxisNum, \
                    "EccentricInertiaFactor": [0]*MaxAxisNum, \
                    "CollisionTestTorque": [0]*MaxAxisNum, \
                    "extForceSwitch": 300, \
                    "EnbAlarmMode": 1, \
                    },
    }

    def __init__(self, MotionCtrl, parent=None):
        super(frmMotionTuner, self).__init__(parent)

        # Init normal data
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData
            # Test condition
        self.AxisId = 1
        self.Angle = 0
        self.Speed = 0
        # self.SampleTime = 0
        self.lstData = list()
        self.DataLength = 0
        self.AxisX = 0
            # Gravity distribution calculation

            # Gravity factor measurement
        self.SampledPoints = [0]*MaxAxisNum
        self.AverageGravity = [0]*MaxAxisNum
        self.AverageTorque = [0]*MaxAxisNum
        self.lstMeasuredGravityFactor = [0]*MaxAxisNum
            # extForce compensation
        self.lstMeasuredDynamicFriction = [0]*MaxAxisNum
        self.lstMeasuredStaticFriction = [0]*MaxAxisNum
        self.lstMeasuredDraggedDynamicFriction = [0]*MaxAxisNum
        self.lstMeasuredDraggedStaticFriction = [0]*MaxAxisNum
        self.SpeedLimit = 0
        self.AccDecLimit = 0
        
            # Plot request
        self.lstCurveColors = list()
        self.lstCurveLabels = list()

        self.dctConfig = self.dctDefConfig

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())

        # Init UI components
        self.setupUi(self)

        self.tbwMotionTuner.setCurrentIndex(0)

            # Gravity factor measurement
        self.leToolWeight.setText("0")
        self.cboGravityAxis.addItems(["J2","J4","J6"])
        self.cboGravityAxis.setCurrentIndex(0)
        self.cboGravityAngle.addItems(["30","-30","60","-60","90","-90"])
        self.cboGravityAngle.setCurrentIndex(0)
        self.leGravityFactor.setEnabled(False)
        self.leAverageGravity.setEnabled(False)
        self.leAverageTorque.setEnabled(False)
        self.leSampledPoints.setEnabled(False)
            # Friction factor measurement
        self.cboFrictionAxis.addItems(["J1","J2","J3","J4","J5","J6","J7"])
        self.cboFrictionAxis.setCurrentIndex(0)
        self.cboFrictionAngle.addItems(["30","60","90"])
        self.cboFrictionAngle.setCurrentIndex(0)
        self.leStaticFriction.setEnabled(False)
        self.leDynamicFriction.setEnabled(False)
        self.leDraggedStaticFriction.setEnabled(False)
        self.leDraggedDynamicFriction.setEnabled(False)
            # extForce compensation 
        self.cboExtForceAxis.addItems(["J1","J2","J3","J4","J5","J6","J7"])
        self.cboExtForceAxis.setCurrentIndex(0)
        self.cboExtForceAngle.addItems(["30","60","90"])
        self.cboExtForceAngle.setCurrentIndex(0)
        self.ckbEnbAlarmMode.setChecked(True)

            # Config Management
        self.leMotionConfigFilePath.setEnabled(False)

        # Connect signal&slot paire
            # Config Management
        self.btnLoadMotionConfigFile.clicked.connect(self.sltPushButtonHandler)
        self.btnSaveMotionConfigFile.clicked.connect(self.sltPushButtonHandler)
            # Gravity factor measurement
        self.btnGravityDistribution.clicked.connect(self.sltPushButtonHandler)
        self.cboGravityAxis.currentTextChanged.connect(self.sltCurrentTextChanged)
        self.btnGravityFactorMeasure.clicked.connect(self.sltPushButtonHandler)
            # Friction factor measurement
        self.cboFrictionAxis.currentTextChanged.connect(self.sltCurrentTextChanged)
        self.btnFrictionFactorMeasure.clicked.connect(self.sltPushButtonHandler)
            # extForce compensation
        self.cboExtForceAxis.currentTextChanged.connect(self.sltCurrentTextChanged)
        self.btnReloadMeasuredFactors.clicked.connect(self.sltPushButtonHandler)
        self.btnExtForceCompensate.clicked.connect(self.sltPushButtonHandler)
        # self.btnCollisionTest.clicked.connect(self.sltPushButtonHandler)

        self.sigEventHandler.connect(self.sltEventHandler)# Internal event process connection
        self.sigfrmMotionTunerProcess.connect(self.MotionCtrl.sltMotionTunerProcess)# Establish frmMotionTunerProcess connection
        self.sigfrmMotionTunerEvent.connect(self.MotionCtrl.sltMotionTunerEvent)

        # Init GUI status
        self.sigEventHandler.emit({"ReloadMotionConfig":[""]})

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()

        if btn.objectName() == "btnLoadMotionConfigFile":
            self.sigEventHandler.emit({"LoadMotionConfigFile": [""]})  
        elif btn.objectName() == "btnSaveMotionConfigFile":
            self.sigEventHandler.emit({"SaveMotionConfigFile": [""]})  

        elif btn.objectName() == "btnGravityDistribution":
            self.sigEventHandler.emit({"GravityDistribution": [""]})
        elif btn.objectName() == "btnGravityFactorMeasure":
            self.sigEventHandler.emit({"GravityFactorMeasure": [""]})

        elif btn.objectName() == "btnFrictionFactorMeasure":
            self.sigEventHandler.emit({"FrictionFactorMeasure": [""]})

        elif btn.objectName() == "btnReloadMeasuredFactors":
            self.sigEventHandler.emit({"ReloadMeasuredFactors": [""]})  
        elif btn.objectName() == "btnExtForceCompensate":
            self.sigEventHandler.emit({"ExtForceCompensate": [""]})  
        # elif btn.objectName() == "btnCollisionTest":
        #     self.sigEventHandler.emit({"CollisionTest": [""]})  

    @pyqtSlot(str)
    def sltCurrentTextChanged(self, currText):
        cbo = self.sender()
        if cbo.objectName() == "cboGravityAxis":
            self.sigEventHandler.emit({"UpdateGravityTest": [""]})

        elif cbo.objectName() == "cboFrictionAxis":
            self.sigEventHandler.emit({"UpdateFrictionTest": [""]})

        elif cbo.objectName() == "cboExtForceAxis":
            self.sigEventHandler.emit({"UpdateExtForceTest": [""]})

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

            # Config Management
            if k == "LoadMotionConfigFile":
                # Load motion config from file
                dctTemp, Result = self.LoadMotionConfigFromFile()
                if Result == 0:
                    self.dctConfig = dctTemp
                    self.StatusChange("SetGravityDistributionToHMI")
                    self.StatusChange("SetGravityConfigToHMI")
                    self.StatusChange("SetFrictionConfigToHMI")
                    self.StatusChange("SetExtForceConfigToHMI")
                    self.StatusChange("SetConfigManagementToHMI")

            elif k == "SaveMotionConfigFile":
                self.GetMotionConfigFromHMI("All")
                # Save motion config to file
                self.SaveMotionConfigToFile(self.dctConfig)

            elif k == "ReloadMotionConfig":
                # Load motion config from file
                self.ReloadMotionConfig()
                # Update to HMI
                self.StatusChange("SetGravityDistributionToHMI")
                self.StatusChange("SetGravityConfigToHMI")
                self.StatusChange("SetFrictionConfigToHMI")
                self.StatusChange("SetExtForceConfigToHMI")
                self.StatusChange("SetConfigManagementToHMI")

            # Gravity factor measurement
            elif k == "GravityDistribution" or k == "GravityFactorMeasure":
                self.GetMotionConfigFromHMI("Gravity")
                self.sigfrmMotionTunerProcess.emit({k:[""]})
            elif k == "UpdateGravityTest":
                self.StatusChange("SetGravityConfigToHMI")
                self.StatusChange("SetGravityResultToHMI")

            # Friction factor measurement
            elif k == "FrictionFactorMeasure":
                self.GetMotionConfigFromHMI("Friction")
                self.sigfrmMotionTunerProcess.emit({k:[""]})
            elif k == "UpdateFrictionTest":
                self.StatusChange("SetFrictionConfigToHMI")
                self.StatusChange("SetFrictionResultToHMI")

            # extForce compensation
            elif k == "ExtForceCompensate":
                self.GetMotionConfigFromHMI("extForce")
                self.sigfrmMotionTunerProcess.emit({k:[""]})
            elif k == "UpdateExtForceTest":
                self.StatusChange("SetExtForceConfigToHMI")
            elif k == "ReloadMeasuredFactors":
                self.StatusChange("SetMeasuredFactorToHMI")

            elif k == "CollisionTest":
                self.sigfrmMotionTunerEvent.emit({k:[500]})

            elif k == "ShowPlot":
                self.ShowPlot()

            elif k == "StatusChange":
                self.StatusChange(v[0])

    def StatusChange(self, status):
        log.debug("StatusChange: %s\r\n", status)

        if status == "Ready":
            pass

        # Gravity factor measurement
        elif status == "SetGravityDistributionToHMI":
            param = self.dctConfig["Gravity"]
            self.leToolWeight.setText(str(param["ToolWeight"]))
        elif status == "SetGravityConfigToHMI":
            self.AxisId = 2*(int(self.cboGravityAxis.currentIndex())+1)
            param = self.dctConfig["Gravity"]
            self.leGravitySamplingTime.setText(str(param["SamplingTime"]))
            self.leGravitySpeedLimit.setText(str(param["SpeedLimit"]))
            self.leGravitySpeed.setText(str(param["Speed"]))
            self.leGravityInitialFactor.setText(str(param["InitialGravityFactor"][self.AxisId-1]))
        elif status == "SetGravityResultToHMI":
            self.AxisId = 2*(int(self.cboGravityAxis.currentIndex())+1)
            self.leGravityFactor.setText(str(round(self.lstMeasuredGravityFactor[self.AxisId-1])))
            self.leAverageGravity.setText(str(round(self.AverageGravity[self.AxisId-1])))
            self.leAverageTorque.setText(str(round(self.AverageTorque[self.AxisId-1])))
            self.leSampledPoints.setText(str(self.SampledPoints[self.AxisId-1]))

        # Friction factor measurement
        elif status == "SetFrictionConfigToHMI":
            self.AxisId = int(self.cboFrictionAxis.currentIndex())+1
            param = self.dctConfig["Friction"]
            self.leFrictionSamplingTime.setText(str(param["SamplingTime"]))
            self.leFrictionSpeedLimit.setText(str(param["SpeedLimit"]))
            self.leFrictionMinTestSpeed.setText(str(param["MinTestSpeed"]))
            self.leFrictionMaxTestSpeed.setText(str(param["MaxTestSpeed"]))
            self.leFrictionSpeedTestSections.setText(str(param["TestSpeedSections"]))
        elif status == "SetFrictionResultToHMI":
            self.AxisId = int(self.cboFrictionAxis.currentIndex())+1
            self.leStaticFriction.setText(str(round(self.lstMeasuredStaticFriction[self.AxisId-1])))
            self.leDynamicFriction.setText(str(round(self.lstMeasuredDynamicFriction[self.AxisId-1])))
            self.leDraggedStaticFriction.setText(str(round(self.lstMeasuredDraggedStaticFriction[self.AxisId-1])))
            self.leDraggedDynamicFriction.setText(str(round(self.lstMeasuredDraggedDynamicFriction[self.AxisId-1])))

        # extForce compensation
        elif status == "SetExtForceConfigToHMI":
            self.AxisId = int(self.cboExtForceAxis.currentIndex())+1
            param = self.dctConfig["extForce"]
            self.leExtSamplingTime.setText(str(param["SamplingTime"]))
            self.leExtSpeed.setText(str(param["Speed"]))
            self.leExtDecelerationLimit.setText(str(param["DecelerationLimit"]))
            self.leExtForceSwitch.setText(str(param["extForceSwitch"]))
            if param["EnbAlarmMode"] == 0:
                self.ckbEnbAlarmMode.setChecked(False)
            else:
                self.ckbEnbAlarmMode.setChecked(True)
            self.leExtGravityFactor.setText(str(param["GravityFactor"][self.AxisId-1]))
            self.leExtStaticFrictionFactor.setText(str(param["StaticFrictionFactor"][self.AxisId-1]))
            self.leExtDynamicFrictionFactor.setText(str(param["DynamicFrictionFactor"][self.AxisId-1]))
            self.leExtDraggedStaticFrictionFactor.setText(str(param["DraggedStaticFrictionFactor"][self.AxisId-1]))
            self.leExtDraggedDynamicFrictionFactor.setText(str(param["DraggedDynamicFrictionFactor"][self.AxisId-1]))
            self.leExtConcentricInertiaFactor.setText(str(param["ConcentricInertiaFactor"][self.AxisId-1]))
            self.leExtEccentricInertiaFactor.setText(str(param["EccentricInertiaFactor"][self.AxisId-1]))
            self.leCollisionTestTorque.setText(str(param["CollisionTestTorque"][self.AxisId-1]))

        elif status == "SetMeasuredFactorToHMI":
            self.AxisId = int(self.cboExtForceAxis.currentIndex())+1
            param = self.dctConfig["extForce"]
            param["GravityFactor"][self.AxisId-1] = round(self.lstMeasuredGravityFactor[self.AxisId-1])
            param["StaticFrictionFactor"][self.AxisId-1] = round(self.lstMeasuredStaticFriction[self.AxisId-1])
            param["DynamicFrictionFactor"][self.AxisId-1] = round(self.lstMeasuredDynamicFriction[self.AxisId-1])
            param["DraggedStaticFrictionFactor"][self.AxisId-1] = round(self.lstMeasuredDraggedStaticFriction[self.AxisId-1])
            param["DraggedDynamicFrictionFactor"][self.AxisId-1] = round(self.lstMeasuredDraggedDynamicFriction[self.AxisId-1])
            self.leExtGravityFactor.setText(str(param["GravityFactor"][self.AxisId-1]))
            self.leExtStaticFrictionFactor.setText(str(param["StaticFrictionFactor"][self.AxisId-1]))
            self.leExtDynamicFrictionFactor.setText(str(param["DynamicFrictionFactor"][self.AxisId-1]))
            self.leExtDraggedStaticFrictionFactor.setText(str(param["DraggedStaticFrictionFactor"][self.AxisId-1]))
            self.leExtDraggedDynamicFrictionFactor.setText(str(param["DraggedDynamicFrictionFactor"][self.AxisId-1]))

        # Config Management
        elif status == "SetConfigManagementToHMI":
            self.leMotionConfigFilePath.setText(dctAPP_CFIG["MOTION_CONFIG_PATH"])

    def GetMotionConfigFromHMI(self, SectionType):

        if SectionType == "All" or SectionType == "Gravity":
            self.AxisId = 2*(int(self.cboGravityAxis.currentIndex())+1)
            self.Angle = int(self.cboGravityAngle.currentText())
            param = self.dctConfig["Gravity"]
            param["ToolWeight"] = int(self.leToolWeight.text())
            param["SamplingTime"] = int(self.leGravitySamplingTime.text())
            param["SpeedLimit"] = int(self.leGravitySpeedLimit.text())
            param["Speed"] = int(self.leGravitySpeed.text())
            param["InitialGravityFactor"][self.AxisId-1] = int(self.leGravityInitialFactor.text())
            # # Auto calculate sampling time
            # msTestTime = 300+((2000*self.Angle*10)/param["Speed"])
            # msSamplingTime = round((msTestTime*6)/8000)
            # log.debug("msTestTime: %d, msSamplingTime: %d\r\n", msTestTime, msSamplingTime)
            # if param["SamplingTime"] < msSamplingTime:
            #     param["SamplingTime"] = msSamplingTime
            #     self.leGravitySamplingTime.setText(str(param["SamplingTime"]))

        if SectionType == "All" or SectionType == "Friction":
            self.AxisId = int(self.cboFrictionAxis.currentIndex())+1
            self.Angle = int(self.cboFrictionAngle.currentText())
            param = self.dctConfig["Friction"]
            param["SamplingTime"] = int(self.leFrictionSamplingTime.text())
            param["SpeedLimit"] = int(self.leFrictionSpeedLimit.text())
            param["MinTestSpeed"] = int(self.leFrictionMinTestSpeed.text())
            param["MaxTestSpeed"] = int(self.leFrictionMaxTestSpeed.text())
            param["TestSpeedSections"] = int(self.leFrictionSpeedTestSections.text())

        if SectionType == "All" or SectionType == "extForce":
            self.AxisId = int(self.cboExtForceAxis.currentIndex())+1
            self.Angle = int(self.cboExtForceAngle.currentText())
            param = self.dctConfig["extForce"]
            param["SamplingTime"] = int(self.leExtSamplingTime.text())
            param["Speed"] = int(self.leExtSpeed.text())
            param["DecelerationLimit"] = int(self.leExtDecelerationLimit.text())
            param["extForceSwitch"] = int(self.leExtForceSwitch.text())
            if self.ckbEnbAlarmMode.isChecked():
                param["EnbAlarmMode"] = 1
            else:
                param["EnbAlarmMode"] = 0
            param["GravityFactor"][self.AxisId-1] = int(self.leExtGravityFactor.text())
            param["StaticFrictionFactor"][self.AxisId-1] = int(self.leExtStaticFrictionFactor.text())
            param["DynamicFrictionFactor"][self.AxisId-1] = int(self.leExtDynamicFrictionFactor.text())
            param["DraggedStaticFrictionFactor"][self.AxisId-1] = int(self.leExtDraggedStaticFrictionFactor.text())
            param["DraggedDynamicFrictionFactor"][self.AxisId-1] = int(self.leExtDraggedDynamicFrictionFactor.text())
            param["ConcentricInertiaFactor"][self.AxisId-1] = int(self.leExtConcentricInertiaFactor.text())
            param["EccentricInertiaFactor"][self.AxisId-1] = int(self.leExtEccentricInertiaFactor.text())
            param["CollisionTestTorque"][self.AxisId-1] = int(self.leCollisionTestTorque.text())

    def ShowPlot(self):
        n = len(self.lstData)
        plt.figure(figsize = (n, 8), dpi = 80)

        for i in range(n):
            plt.subplot((n*100) + 10 + i+1)
            plt.plot(self.AxisX, self.lstData[i], color = self.lstCurveColors[i], label = self.lstCurveLabels[i])
            plt.grid(True)
            plt.legend(loc ="upper right")

        plt.show()

    def ReloadMotionConfig(self):
        dctTemp = dict()
        chkok = 0
        filePath = dctAPP_CFIG["MOTION_CONFIG_PATH"]
        if len(QFileInfo(filePath).fileName().split(".")) < 2:
            filePath += ".mcf"

        try:
            # Found configuration file
            with open(filePath,'r') as f:
                dctTemp = json.load(f)
                f.close()
            chkok = 1
            # Check config is available
            for k in self.dctDefConfig:
                if k not in dctTemp:
                    chkok = 0
                    break
        except Exception as e:
            log.debug("Exception: %s\r\n", str(e))
        finally:
            pass
            
        try:
            if chkok == 1:
                for k in dctTemp:
                    self.dctConfig[k] = dctTemp[k]
                log.debug("Load %s file ok\r\n", filePath)
            else:
                log.debug("Create new %s file\r\n", filePath)
                with open(filePath,'w') as f:
                    json.dump(self.dctDefConfig, f, ensure_ascii = False, indent = 4)
                    self.dctConfig = self.dctDefConfig
                    f.close()
        except Exception as e:
            log.debug("Exception: %s\r\n", str(e))
        finally:
            pass

    def LoadMotionConfigFromFile(self):
        dctTemp = dict()
        Result = -1

        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getOpenFileName(self, \
                    "Load Motion Config From File", \
                    dctAPP_CFIG["MOTION_CONFIG_PATH"], \
                    "motion configuration file (*.mcf)", \
                    options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Load from filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += ".mcf"
                with open(filePath) as ptFile: 
                    dctTemp = json.load(ptFile)
                    # Check loadded file is availabled
                    for k in self.dctDefConfig:
                        if k not in dctTemp:
                            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": ["Error","Loaded config file in unavailable!"]})
                            return dctTemp, Result
                    # Save pre-loaded file path
                    dctAPP_CFIG["MOTION_CONFIG_PATH"] = filePath
                    Result = 0

        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": ["Exception",str(e)]})
        finally:
            return dctTemp, Result

    def SaveMotionConfigToFile(self, dctTemp):
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getSaveFileName(self, \
                    "Save Motion Config To File", \
                    dctAPP_CFIG["MOTION_CONFIG_PATH"], \
                    "motion configuration file (*.mcf)", \
                    options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Save to filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += ".mcf"
                with open(filePath,'w') as ptFile:
                    json.dump(dctTemp, ptFile, ensure_ascii = False, indent = 4)
                    #ptFile.close()
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": ["Exception",str(e)]})
        finally:
            pass

#End of Class frmMotionTuner





