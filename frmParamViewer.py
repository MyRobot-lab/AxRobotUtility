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
import sys, logging, time
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QFileInfo, pyqtSlot, pyqtSignal, Qt
from ui.frmParamViewerUi import *
from AxRobotData import *

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmParamViewer(QWidget, Ui_Form):
    sigEventHandler = pyqtSignal(dict)
    sigParamViewerProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent=None):
        super(frmParamViewer, self).__init__(parent)

        # Init object point
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())
        
        # Init UI components
        self.setupUi(self)
        self.CreateMotionParamViewer()
        self.CreateServoParamViewer()
        self.tbwParamEditor.setCurrentIndex(0)

        # Connect signal&slot paire
            # Internal event handling
        self.sigEventHandler.connect(self.sltEventHandler)
            # Establish ParamViewerProcess connection
        self.sigParamViewerProcess.connect(self.MotionCtrl.sltParamViewerProcess)
        self.btnUploadMotionParam.clicked.connect(self.sltPushButtonHandler)
        self.btnSaveAsMotionReportFile.clicked.connect(self.sltPushButtonHandler)
        self.btnUploadServoParam.clicked.connect(self.sltPushButtonHandler)
        self.btnSaveAsServoReportFile.clicked.connect(self.sltPushButtonHandler)
        self.btnSaveAsServoConfigFile.clicked.connect(self.sltPushButtonHandler)
        self.btnExpandCollapseAllMotionParam.clicked.connect(self.sltPushButtonHandler)
        self.btnExpandCollapseAllServoParam.clicked.connect(self.sltPushButtonHandler)

        # Init GUI status
        self.sigEventHandler.emit({"Ready":[""]})

    def SetGuiStatus(self, event, option=""):
        if event == "Ready":
            self.btnUploadMotionParam.setEnabled(True)
            self.btnSaveAsMotionReportFile.setEnabled(True)
            self.btnUploadServoParam.setEnabled(True)
            self.btnSaveAsServoReportFile.setEnabled(True)
            self.btnSaveAsServoConfigFile.setEnabled(True)
        elif event == "CollapseAll":
            if option == "Motion":
                self.btnExpandCollapseAllMotionParam.setText("Expand All")
            else:
                self.btnExpandCollapseAllServoParam.setText("Expand All")
        elif event == "ExpandAll":
            if option == "Motion":
                self.btnExpandCollapseAllMotionParam.setText("Collapse All")
            else:
                self.btnExpandCollapseAllServoParam.setText("Collapse All")
        else:
            self.btnUploadMotionParam.setEnabled(False)
            self.btnSaveAsMotionReportFile.setEnabled(False)
            self.btnUploadServoParam.setEnabled(False)
            self.btnSaveAsServoReportFile.setEnabled(False)
            self.btnSaveAsServoConfigFile.setEnabled(False)

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()
        if btn.objectName() == "btnUploadMotionParam":
            self.sigEventHandler.emit({"UploadMotionParam":[""]})

        elif btn.objectName() == "btnSaveAsMotionReportFile":
            self.sigEventHandler.emit({"SaveAsMotionReportFile":[""]})

        elif btn.objectName() == "btnUploadServoParam":
            self.sigEventHandler.emit({"UploadServoParam":[""]})

        elif btn.objectName() == "btnSaveAsServoReportFile":
            self.sigEventHandler.emit({"SaveAsServoReportFile":[""]})

        elif btn.objectName() == "btnSaveAsServoConfigFile":
            self.sigEventHandler.emit({"SaveAsServoConfigFile":[""]})

        elif btn.objectName() == "btnExpandCollapseAllMotionParam":
            if btn.text() == "Expand All":
                self.sigEventHandler.emit({"ExpandAll":["Motion"]})
            else:
                self.sigEventHandler.emit({"CollapseAll":["Motion"]})

        elif btn.objectName() == "btnExpandCollapseAllServoParam":
            if btn.text() == "Expand All":
                self.sigEventHandler.emit({"ExpandAll":["Servo"]})
            else:
                self.sigEventHandler.emit({"CollapseAll":["Servo"]})

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

            if k == "UploadMotionParam":
                # Change GUI Status
                self.SetGuiStatus(k)
                # Find first parameter name
                for kp in self.MotionData.dctMotionParam:
                    if kp[:3]=="blk":
                        continue
                    break
                self.UploadMotionParams(kp, len(self.MotionData.dctMotionParam))
            elif k == "SaveAsMotionReportFile":
                self.SaveMotionParamToFile(self.MotionData.dctMotionParam, 0)
            elif k == "UpdateMotionParams":
                self.UpdateMotionParams(v[0], v[1])

            elif k == "UploadServoParam":
                # Change GUI Status
                self.SetGuiStatus(k)
                # Find first parameter name
                for kp in self.MotionData.dctServoParam:
                    if kp[:3]=="blk":
                        continue
                    break
                self.UploadServoParams(kp, len(self.MotionData.dctServoParam))
            elif k == "SaveAsServoReportFile":
                self.SaveServoParamToFile(self.MotionData.dctServoParam, 0)
            elif k == "SaveAsServoConfigFile":
                self.SaveServoParamToFile(self.MotionData.dctServoParam, 1)
            elif k == "UpdateServoParams":
                self.UpdateServoParams(v[0], v[1])
            elif k == "Ready":
                self.SetGuiStatus(k)
            elif k == "CollapseAll":
                self.SetGuiStatus(k, v[0])
                if v[0] == "Motion":
                    self.trvMotionParam.collapseAll()
                else:
                    self.trvServoParam.collapseAll()
            elif k == "ExpandAll":
                self.SetGuiStatus(k, v[0])
                if v[0] == "Motion":
                    self.trvMotionParam.expandAll()
                else:
                    self.trvServoParam.expandAll()

    def CreateMotionParamViewer(self):
        trv = self.trvMotionParam
        # Create columns
        trv.setColumnWidth(0, 100)#Index
        trv.setColumnWidth(1, 120)#Name
        trv.setColumnWidth(2, 120)#Value
        trv.setColumnWidth(3, 100)#Unit
        #trv.setColumnWidth(4, 150)#Flag
        hdr = trv.header()
        hdr.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        # Create rows
        for k in self.MotionData.dctMotionParam:
            # Skip block description
            if k[:3] == "blk":
                continue
            v = self.MotionData.dctMotionParam[k]

            # Create top level
            qtop = QtWidgets.QTreeWidgetItem(trv)
            qtop.setText(0, str(v["Index"]))
            qtop.setText(1, k)
            qtop.setText(3, v["Unit"])
            strFlag = "stu."
            if v["Flag"] & flgCTRL != 0:
                strFlag = "ctl."
            elif v["Flag"] & flgCFIG != 0:
                strFlag = "cfg."
            qtop.setText(4, strFlag)
            # qtop.setText(5, "{}".format(v["Max"]))
            # qtop.setText(6, "{}".format(v["Min"]))
            # qtop.setText(7, v["Note"])
            # Create child
            if v["Flag"] & flgSHOW_AS_HEX:
                strFmt = "0x{:08x}"
            else:
                strFmt = "{}"
            if type(v["Value"]) is list:
                for j in range(len(v["Value"])):
                    qchd = QtWidgets.QTreeWidgetItem(qtop)
                    qchd.setText(1, "J"+str(j+1))
                    qchd.setText(2, strFmt.format(v["Value"][j]))
            else:
                qtop.setText(2, strFmt.format(v["Value"]))       

    def CreateServoParamViewer(self):
        trv = self.trvServoParam
        # Create columns
        trv.setColumnWidth(0, 100)#Index
        trv.setColumnWidth(1, 120)#Name
        trv.setColumnWidth(2, 120)#Value
        trv.setColumnWidth(3, 100)#Unit
        #trv.setColumnWidth(4, 150)#Flag
        hdr = trv.header()
        hdr.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        # Create rows
        for k in self.MotionData.dctServoParam:
            # Skip block description
            if k[:3] == "blk":
                continue
            v = self.MotionData.dctServoParam[k]

            # Create top level
            qtop = QtWidgets.QTreeWidgetItem(trv)
            qtop.setText(0, str(v["Index"]))
            qtop.setText(1, k)
            qtop.setText(3, v["Unit"])
            strFlag = "stu."
            if v["Flag"] & flgCTRL != 0:
                strFlag = "ctl."
            elif v["Flag"] & flgCFIG != 0:
                strFlag = "cfg."
            qtop.setText(4, strFlag)
            # qtop.setText(5, "{}".format(v["Max"]))
            # qtop.setText(6, "{}".format(v["Min"]))
            # qtop.setText(7, v["Note"])
            # Create child
            if v["Flag"] & flgSHOW_AS_HEX:
                strFmt = "0x{:08x}"
            else:
                strFmt = "{}"
            if type(v["Value"]) is list:
                for j in range(len(v["Value"])):
                    qchd = QtWidgets.QTreeWidgetItem(qtop)
                    qchd.setText(1, "J"+str(j+1))
                    qchd.setText(2, strFmt.format(v["Value"][j]))
            else:
                qtop.setText(2, strFmt.format(v["Value"]))

    def UploadMotionParams(self, ParamName, ItemCount):
        dctCmd = {"MotionRead":[ParamName, ItemCount]}
        self.sigParamViewerProcess.emit(dctCmd)
        log.debug("UploadMotionParams:%s\r\n", str(dctCmd))

    def UpdateMotionParams(self, ParamName, ItemCount):
        trv = self.trvMotionParam
        found = 0
        for i in range(trv.topLevelItemCount()):
            # Get top level
            qtop = trv.topLevelItem(i)
            # Find parameter name
            if qtop.text(1) == ParamName or found == 1:
                found = 1
                if ItemCount <= 0:
                    break
                ItemCount -= 1
                # Update value
                if self.MotionData.dctMotionParam[qtop.text(1)]["Flag"] & flgSHOW_AS_HEX:
                    strFmt = "0x{:08x}"
                else:
                    strFmt = "{}"
                v = self.MotionData.dctMotionParam[qtop.text(1)]["Value"]
                if qtop.childCount() == 0:
                    qtop.setText(2, strFmt.format(v))
                else:
                    for j in range(qtop.childCount()):
                        qtop.child(j).setText(2, strFmt.format(v[j]))
                #log.debug("UpdateMotionParams: %s=%s\r\n", qtop.text(1), str(v))

    def UploadServoParams(self, ParamName, ItemCount):
        dctCmd = {"ServoRead":[ParamName, ItemCount]}
        self.sigParamViewerProcess.emit(dctCmd)
        log.debug("UploadServoParams:%s\r\n", str(dctCmd))

    def UpdateServoParams(self, ParamName, ItemCount):
        trv = self.trvServoParam
        found = 0
        for i in range(trv.topLevelItemCount()):
            # Get top level
            qtop = trv.topLevelItem(i)
            # Find parameter name
            if qtop.text(1) == ParamName or found == 1:
                found = 1
                if ItemCount <= 0:
                    break
                ItemCount -= 1
                # Update value
                if self.MotionData.dctServoParam[qtop.text(1)]["Flag"] & flgSHOW_AS_HEX:
                    strFmt = "0x{:08x}"
                else:
                    strFmt = "{}"
                v = self.MotionData.dctServoParam[qtop.text(1)]["Value"]
                if qtop.childCount() == 0:
                    qtop.setText(2, strFmt.format(v))
                else:
                    for j in range(qtop.childCount()):
                        qtop.child(j).setText(2, strFmt.format(v[j]))
                #log.debug("UpdateServoParams: %s=%s\r\n", qtop.text(1), str(v))

    def SaveMotionParamToFile(self, dctParams, SaveAsConfigFile):
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            if SaveAsConfigFile == 0:
                strTitle = "Save As Report File"
                strExtendtion = ".rpt"
                strExtendDesc = "parameter report file (*.rpt)"
            else:
                strTitle = "Save As Configuration File"
                strExtendtion = ".txt"
                strExtendDesc = "configuration file (*.txt)"

            filePath, _ = QFileDialog.getSaveFileName(self, \
                            strTitle, \
                            dctAPP_CFIG["PARAM_PATH"], \
                            strExtendDesc, \
                            options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Save to filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += strExtendtion
                f = open(filePath, "w")
                self.CreateMotionFileContent(f, dctParams, SaveAsConfigFile)
                f.close()
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", str(e)]})
        finally:
            pass

    def CreateMotionFileContent(self, f, dctParams, SaveAsConfigFile):
        f.write("# \n")
        if SaveAsConfigFile == 0:
            f.write("# Title: Motion Parameter Report File\n")
        else:
            f.write("# Title: Motion Parameter Configuration File\n")
        f.write("# Firmware Version/Date: {}/{}\n".format(str(dctParams["sysVERS"]["Value"]), str(dctParams["sysDATE"]["Value"])))
        f.write("# Date Time: {}\n".format(time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime())))
        f.write("# \n")

        for pm in dctParams:
            if pm[:3] == "blk":
                f.write("\n\n# {}\n".format(dctParams[pm]["Name"]))
                continue
            f.write("{}={}\n".format(pm, str(dctParams[pm]["Value"])))

    def SaveServoParamToFile(self, dctParams, SaveAsConfigFile):
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            if SaveAsConfigFile == 0:
                strTitle = "Save As Report File"
                strExtendtion = ".rpt"
                strExtendDesc = "parameter report file (*.rpt)"
            else:
                strTitle = "Save As Configuration File"
                strExtendtion = ".txt"
                strExtendDesc = "configuration file (*.txt)"

            filePath, _ = QFileDialog.getSaveFileName(self, \
                            strTitle, \
                            dctAPP_CFIG["PARAM_PATH"], \
                            strExtendDesc, \
                            options=opt)

            fileName = QFileInfo(filePath).fileName()
            log.debug("Save to filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if SaveAsConfigFile == 0:
                    fileName = fileName.split(".")
                    if len(fileName) < 2:
                        filePath += strExtendtion
                    f = open(filePath, "w")
                    self.CreateServoFileContent(f, dctParams, SaveAsConfigFile)
                    f.close()
                else:
                    # Slice path part
                    filePath = filePath.split(".")
                    for i in range(self.MotionCtrl.StartUp.OnlineServoCount):
                        f = open(filePath[0]+str(i+1)+strExtendtion, "w")
                        self.CreateServoFileContent(f, dctParams, i+1)
                        f.close()
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", str(e)]})
        finally:
            pass

    def CreateServoFileContent(self, f, dctParams, SaveAsConfigFile):
        f.write("# \n")
        if SaveAsConfigFile == 0:# Save as report
            f.write("# Title: All Servo Parameter Report File\n")
            f.write("# Firmware Version/Date: {}/{}\n".format(str(dctParams["sysVERS"]["Value"]), \
            str(dctParams["sysDATE"]["Value"])))
        else:# Save as configuratoin
            f.write("# Title: Servo {} Parameter Configuration File\n".format(SaveAsConfigFile))
            f.write("# Firmware Version/Date: {}/{}\n".format(str(dctParams["sysVERS"]["Value"][SaveAsConfigFile-1]), \
            str(dctParams["sysDATE"]["Value"][SaveAsConfigFile-1])))

        f.write("# Date Time: {}\n".format(time.strftime("%Y-%m-%d %I:%M:%S %p", time.localtime())))
        f.write("# \n")

        for pm in dctParams:
            # Show block description
            if pm[:3] == "blk":
                f.write("\n\n# {}\n".format(dctParams[pm]["Name"]))
                continue

            # Skip unconfigurable parameters
            if SaveAsConfigFile != 0:
                if dctParams[pm]["Flag"] & flgCFIG == 0:
                    continue

            if SaveAsConfigFile == 0:
                f.write("{}={}\n".format(pm, str(dctParams[pm]["Value"])))
            else:
                # Check parameter that has init. value
                if dctParams[pm]["Flag"] & flgCFIG_RESET != 0:
                    f.write("{}={}\n".format(pm, str(0)))
                else:
                    f.write("{}={}\n".format(pm, str(dctParams[pm]["Value"][SaveAsConfigFile-1])))

#End of Class frmParamViewer




