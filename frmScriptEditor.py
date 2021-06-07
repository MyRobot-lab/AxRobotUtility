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
import sys, logging
from PyQt5.QtWidgets import QWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QFileInfo, pyqtSlot, pyqtSignal, Qt
from ui.frmScriptEditorUi import *
from AxRobotData import *

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

# Sharing data
RunScriptStateDef = {
    "Run"  : 1,
    "Stop" : 2,
    "Pause": 3,
}

class frmScriptEditor(QWidget, Ui_Form):
    sigEventHandler = pyqtSignal(dict)
    sigScriptProcess = pyqtSignal(list)

    def __init__(self, MotionCtrl, parent=None):
        super(frmScriptEditor, self).__init__(parent)

        # Init object point
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData

        # Init normal data
        self.CompiledScriptLines = list()
        self.lstScriptLines = list()
        self.RunScriptState = RunScriptStateDef["Stop"]
        self.DefaultSpeed = 0

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())

        # Init UI components
        self.setupUi(self)
        self.cboDefaultSpeed.addItems(["10","50","100","200","300"])
        self.cboDefaultSpeed.setCurrentText("100")

        # Connect signal&slot paire
        self.sigEventHandler.connect(self.sltEventHandler)# Establish internal event handling connectoin
        self.sigScriptProcess.connect(self.MotionCtrl.sltScriptProcess)# Establish ScriptProcess connection
        """
        self.tblScriptEditor.itemActivated.connect(self.sltTableHandler)
        """
        self.tblScriptEditor.itemClicked.connect(self.sltTableHandler)
#        self.tblScriptEditor.itemChanged.connect(self.sltTableHandler)
        """
        self.tblScriptEditor.itemDoubleClicked.connect(self.sltTableHandler)
        self.tblScriptEditor.itemPressed.connect(self.sltTableHandler)
        self.tblScriptEditor.itemEntered.connect(self.sltTableHandler)
        """
#        self.tblScriptEditor.cellActivated.connect(self.sltCellHandler)
        self.tblScriptEditor.cellChanged.connect(self.sltCellHandler)
#        self.tblScriptEditor.cellClicked.connect(self.sltCellHandler)
#        self.tblScriptEditor.cellDoubleClicked.connect(self.sltCellHandler)
#        self.tblScriptEditor.cellEntered.connect(self.sltCellHandler)
#        self.tblScriptEditor.cellPressed.connect(self.sltCellHandler)

        self.btnCompile.clicked.connect(self.sltPushButtonHandler)
        self.btnRun.clicked.connect(self.sltPushButtonHandler)
        self.btnRemoveLine.clicked.connect(self.sltPushButtonHandler)
        self.btnClearAll.clicked.connect(self.sltPushButtonHandler)
        self.btnLoadScriptFromFile.clicked.connect(self.sltPushButtonHandler)
        self.btnSaveScriptToFile.clicked.connect(self.sltPushButtonHandler)


            # Init ScriptEditor behavior
        hdr = self.tblScriptEditor.horizontalHeader()
        hdr.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tblScriptEditor.setShowGrid(False)
        self.tblScriptEditor.setSelectionBehavior(self.tblScriptEditor.SelectRows)
        """
        self.tblScriptEditor.setEditTriggers(self.tblScriptEditor.NoEditTriggers \
                                            | self.tblScriptEditor.AnyKeyPressed \
                                            | self.tblScriptEditor.CurrentChanged \
                                            | self.tblScriptEditor.DoubleClicked \
                                            | self.tblScriptEditor.EditKeyPressed \
                                            | self.tblScriptEditor.SelectedClicked \
                                            )
        """
        self.tblScriptEditor.setEditTriggers(self.tblScriptEditor.AllEditTriggers)
