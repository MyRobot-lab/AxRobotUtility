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
import sys, logging, math, time, random, os, copy, serial
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot, Qt
from AxRobotData import *
from frmPointEditor import *

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

# Global variable


# Flags Definition


class MotionMonitor(QObject):
    sigModle3dViewer = pyqtSignal(dict)
    sigMainWinEventHandler = pyqtSignal(dict)
    sigMotionMonitorProcess = pyqtSignal(dict)

    def __init__(self, MotionCtrl, parent=None):
        super(MotionMonitor, self).__init__(parent)
        self.MotionCtrl = MotionCtrl
        self.MotionData = MotionCtrl.MotionData
        self.Robot3dModelCreated = 0
        self.ledStatus = 0
        self.ledFlag = 0
        self.strMotionStatus = ""

        # Set logger level
        log.setLevel(self.MotionData.GetLogLevel())

        # Connect signal&slot paire
        self.sigMotionMonitorProcess.connect(self.MotionCtrl.sltMotionMonitorProcess)

        # Start Time Task
        self.TimeTaskState = -1
        self.TimeTask = QTimer()
        self.TimeTask.timeout.connect(self.TimeTickTask)

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        for k, v in dctEvents.items():
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

            if k == "Create3dModel":
                self.sigModle3dViewer.emit({"Create3dModle":""})
                self.Robot3dModelCreated = 1

    def BindModle3dViewer(self, pModle3dViewer):
        self.Modle3dViewer = pModle3dViewer

        # Connect signal&slot paire
        self.sigModle3dViewer.connect(self.Modle3dViewer.sltEventHandler)

    def StartTimeTickTask(self, ExePeriod):
        self.DivCnt_2sec = round(2000/ExePeriod)
        self.DivCnt_1sec = round(1000/ExePeriod)
        self.DivCnt_500msec = round(500/ExePeriod)
        self.TimeTaskCountDown = [0]*5
        self.TimeTask.start(ExePeriod)# Set execution time duration @ms
        self.TimeTaskState = 0
        log.debug("Start monitor time task\r\n")

    def TimeTickTask(self):
        if self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
            if self.MotionCtrl.SuspendRealTimeUpdate == 0:
                # Executeion @ 1sec
                if self.TimeTaskCountDown[0] != 0:
                    self.TimeTaskCountDown[0] -= 1
                elif self.MotionCtrl.UpdateMonitorReqCnt == 0:
                    self.MotionCtrl.UpdateMonitorReqCnt = 1
                    if self.TimeTaskState == 0:
                        self.sigMotionMonitorProcess.emit({"UpdataMotionParam":["cmdERR"]})
                        self.TimeTaskState = 1
                    else:
                        self.sigMotionMonitorProcess.emit({"UpdataServoParam":["iopPWR","iopTMP"]})
                        self.TimeTaskState = 0
                    self.TimeTaskCountDown[0] = self.DivCnt_1sec

                # Trigger to get motion data "_map[]"
                self.sigMotionMonitorProcess.emit({"UpdateMotionData":""})

            if self.MotionData.SystemState >= dctSYSTEM_STATE["SERVO_ON"]:
                # Do this at 3D model enabled only
                if self.Robot3dModelCreated != 0 and self.MotionCtrl.UpdateMotionDataCnt > 2:
                    import simu.pipeRobot
                    # Update "_map[]" to pipeRobot
                    for i in range(len(simu.pipeRobot._map)):
                        simu.pipeRobot._map[i] = self.MotionCtrl.Conn._map[i]
                    self.sigModle3dViewer.emit({"Update3dModle":""})

            self.UpdateRealTimeStatusParam()

            # Executeion @ 0.5sec
            if self.TimeTaskCountDown[1] != 0:
                self.TimeTaskCountDown[1] -= 1
            else:
                self.TimeTaskCountDown[1] = 1
                self.UpdateMotionStatusIndicatorLED()

            self.sigMainWinEventHandler.emit({"RealTimeStatusUpdate":[self.ledStatus, self.strMotionStatus]})

        # Executeion @ 1sec
        if self.TimeTaskCountDown[2] != 0:
            self.TimeTaskCountDown[2] -= 1
        else:
            self.sigMainWinEventHandler.emit({"SetStatusBar":""})
            self.TimeTaskCountDown[2] = self.DivCnt_1sec

    def UpdateRealTimeStatusParam(self):
        if self.MotionCtrl.Conn == None:
            return
        # Update Motion parameters
        self.MotionData.dctMotionParam["cmdVEL"]["Value"] = self.MotionCtrl.Conn._vel[1:]                      
        self.MotionData.dctMotionParam["cmdSPD"]["Value"] = self.MotionCtrl.Conn._spd[1:]                   
        self.MotionData.dctMotionParam["cmdTRQ"]["Value"] = self.MotionCtrl.Conn._trq[1:]
        self.MotionData.dctMotionParam["cmdAMP"]["Value"] = self.MotionCtrl.Conn._amp[1:] 
        self.MotionData.dctMotionParam["cmdACC"]["Value"] = self.MotionCtrl.Conn._acc[1:] 
        self.MotionData.dctMotionParam["cmdOUT"]["Value"] = self.MotionCtrl.Conn._out[1:] 
        self.MotionData.dctMotionParam["cmdMXD"]["Value"] = self.MotionCtrl.Conn._mxC[1:] 
        self.MotionData.dctMotionParam["cmdMXG"]["Value"] = self.MotionCtrl.Conn._mxG[1:]
        self.MotionData.dctMotionParam["cmdMXM"]["Value"] = self.MotionCtrl.Conn._mxM[1:] 
        self.MotionData.dctMotionParam["segSTS"]["Value"] = self.MotionCtrl.Conn._status

        # Diagnostic variables
        for i in range(len(self.MotionData.dctRtStatus["Segment"]["Value"])):
            self.MotionData.dctRtStatus["Segment"]["Value"][i] = self.MotionCtrl.Conn._map[i]
        if self.MotionData.SystemState >= dctSYSTEM_STATE["SERVO_ON"]:
            TcpVal = self.MotionCtrl.Conn.pTo(self.MotionCtrl.Conn._joint, RSVPT_WORK)
            TcpVal = ["{:.3f}".format(i) for i in TcpVal[1:]]
            self.MotionData.dctRtStatus["TCP"]["Value"] = TcpVal[:6]# 0.1%deg
        self.MotionData.dctRtStatus["Track"]["Value"] = self.MotionCtrl.Conn._track[1:]
        self.MotionData.dctRtStatus["Joint"]["Value"] = self.MotionCtrl.Conn._joint[1:]# 0.1%deg

        # Misc. variables
        self.MotionData.dctRtStatus["Diagnostic"]["Value"][0] = self.MotionCtrl.Conn.CommColiErr
        self.MotionData.dctRtStatus["Diagnostic"]["Value"][1] = self.MotionCtrl.Conn.SegLostErr
        self.MotionData.dctRtStatus["Diagnostic"]["Value"][2] = self.MotionCtrl.Conn.mm.PtCnvColiErr
        self.MotionData.dctRtStatus["Diagnostic"]["Value"][3] = self.MotionCtrl.Conn.mm.PtCnvErr
        self.MotionData.dctRtStatus["Diagnostic"]["Value"][4] = self.MotionCtrl.Conn.CommTimeOut
        self.MotionData.dctRtStatus["Diagnostic"]["Value"][5] = self.MotionCtrl.Conn.FoeTimeOut

    def UpdateMotionStatusIndicatorLED(self):
        # Decide LED status
        if self.MotionCtrl.Conn._map[5] == 0:# segMOD = 0, OFF
            self.strMotionStatus = "Ready"
            if self.ledFlag == 0:# Forward direction
                if self.ledStatus == 0x01:
                    self.ledStatus = 0x02
                elif self.ledStatus == 0x02:
                    self.ledStatus = 0x04
                else:
                    self.ledFlag = 1
            else:# Backward direction
                if self.ledStatus == 0x04:
                    self.ledStatus = 0x02
                elif self.ledStatus == 0x02:
                    self.ledStatus = 0x01
                else:
                    self.ledFlag = 0
        elif self.MotionCtrl.Conn._map[5] == 1:# segMOD = 1, Drag mode
            self.strMotionStatus = "Drag"
            self.ledStatus = 0x02
        elif self.MotionCtrl.Conn._map[5] == 2:# segMOD = 2, Teaching mode
            self.strMotionStatus = "Teaching"
            if self.ledStatus == 0x02:
                self.ledStatus = 0x06
            else:
                self.ledStatus = 0x02
        elif self.MotionCtrl.Conn._map[5] == 4:# segMOD = 4, Manual mode
            self.strMotionStatus = "Manual"
            if self.ledStatus == 0x01:
                self.ledStatus = 0x00
            else:
                self.ledStatus = 0x01
        else:# Otherwise
            if self.MotionCtrl.Conn._map[4] == 0:# Motion/Stop
                self.strMotionStatus = "Auto/Motion"
                if self.ledStatus == 0x04:
                    self.ledStatus = 0x06
                else:
                    self.ledStatus = 0x04
            elif self.MotionCtrl.Conn._map[4] == 1:# Recovery
                self.strMotionStatus = "Auto/Recovery"
                if self.ledStatus == 0x02:
                    self.ledStatus = 0x03
                else:
                    self.ledStatus = 0x02
            elif self.MotionCtrl.Conn._map[4] == 4:# Brake
                self.strMotionStatus = "Auto/Brake"
                self.ledStatus = 0x07
            elif self.MotionCtrl.Conn._map[4] == 9:# Alarm
                self.strMotionStatus = "Auto/Alarm"
                if self.ledStatus == 0x01:
                    self.ledStatus = 0x03
                else:
                    self.ledStatus = 0x01

        return self.ledStatus, self.strMotionStatus
#End of Class MotionMonitor
