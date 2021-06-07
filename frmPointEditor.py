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
import sys, logging, json
from PyQt5.QtWidgets import QWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QFileInfo, pyqtSlot, pyqtSignal, Qt
from ui.frmPointEditorUi import *
from AxRobotData import *

# Reserved point names
RSVPT_JOINT    = "joint"
RSVPT_WORLD    = "world"
RSVPT_WORK     = "work"
RSVPT_BASE     = "base"
RSVPT_TOOL     = "tool"
RSVPT_ROBOT    = "robot"

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class frmPointEditor(QWidget, Ui_Form):
    sigEventHandler = pyqtSignal(dict)
    sigPointEditorProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent=None):
        super(frmPointEditor, self).__init__(parent)

        # Init object point
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData
        self.RenameEventFilter = 0
        self.ReservedPointNames = [RSVPT_JOINT, RSVPT_WORLD, RSVPT_WORK, RSVPT_BASE, RSVPT_TOOL, RSVPT_ROBOT]

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())

        # Init UI components
        self.setupUi(self)
            # Init PointEditor columns
        self.tblPointEditor.setColumnWidth(0, 100)# Point name
        self.tblPointEditor.setColumnWidth(1, 100)# Base
        hdr = self.tblPointEditor.horizontalHeader()
        hdr.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)# Value
        self.tblPointEditor.setSelectionBehavior(self.tblPointEditor.SelectRows)
        self.tblPointEditor.setSelectionMode(self.tblPointEditor.SingleSelection)
            # Init base coordination selector
        self.cboBase.addItems([RSVPT_JOINT, RSVPT_WORLD, RSVPT_WORK, RSVPT_BASE])
        self.cboBase.setCurrentText(RSVPT_JOINT)

        # Connect signal&slot paire
        # self.tblPointEditor.itemActivated.connect(self.sltTableHandler)
        # self.tblPointEditor.itemClicked.connect(self.sltTableHandler)
        self.tblPointEditor.itemChanged.connect(self.sltTableHandler)
        self.btnAddPoint.clicked.connect(self.sltPushButtonHandler)
        self.btnRemovePoint.clicked.connect(self.sltPushButtonHandler)
        self.btnClearAll.clicked.connect(self.sltPushButtonHandler)
        self.btnLoadPointsFromFile.clicked.connect(self.sltPushButtonHandler)
        self.btnSavePointsToFile.clicked.connect(self.sltPushButtonHandler)
        self.sigEventHandler.connect(self.sltEventHandler)#Internal event handling
        self.sigPointEditorProcess.connect(self.MotionCtrl.sltPointEditorProcess)# Establish PointEditorProcess connection

    def sltTableHandler(self, item):
        if self.RenameEventFilter == 0:
            self.sigEventHandler.emit({"RenamePoint":""})

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()
        if btn.objectName() == "btnAddPoint":
            self.sigEventHandler.emit({"AddPoint":[""]})

        elif btn.objectName() == "btnRemovePoint":
            self.sigEventHandler.emit({"RemovePoint":[""]})

        elif btn.objectName() == "btnClearAll":
            self.sigEventHandler.emit({"ClearAll":[""]})

        elif btn.objectName() == "btnLoadPointsFromFile":
            self.sigEventHandler.emit({"LoadPointsFromFile":[""]})

        elif btn.objectName() == "btnSavePointsToFile":
            self.sigEventHandler.emit({"SavePointsToFile":[""]})

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

            if k == "AddPoint":
                self.AppendPoint("P"+str(self.tblPointEditor.rowCount()))

            elif k == "RemovePoint":
                if self.tblPointEditor.rowCount() == 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Point editor has been empty"]})
                elif self.tblPointEditor.currentRow() < 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Please select the row will be removed"]})
                else:
                    # Remove current row
                    self.RemovePoint(self.tblPointEditor.item(self.tblPointEditor.currentRow(), 0).text())

            elif k == "ClearAll":
                if self.tblPointEditor.rowCount() == 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Point editor has been cleared"]})
                else:
                    self.ClearAllUserDefinedPoints()

            elif k == "LoadPointsFromFile":
                # Convert point editor to dictionary form
                dctPoints, Result = self.LoadPointsFromFile()
                if Result == 0:
                    self.MotionCtrl.Conn.SetPointDataBase(dctPoints)
                    self.ConvertDictToPointEditor(dctPoints, 1)

            elif k == "SavePointsToFile":
                # Check duplicated point name
                strDupPointName, lstDupRows = self.CheckDuplicatedPoints()
                if len(lstDupRows) > 1:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Found duplicated point name:{} at row:{}".format(strDupPointName, str(lstDupRows))]})
                # Check empty table
                elif self.tblPointEditor.rowCount() == 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Cannot save as empty point file"]})
                # Save to point file
                else:
                    self.SavePointsToFile(self.MotionCtrl.Conn.GetPointDataBase())

            elif k == "RenamePoint":
                dctPoints = self.ConvertPointEditorToDict()
                self.MotionCtrl.Conn.SetPointDataBase(dctPoints)

    def AppendPoint(self, PointName):
        # Convert to specified based coordination
        lstPoint = self.MotionCtrl.Conn.pTo(self.MotionCtrl.Conn._track, self.cboBase.currentText())
        # Add into point database
        self.MotionCtrl.Conn.pSet(PointName, lstPoint)

        # Add into point editor
        dctPoints = {PointName:lstPoint}
        self.ConvertDictToPointEditor(dctPoints, 0)
        log.debug("AppendPoint.PointDatabase:%s\r\n", dctPoints)

    def RemovePoint(self, PointName):
        # Remove from point database
        log.debug("PointName:%s\r\n", PointName)
        self.MotionCtrl.Conn.pClear(PointName)

        # Remove from point editor
        dctPoints = self.MotionCtrl.Conn.GetPointDataBase()
        self.ConvertDictToPointEditor(dctPoints, 1)
        log.debug("RemovePoint.PointDatabase:%s\r\n", dctPoints)

    def CheckDuplicatedPoints(self):
        lstDupRows = list()
        strDupPointName = ""
        for refRow in range(self.tblPointEditor.rowCount()):
            lstDupRows.clear()
            lstDupRows.append(refRow+1)
            for chkRow in range(refRow+1, self.tblPointEditor.rowCount()):
                if self.tblPointEditor.item(chkRow,0).text() == self.tblPointEditor.item(refRow,0).text():
                    lstDupRows.append(chkRow+1)
            if len(lstDupRows) > 1:
                strDupPointName = self.tblPointEditor.item(chkRow,0).text()
                log.debug("Found duplicated point name:%s at row:%s\r\n", strDupPointName, str(lstDupRows))
                break

        return strDupPointName, lstDupRows

    def ClearAllUserDefinedPoints(self):
        dctPoints = dict()
        pointDatabase = self.MotionCtrl.Conn.GetPointDataBase()
        for k, v in pointDatabase.items():
            # Filte out reserved points
            if (k in self.ReservedPointNames) or (k[0] == "#"):
                dctPoints[k] = v
        self.MotionCtrl.Conn.SetPointDataBase(dctPoints)
        self.ConvertDictToPointEditor(dctPoints, 1)

    def ConvertDictToPointEditor(self, dctPoints, IsOverWrite):
        self.RenameEventFilter = 1

        # Clear all rows
        if IsOverWrite:
            while self.tblPointEditor.rowCount():
                self.tblPointEditor.removeRow(0)
                log.debug("removeRow:%s\r\n", str(0))

        # Append rows
        row = self.tblPointEditor.rowCount()
        for ptName in dctPoints:
            # Filte out reserved points
            if (ptName in self.ReservedPointNames) or (ptName[0] == "#"):
                continue
            
            self.tblPointEditor.insertRow(row)
            self.tblPointEditor.setItem(row, 0, QTableWidgetItem(ptName))# Show point name
            itm = QTableWidgetItem(dctPoints[ptName][0])
            itm.setFlags(itm.flags() & ~(Qt.ItemIsEditable))
            self.tblPointEditor.setItem(row, 1, itm)# Show based coordination
            s = "{:.3f}".format(dctPoints[ptName][1])
            for v in dctPoints[ptName][2:]:
                s = s+", {:.3f}".format(v)
            itm = QTableWidgetItem(s)
            itm.setFlags(itm.flags() & ~(Qt.ItemIsEditable))
            self.tblPointEditor.setItem(row, 2, itm)# Show point value
            log.debug("insertRow:%s\r\n", str(row))
            row += 1
        log.debug("ConvertDictToPointEditor:%s\r\n", str(dctPoints))
        self.RenameEventFilter = 0

    def ConvertPointEditorToDict(self):
        dctPoints = dict()
        pointDatabase = self.MotionCtrl.Conn.GetPointDataBase()
        for k, v in pointDatabase.items():
            # Filte out reserved points
            if (k in self.ReservedPointNames) or (k[0] == "#"):
                dctPoints[k] = v

        for row in range(self.tblPointEditor.rowCount()):
            lstPoint = [self.tblPointEditor.item(row,1).text()]
            lstValues = self.tblPointEditor.item(row,2).text().split(",")
            for s in lstValues:
                lstPoint.append(float(s))
            dctPoints[self.tblPointEditor.item(row,0).text()] = lstPoint
        log.debug("ConvertPointEditorToDict:%s\r\n", str(dctPoints))
        return dctPoints

    def LoadPointsFromFile(self):
        dctPoints = dict()
        Result = -1

        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getOpenFileName(self, \
                    "Load Points From File", \
                    dctAPP_CFIG["SCRIPT_PATH"], \
                    "point location file (*.pt)", \
                    options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Load from filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += ".pt"
                with open(filePath) as ptFile: 
                    dctPoints = json.load(ptFile)
                    #ptFile.close()
                    Result = 0
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": ["Exception",str(e)]})
        finally:
            return dctPoints, Result

    def SavePointsToFile(self, dctPoints):
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getSaveFileName(self, \
                    "Save Points To File", \
                    dctAPP_CFIG["SCRIPT_PATH"], \
                    "point location file (*.pt)", \
                    options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Save to filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += ".pt"
                with open(filePath,'w') as ptFile:
                    json.dump(dctPoints, ptFile, ensure_ascii = False, indent = 4)
                    #ptFile.close()
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": ["Exception",str(e)]})
        finally:
            pass

#End of Class frmPointEditor