#        self.tblScriptEditor.setSelectionMode(self.tblScriptEditor.SingleSelection)
        self.tblScriptEditor.setSelectionMode(self.tblScriptEditor.NoSelection)

        # Init GUI status
        self.sigEventHandler.emit({"ClearAll":[""]})

    def sltCellHandler(self, r, c):
        global RunScriptState
        # log.debug("cell event @%d/%d, RunScriptState=%s\r\n", r, c, self.RunScriptState)
        if self.RunScriptState == RunScriptStateDef["Stop"]:
            self.sigEventHandler.emit({"Uncompiled":[""]})

    def sltTableHandler(self, item):
        global RunScriptStateDef
        log.debug("table event @%s\r\n", str(item))
        if self.RunScriptState == RunScriptStateDef["Pause"]:
            self.sigEventHandler.emit({"Continue":[""]})
        else:
            self.sigEventHandler.emit({"Pause":[""]})

    # def ItemkeyPressEvent(self, event):
    #     log.debug("Item key press event @%s\r\n", str(event.key()))

    #     # Delete selected empty row
    #     if event.key() == Qt.Key_Backspace:
    #         row = self.tblScriptEditor.currentRow()
    #         if row>=0 and self.tblScriptEditor.item(row, 0).text() == "":
    #             self.tblScriptEditor.removeRow(row)
    #             log.debug("Delete selected empty row2 %s\r\n", row)

    #     super(QTableWidgetItem, self).keyPressEvent(event)

    def keyPressEvent(self, event):
        log.debug("key press event @%s\r\n", str(event.key()))

        # Append new row
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.sigEventHandler.emit({"InsertNewLine":[""]})

        # Delete selected empty row
        elif event.key() == Qt.Key_Backspace:
            self.sigEventHandler.emit({"RemoveSpaceLine":[""]})

        super(frmScriptEditor, self).keyPressEvent(event)

    def SetGuiStatus(self, event):
        if event == "Run":
            self.btnCompile.setEnabled(False)
            self.btnRun.setEnabled(True)
            self.btnClearAll.setEnabled(False)
            self.btnRemoveLine.setEnabled(False)
            self.btnLoadScriptFromFile.setEnabled(False)
            self.btnSaveScriptToFile.setEnabled(False)
            self.tblScriptEditor.setEditTriggers(self.tblScriptEditor.NoEditTriggers)
            self.tblScriptEditor.setSelectionMode(self.tblScriptEditor.NoSelection)
            if self.tblScriptEditor.currentItem() != None:
                self.tblScriptEditor.currentItem().setSelected(False)
            self.btnRun.setText("Cancel")
            self.cboDefaultSpeed.setEnabled(False)
        elif event == "Ready":
            self.btnCompile.setEnabled(True)
            self.btnRun.setEnabled(True)
            self.btnClearAll.setEnabled(True)
            self.btnRemoveLine.setEnabled(True)
            self.btnLoadScriptFromFile.setEnabled(True)
            self.btnSaveScriptToFile.setEnabled(True)
            self.tblScriptEditor.setEditTriggers(self.tblScriptEditor.AllEditTriggers)
            self.tblScriptEditor.setSelectionMode(self.tblScriptEditor.SingleSelection)
            self.btnRun.setText("Run")
            self.cboDefaultSpeed.setEnabled(True)
        elif event == "Uncompiled":
            self.btnCompile.setEnabled(True)
            self.btnRun.setEnabled(False)
            self.btnClearAll.setEnabled(True)
            self.btnRemoveLine.setEnabled(True)
            self.btnLoadScriptFromFile.setEnabled(True)
            self.btnSaveScriptToFile.setEnabled(True)
            self.cboDefaultSpeed.setEnabled(True)
        elif event == "ClearAll":
            self.btnCompile.setEnabled(False)
            self.btnRun.setEnabled(False)
            self.btnClearAll.setEnabled(True)
            self.btnRemoveLine.setEnabled(True)
            self.btnSaveScriptToFile.setEnabled(False)
            self.btnLoadScriptFromFile.setEnabled(True)
            self.cboDefaultSpeed.setEnabled(True)

    @pyqtSlot()
    def sltPushButtonHandler(self):
        btn = self.sender()
        if btn.objectName() == "btnCompile":
            self.sigEventHandler.emit({"Compile":[""]})

        elif btn.objectName() == "btnRun":
            if btn.text() == "Run":
                self.sigEventHandler.emit({"Run":[""]})
            elif btn.text() == "Cancel":
                self.sigEventHandler.emit({"Cancel":[""]})

        elif btn.objectName() == "btnRemoveLine":
            self.sigEventHandler.emit({"RemoveSelectedLine":[""]})

        elif btn.objectName() == "btnClearAll":
            self.sigEventHandler.emit({"ClearAll":[""]})

        elif btn.objectName() == "btnLoadScriptFromFile":
            self.sigEventHandler.emit({"LoadScriptFromFile":[""]})

        elif btn.objectName() == "btnSaveScriptToFile":
            self.sigEventHandler.emit({"SaveScriptToFile":[""]})

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        global RunScriptStateDef
        for k, v in dctEvents.items():
            if k != "SetRowColor":
                log.debug("RxEvent:%s, %s\r\n", k, str(v))# For debug only

            if k == "Compile":
                if self.tblScriptEditor.rowCount() == 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                            ["Warning","Script editor is empty"]})
                else:
                    self.lstScriptLines = self.ConvertScriptEditorToList()
                    result, self.CompiledScriptLines, UnRecogLines = self.CompileScript(self.lstScriptLines)
                    if result < 0:
                        self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                            ["Error","Unrecognized commands @lines: {}".format(UnRecogLines)]})
                    else:
                        self.SetGuiStatus("Ready")

            elif k == "Run":
                if self.tblScriptEditor.rowCount() == 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Script editor is empty"]})
                elif len(self.CompiledScriptLines) <= 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Please compile the script before running"]})
                else:
                    self.RunScriptState = RunScriptStateDef["Run"]
                    self.SetGuiStatus(k)
                    # Get default speed setting
                    self.DefaultSpeed = int(self.cboDefaultSpeed.currentText())
                    self.sigScriptProcess.emit(self.CompiledScriptLines)

            elif k == "Ready" or k == "Cancel":
                self.RunScriptState = RunScriptStateDef["Stop"]
                self.SetGuiStatus(k)

            elif k == "Uncompiled":
                self.SetGuiStatus(k)

            elif k == "Pause":
                self.RunScriptState = RunScriptStateDef["Pause"]

            elif k == "Continue":
                self.RunScriptState = RunScriptStateDef["Run"]

            elif k == "ClearAll":
                self.ClearAllRows()
                # Clear compiled script
                self.CompiledScriptLines.clear()
                self.SetGuiStatus(k)

            elif k == "LoadScriptFromFile":
                # Convert script editor to list form
                self.lstScriptLines, Result = self.LoadScriptFromFile()
                if Result == 0:
                    self.ConvertListToScriptEditor(self.lstScriptLines, 1)
                    self.SetGuiStatus("Uncompiled")

            elif k == "SaveScriptToFile":
                self.lstScriptLines = self.ConvertScriptEditorToList()

                # Check empty script
                if len(self.lstScriptLines) == 0:
                    self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox": \
                        ["Warning","Cannot save as empty script file"]})
                # Save to script file
                else:
                    self.SaveScriptToFile(self.lstScriptLines)

            elif k == "SetRowColor":
                self.tblScriptEditor.item(v[0], 0).setBackground(v[1])

            elif k == "InsertNewLine":
                self.InsertNewLine()

            elif k == "RemoveSelectedLine":
                self.RemoveSelectedLine()

    def InsertNewLine(self):
        row = self.tblScriptEditor.currentRow()+1
        self.tblScriptEditor.insertRow(row)
        self.tblScriptEditor.setItem(row, 0, QTableWidgetItem(""))
        # self.tblScriptEditor.setCurrentItem(self.tblScriptEditor.item(row,0))
        # self.tblScriptEditor.item(row,0).setBackground(QtGui.QColor(222, 225, 227))
        self.tblScriptEditor.editItem(self.tblScriptEditor.item(row,0))
        log.debug("Append new row %s\r\n", row)

    def RemoveSelectedLine(self):
        log.debug("RemoveSelectedLine: %d\r\n", self.tblScriptEditor.currentRow())
        self.tblScriptEditor.removeRow(self.tblScriptEditor.currentRow())


    def RemoveSpaceLine(self):
        row = self.tblScriptEditor.currentRow()
        if row>=0 and self.tblScriptEditor.item(row, 0).text() == "":
            self.tblScriptEditor.removeRow(row)
            log.debug("RemoveSpaceLine: %d\r\n", row)

    def GetRunScriptState(self):
        return RunScriptState

    def ClearAllRows(self):
        # Clear all rows
        while self.tblScriptEditor.rowCount():
            self.tblScriptEditor.removeRow(0)
    
        # # Reserved one row
        # self.tblScriptEditor.insertRow(0)
        # self.tblScriptEditor.setItem(0, 0, QTableWidgetItem(""))

    def ConvertListToScriptEditor(self, lstScriptLines, IsOverWrite):
        if IsOverWrite:
            # Clear all rows
            while self.tblScriptEditor.rowCount():
                self.tblScriptEditor.removeRow(0)

        # Append rows
        row = self.tblScriptEditor.rowCount()
        for line in lstScriptLines:
            self.tblScriptEditor.insertRow(row)
            self.tblScriptEditor.setItem(row, 0, QTableWidgetItem(str(line)))
            log.debug("ConvertListToScriptEditor: insertRow[%s]: %s\r\n", str(row), line)
            row += 1

    def ConvertScriptEditorToList(self):
        lstScriptLines = list()
        for row in range(self.tblScriptEditor.rowCount()):
            lstScriptLines.append(self.tblScriptEditor.item(row,0).text())
        log.debug("ConvertScriptEditorToList:%s, %d\r\n", str(lstScriptLines), len(lstScriptLines))
        return lstScriptLines

    #############################################################
    # General format     : [strCmd, strParam0, strParam1..strParamN]
    # Move joint command : ["MOVJNT", "J1=90", "J2=30", "J7=80", "SPD=100", "ACC=100"]
    # Move point command : ["MOVPT", "P1", "P3", "P2, P1", "SPD=100", "ACC=100"]
    # Move line command  : ["MOVLN", "P1", "P2", "P3", "SPD=100", "ACC=100"]
    # Delay command(ms)  : ["DELAY", "10"]
    # Loop command(ms)   : ["LOOP", "10"], ["ENDLOOP"]
    # Comment            : ["#", "comment description"]
    #############################################################
    def CompileScript(self, lstScriptLines):
        Result = -1
        CompiledScriptLines = list()

        # Check empty script
        if len(lstScriptLines) == 0:
            return Result, CompiledScriptLines
        
        LoopCmdStack = list()
        UnrecognizedLines = list()
        UnrecognizedLines.clear()

        # Parsing each command line
        for ln in range(len(lstScriptLines)):
            # Convert to upper case
            line = lstScriptLines[ln].upper()

            # Split into fields
            fields = line.split()

            # Skip empty line
            if len(fields) == 0:
                continue

            for fn in range(len(fields)):
                fields[fn].strip()

            # Parsing each fields
            if fields[0] == "MOVJNT":
                # Check parameter
                if len(fields[1:]) != 0:
                    for fn in range(1,len(fields)):
                        subfields = fields[fn].split("=")
                        if fields[fn][0] == "#":# Ignore comment
                            fields = fields[:fn]
                            break
                        elif len(subfields) == 2:# Check subfields
                            if (len(subfields[0])>1) and subfields[0][0] == "J":# Get joint number
                                # Joint number and angle limitation
                                if int(subfields[0][1:]) <= 8 and abs(int(subfields[1])) <= 180:
                                    continue
                            elif subfields[0] == "SPD":# Get specified speed
                                # Speed limitation
                                if abs(int(subfields[1])) <= 1000:
                                    continue
                            elif subfields[0] == "ACC":# Get specified acceleration
                                # Acceleration limitation
                                if abs(int(subfields[1])) <= 1000:
                                    continue
                        UnrecognizedLines.append(ln+1)
                        break
                else:
                    UnrecognizedLines.append(ln+1)

            elif fields[0] == "MOVPT" or fields[0] == "MOVLN":
                # Check parameter
                if len(fields[1:]) != 0:
                    for fn in range(1,len(fields)):
                        subfields = fields[fn].split("=")
                        if fields[fn][0] == "#":# Ignore comment
                            fields = fields[:fn]
                            break
                        elif len(subfields) == 1:
                            if self.CheckPointExist(fields[fn]) == True:# Check point name
                                continue
                        elif len(subfields) == 2:# Check subfields
                            if subfields[0] == "SPD":# Get specified speed
                                # Speed limitation
                                if abs(int(subfields[1])) <= 1000:
                                    continue
                            elif subfields[0] == "ACC":# Get specified acceleration
                                # Acceleration limitation
                                if abs(int(subfields[1])) <= 1000:
                                    continue
                        UnrecognizedLines.append(ln+1)
                        break
                else:
                    UnrecognizedLines.append(ln+1)

            elif fields[0] == "DELAY":
                # Check parameter
                if len(fields) < 2 or fields[1].isnumeric() == False:
                    UnrecognizedLines.append(ln+1)
                elif len(fields) > 2 and fields[2][0] != "#":
                    UnrecognizedLines.append(ln+1)
                else:
                    fields[1] = int(fields[1])
                    # Cut off useless part
                    fields = fields[:2]

            elif fields[0] == "LOOP":
                # Check parameter
                if len(fields) < 2 or fields[1].isnumeric() == False:
                    UnrecognizedLines.append(ln+1)
                elif len(fields) > 2 and fields[2][0] != "#":
                    UnrecognizedLines.append(ln+1)
                else:
                    # Cut off useless part
                    fields = fields[:2]

                    # Push loop count and line number into stack
                    LoopCmdStack.append([fields[1], ln])
                    fields[1] = int(fields[1])
                    fields.append(0)# Append fields[2] to save "LOOPEND" line number

            elif fields[0] == "LOOPEND":
                # Check parameter
                if len(fields) > 1 and fields[1][0] != "#":
                    UnrecognizedLines.append(ln+1)
                else:
                    # Cut off useless part
                    fields = fields[:1]

                    # Pop loop count and line number into stack
                    fields.append(int(LoopCmdStack[len(LoopCmdStack)-1][0]))#loop count
                    fields.append(int(LoopCmdStack[len(LoopCmdStack)-1][1]))#loop start line
                    LoopCmdStack.pop(len(LoopCmdStack)-1)

                    # Save back LOOPEND line
                    CompiledScriptLines[fields[2]][2] = ln

            elif fields[0][0] == "#":
                pass

            else:
                UnrecognizedLines.append(ln+1)
            log.debug("Compiled line[%d]: cmd=%s, param=%s\r\n", ln+1, fields[0], str(fields[1:]))

            CompiledScriptLines.append(fields)
        # End of lines parsing

        # Check LOOP command paires
        if len(LoopCmdStack) != 0:
            UnrecognizedLines.append(int(LoopCmdStack[0][0])+1)
            log.debug("Non-emptied LoopCmdStack[]: %s\r\n", str(LoopCmdStack))

        if len(UnrecognizedLines) == 0:
            Result = 0
        else:
            CompiledScriptLines.clear()

        return Result, CompiledScriptLines, UnrecognizedLines

    def LoadScriptFromFile(self):
        Result = -1
        lstScriptLines = list()
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getOpenFileName(self, \
                    "Load Script From File", \
                    dctAPP_CFIG["SCRIPT_PATH"], \
                    "motion script file (*.ms)", \
                    options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Load from filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += ".ms"
                f = open(filePath, "r")
                # Remove non-printable characters
                lstScriptLines = self.FilterOutNonPrintableChar(f.readlines())
                f.close()
                Result = 0
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", str(e)]})
        finally:
            return lstScriptLines, Result

    def SaveScriptToFile(self, lstScriptLines):
        opt = QFileDialog.Options()
        opt |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getSaveFileName(self, \
                    "Save Script To File", \
                    dctAPP_CFIG["SCRIPT_PATH"], \
                    "motion script file (*.ms)", \
                    options=opt)

            fileName = QFileInfo(filePath).fileName().split(".")
            log.debug("Save to filePath:%s, fileName:%s\r\n", filePath, fileName)
            if filePath != "" and fileName != "":
                if len(fileName) < 2:
                    filePath += ".ms"
                f = open(filePath, "w")
                for line in lstScriptLines:
                    f.write(line+"\n")
                f.close()
        except Exception as e:
            self.MotionCtrl.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", str(e)]})
        finally:
            pass

    def FilterOutNonPrintableChar(self, lines):
        for ln in range(len(lines)):
            filtedLine = ""
            for c in lines[ln]:
                if c.isprintable():
                    filtedLine += c
            lines[ln] = filtedLine
        return lines

    def CheckPointExist(self, PointName):
        return self.MotionCtrl.Conn.pExist(PointName)

#End of Class frmScriptEditor