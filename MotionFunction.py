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
import sys, logging, math, time, random, os, copy, serial, datetime, inspect, numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot, Qt
from AxRobotData import *
import escMotion

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

class MotionCtrl(QObject):
    def __init__(self, MotionData, parent=None):
        super(MotionCtrl, self).__init__(parent)
        self.MotionData = MotionData
        self.Conn = None
        self.UpdateMonitorReqCnt = 0
        self.UpdateMotionDataCnt = 0
        self.SuspendRealTimeUpdate = 0

    def GetMsgWithLineNumber(self, e):
        retStr = "@"+__name__+"/line("+str(inspect.currentframe().f_back.f_lineno)+"): "+str(e)
        return retStr

############ For MainWin
    sigMainWinEventHandler = pyqtSignal(dict)
    def sltMainWinProcess(self, dctCmd):
        pass


############ For MotionMonitor
    sigMotionMonitorEventHandler = pyqtSignal(dict)
    def BindMotionMonitor(self, pMotionMonitor):
        self.MotionMonitor = pMotionMonitor
        self.sigMotionMonitorEventHandler.connect(pMotionMonitor.sltEventHandler)

    @pyqtSlot(dict)
    def sltMotionMonitorProcess(self, dctCmd):
        for k, v in dctCmd.items():
            if k == "UpdateMotionData" and self.SuspendRealTimeUpdate==0 and \
                self.MotionData.SystemState >= dctSYSTEM_STATE["SERVO_ON"]:
                try:
                    self.Conn.doUpdate()
                    if self.UpdateMotionDataCnt <= 1000:
                        self.UpdateMotionDataCnt += 1
                    time.sleep(0.001)
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    self.sltStartUpProcess({"Disconnect":[""]})
                    break
                finally:
                    pass
            elif k == "UpdataMotionParam" and self.SuspendRealTimeUpdate==0 and \
                self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
                if self.UpdateMonitorReqCnt == 0:
                    continue
                try:
                    for mv in v:
                        if mv not in self.MotionData.dctMotionParam:
                            continue
                        pk = self.MotionData.dctMotionParam[mv]
                        if isinstance(pk["Value"], list) == True:
                            rv = self.Conn.segR(mv)
                            for i in range(len(pk["Value"])):
                                pk["Value"][i] = int(rv[i])
                        else:
                            pk["Value"] = int(self.Conn.getR(mv))
                        time.sleep(0.001)
                    # End of loop
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass
                self.UpdateMonitorReqCnt = 0
            elif k == "UpdataServoParam" and self.StartUp.OnlineServoCount!=0 and self.SuspendRealTimeUpdate==0 and \
                self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
                if self.UpdateMonitorReqCnt == 0:
                    continue
                try:
                    for sv in v:
                        if sv not in self.MotionData.dctServoParam:
                            continue
                        for i in range(self.StartUp.OnlineServoCount):
                            # Set axis id
                            self.Conn.setAxis(i+1)
                            time.sleep(0.001)
                            rv = self.Conn.getSDO(sv)
                            self.MotionData.dctServoParam[sv]["Value"][i] = int(rv)

                    # End of loop
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass
                self.UpdateMonitorReqCnt = 0
############ For StartUp
    sigStartUpEventHandler = pyqtSignal(dict)
    def BindStartUp(self, pStartUp):
        self.StartUp = pStartUp
        self.sigStartUpEventHandler.connect(pStartUp.sltEventHandler)

    @pyqtSlot(dict)
    def sltStartUpProcess(self, dctCmd):
        import AxRobotData
        for k, v in dctCmd.items():
            if (k == "Connect" or k == "Reconnect") and self.MotionData.SystemState == dctSYSTEM_STATE["DISCONNECTED"]:
                try:
                    # Establish connection
                    AxRobotData.esc = None
                    if k == "Reconnect" and self.StartUp.ConnectedPortName != "":
                        # Show progress box
                        self.sigMainWinEventHandler.emit({"SetProgressBox": \
                            ["Open", "Reconnecting to {}, Please Wait!".format(self.StartUp.ConnectedPortName)]})
                        for t in range(50):# Timeout = 5 sec
                            for sp in serial.tools.list_ports.comports():
                                if sp.device == self.StartUp.ConnectedPortName:
                                    AxRobotData.esc = escMotion.ESC(self.StartUp.ConnectedPortName, False)
                                    log.debug("Reconnect to port %s\r\n", self.StartUp.ConnectedPortName)
                                    break
                            if AxRobotData.esc != None:
                                break
                            time.sleep(0.1)
                    else:
                        # Show progress box
                        self.sigMainWinEventHandler.emit({"SetProgressBox": \
                            ["Open", "Connecting to {}, Please Wait!".format(v[0])]})
                        AxRobotData.esc = escMotion.ESC(v[0], False)
                    if AxRobotData.esc == None:
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Warning", "Fail to connect to "+v[0]]})
                        break
                    self.Conn = AxRobotData.esc

                    self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 20]})
                    exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"escTest0.py","rb").read(), globals())
                    if ecatDeviceN !=0 :
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 40]})    
                        exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"sdoTest0.py","rb").read(), globals())
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 60]}) 
                        exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"pdoTest0.py","rb").read(), globals())
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 80]}) 
                    log.debug("ecatDeviceN:%d, ecatServoN=%d\r\n", ecatDeviceN, ecatServoN)

                    # Save result
                    self.StartUp.OnlineDeviceCount = ecatDeviceN
                    self.StartUp.OnlineServoCount = self.StartUp.OnlineDeviceCount
                    self.MotionData.SystemState = dctSYSTEM_STATE["CONNECTED"]
                    #self.MotionData.SystemState = dctSYSTEM_STATE["SERVO_OFF"]
                    self.SuspendRealTimeUpdate = 0
                    self.UpdateMonitorReqCnt = 0
                    self.StartUp.ConnectedPortName = v[0]
                    self.StartUp.ConnectStartTime = datetime.datetime.now()
                    # import simu.pipeRobot
                    # simu.pipeRobot._map = self.Conn._map

                    # Notify establish connection has success
                    self.sigMainWinEventHandler.emit({"StatusChange":""})
                    self.sigStartUpEventHandler.emit({"StatusChange":""})
                    self.sigUpgradeEventHandler.emit({"StatusChange":["Ready"]})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass

            elif k == "Disconnect" and self.MotionData.SystemState >= dctSYSTEM_STATE["CONNECTED"]:
                try:
                    # Change status first
                    self.StartUp.OnlineDeviceCount = 0
                    self.StartUp.OnlineServoCount = 0
                    self.SuspendRealTimeUpdate = 1
                    self.MotionData.SystemState = dctSYSTEM_STATE["DISCONNECTED"]
                    # self.StartUp.ConnectedPortName = v[0]
                    self.StartUp.ConnectStartTime = None
                    self.MotionDataUpdatedState = 0

                    if self.Conn != None:
                        self.Conn.com.close()
                        time.sleep(0.1)
                        del self.Conn
                        self.Conn = None
                        AxRobotData.esc = None
                        log.debug("delete ""ESC"" object done\r\n")

                    # Notify establish connection has success
                    self.sigMainWinEventHandler.emit({"StatusChange":""})
                    self.sigStartUpEventHandler.emit({"StatusChange":""})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass
            elif k == "ServoOn" and self.MotionData.SystemState < dctSYSTEM_STATE["SERVO_ON"]:
                try:
                    # Show progress box
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Turning Servo ON, Please Wait!"]})

                    self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 20]})
                    exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"drvTest0.py","rb").read(), globals())
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 40]})
                    exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"movTest0.py","rb").read(), globals())
                    if v[1] == True:# Enable extForce mode
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 60]})
                        exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"extTest0.py","rb").read(), globals())
                        self.Conn.putR("almENB", 1)
                        self.Conn.segR("drvOLD",["",0,0,0,0,0,0,0])
                        self.MotionData.extForceEnabled = 1
                    else:
                        self.Conn.putR("cmdMXC", 1000)
                        self.Conn.putR("extENB", 0)
                        self.Conn.segR("drvOLD",["",1,1,1,1,1,1,1])
                        self.MotionData.extForceEnabled = 0

                    # Update result
                    self.MotionData.SystemState = dctSYSTEM_STATE["SERVO_ON"]

                    # Notify establish connection has success
                    self.sigMainWinEventHandler.emit({"StatusChange":""})
                    self.sigStartUpEventHandler.emit({"StatusChange":""})
                    if v[0] == True and self.MotionMonitor.Robot3dModelCreated == 0:
                        time.sleep(0.5)
                        self.sigMotionMonitorEventHandler.emit({"Create3dModel":[""]})

                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass
            elif k == "ServoOff" and self.MotionData.SystemState >= dctSYSTEM_STATE["SERVO_ON"]:
                try:
                    # Show progress box
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Turning Servo OFF, Please Wait!"]})

                    self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 20]})
                    exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"offTest0.py","rb").read(), globals())
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 50]})

                    # Update result
                    self.MotionData.SystemState = dctSYSTEM_STATE["SERVO_OFF"]

                    # Notify establish connection has success
                    self.sigMainWinEventHandler.emit({"StatusChange":""})
                    self.sigStartUpEventHandler.emit({"StatusChange":""})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass
        # End of event loop
        # Close progress box
        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
        time.sleep(1)
        self.sigMainWinEventHandler.emit({"SetProgressBox":["Close"]})

############ For ParamViewer
    sigParamViewerEventHandler = pyqtSignal(dict)
    def BindParamViewer(self, pParamViewer):
        self.ParamViewer = pParamViewer
        self.sigParamViewerEventHandler.connect(pParamViewer.sltEventHandler)

# dctCmd general format:
# {"MotionWrite": [StartName, ItemCount]} : Write multiple data with start parameter name
# {"MotionRead" : [StartName, ItemCount]} : Read multiple data with start parameter name
    @pyqtSlot(dict)
    def sltParamViewerProcess(self, dctCmd):
        self.SuspendRealTimeUpdate = 1
        for k, v in dctCmd.items():
            if k == "MotionWrite":
                pass
            elif k == "MotionRead":
                if v[0].isnumeric() == False:
                    itemCnt = v[1]
                    found = 0
                    try:
                        # Clear progress box and show out
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Uploading, Please Wait!"]})
                        for pk, pv in self.MotionData.dctMotionParam.items():
                            # Ignore unavailable items
                            if (pk[:3] == "blk") or (pk not in self.Conn.mapVar):
                                continue
                            # Find parameter name
                            if pk == v[0] or found == 1:
                                found = 1
                                # Check stop reading 
                                if itemCnt <= 0:
                                    break
                                itemCnt -= 1
                                # log.debug("MotionRead: %s\r\n", pk)
                                if isinstance(pv["Value"], list) == True:
                                    rv = self.Conn.segR(pk)
                                    for i in range(len(pv["Value"])):
                                        pv["Value"][i] = int(rv[i])
                                else:
                                    pv["Value"] = int(self.Conn.getR(pk))
                                time.sleep(0.001)
                                # Notify ParameterViewer to update table 
                                self.sigParamViewerEventHandler.emit({"UpdateMotionParams":[pk, 1]})
                                # Update progress box 
                                self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", int(100*(v[1]-itemCnt)/v[1])]})
                        # End of dctMotionParam loop
                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass
            elif k == "ServoWrite":
                pass
            elif k == "ServoRead":
                # Get online number of servo driver
                if self.StartUp.OnlineServoCount == 0:# Skip process if no servo be found
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Warning", "No available servo be found!"]})
                    continue
                if v[0].isnumeric() == False:
                    itemCnt = v[1]
                    found = 0
                    try:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Uploading, Please Wait!"]})
                        for pk, pv in self.MotionData.dctServoParam.items():
                            # Ignore unavailable items
                            if (pk not in self.Conn.sdoVar) or (pk[:3] == "blk"):
                                continue
                            # Find parameter name
                            if pk == v[0] or found == 1:
                                found = 1
                                # Check stop reading 
                                if itemCnt <= 0:
                                    break
                                itemCnt -= 1
                                for i in range(self.StartUp.OnlineServoCount):
                                    # Set axis id
                                    self.Conn.setAxis(i+1)
                                    rv = self.Conn.getSDO(pk)
                                    pv["Value"][i] = int(rv)
                                    time.sleep(0.001)
                                # Notify ParameterViewer to update table 
                                self.sigParamViewerEventHandler.emit({"UpdateServoParams":[pk, 1]})
                                # Update progress box 
                                self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", int(100*(v[1]-itemCnt)/v[1])]})
                                # log.debug("sltParamViewerProcess.ServoRead: %s, %s\r\n", pk, str(pv["Value"]))
                        # End of dctServoParam loop
                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass
            # End of event loop
            # Close progress box
            self.sigMainWinEventHandler.emit({"SetProgressBox":["Close"]})
        self.SuspendRealTimeUpdate = 0
        self.sigParamViewerEventHandler.emit({"Ready":""})
############ For PointEditor
    sigPointEditorEventHandler = pyqtSignal(dict)
    def BindPointEditor(self, pPointEditor):
        self.PointEditor = pPointEditor
        self.sigPointEditorEventHandler.connect(pPointEditor.sltEventHandler)

    @pyqtSlot(dict)
    def sltPointEditorProcess(self, dctCmd):
        pass

############ For MotionTuner
    sigMotionTunerEventHandler = pyqtSignal(dict)
    def BindMotionTuner(self, pMotionTuner):
        self.MotionTuner = pMotionTuner
        self.sigMotionTunerEventHandler.connect(pMotionTuner.sltEventHandler)

    @pyqtSlot(dict)
    def sltMotionTunerEvent(self, dctCmd):
        for k, v in dctCmd.items():
            if k == "CollisionTest":
                log.debug("CollisionTest: %s\r\n", str(v))
                self.Conn.putR("m@.map.drvTRQ", v[0])
                time.sleep(0.1)
                self.Conn.putR("m@.map.drvTRQ", 0)

    @pyqtSlot(dict)
    def sltMotionTunerProcess(self, dctCmd):
        self.SuspendRealTimeUpdate = 1
        tuner = self.MotionTuner
        dctMotionParam = self.MotionData.dctMotionParam
        for k, v in dctCmd.items():
            if k == "GravityDistribution":
                log.debug("GravityDistribution: %s\r\n", str(v))
                dctCfg = self.MotionTuner.dctConfig["Gravity"]
                datlen = 361
                try:
                    # # Show progress box
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Calculating gravity distribution, Please Wait!"]})

                    self.Conn.pSet("tool",["robot",0.,0.,0.,0.,0.,0.,0.])
                    self.Conn.pSet("base",["world",0.,0.,0.,0.,0.,0.,0.]); self.Conn.modelToolM([1, dctCfg["ToolWeight"], 0, 0, 0])
                    tuner.AxisX = np.zeros(datlen)
                    tuner.lstData.clear()
                    tuner.lstData.append(np.zeros(datlen))
                    tuner.lstData.append(np.zeros(datlen))
                    tuner.lstData.append(np.zeros(datlen))
                    tuner.lstData.append(np.zeros(datlen))
                    tuner.lstData.append(np.zeros(datlen))
                    tuner.lstData.append(np.zeros(datlen))
                    tuner.lstData.append(np.zeros(datlen))
                    log.debug("Test Condition: ToolWeight=%d, AxisX=%d, channel number=%d\r\n", \
                            dctCfg["ToolWeight"], \
                            len(tuner.AxisX), \
                            len(tuner.lstData))

                    for i in range(datlen):
                        self.Conn.pSet("base",["world",0.,0.,500.,0.,90.,0.,0.]); self.Conn.modelToolM([1, dctCfg["ToolWeight"], 0, 0, 0])
                        tuner.AxisX[i]=i-180; p=[tuner.AxisX[i], 90, 0, 0, 0, 0, 0]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        self.Conn.pSet("base",["world",0.,0.,50.,0.,0.,0.,0.]); self.Conn.modelToolM([1, dctCfg["ToolWeight"],0,0,0]);
                        tuner.lstData[0][i]=d[0]; p=[0,tuner.AxisX[i], 0, 0, 0, 0, 0]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        tuner.lstData[1][i]=d[1]; p=[0,90,tuner.AxisX[i],90, 0, 0, 0]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        tuner.lstData[2][i]=d[2]; p=[0, 0, 0,tuner.AxisX[i], 0, 0, 0]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        tuner.lstData[3][i]=d[3]; p=[0, 0, 0,90,tuner.AxisX[i],90, 0]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        tuner.lstData[4][i]=d[4]; p=[0, 0, 0, 0, 0,tuner.AxisX[i], 0]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        tuner.lstData[5][i]=d[5]; p=[0, 0, 0, 0, 0,90,tuner.AxisX[i]]; d=self.Conn.getM(20,p); d=self.Conn.getM(21); d=self.Conn.getM(22);
                        tuner.lstData[6][i]=d[6]
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", (i*100)/datlen]})

                    # Show result plot
                    tuner.lstCurveLabels = ["mxG[1]({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "mxG[2]({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "mxG[3]({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "mxG[4]({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "mxG[5]({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "mxG[6]({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "mxG[7]({})".format(dctMotionParam["cmdMXG"]["Unit"])]
                    tuner.lstCurveColors = ["red", "green", "blue", "black", "red", "green", "blue"]
                    self.sigMotionTunerEventHandler.emit({"ShowPlot":[""]})

                    # # Notify establish connection has success
                    # self.sigMainWinEventHandler.emit({"StatusChange":""})
                    # self.sigStartUpEventHandler.emit({"StatusChange":""})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["Close"]})
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                # Close progress box
                self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                self.sigMainWinEventHandler.emit({"SetProgressBox":["Close"]})

            elif k == "GravityFactorMeasure":
                log.debug("GravityFactorMeasure: %s\r\n", str(v))
                dctCfg = self.MotionTuner.dctConfig["Gravity"]
                try:
                    # # Show progress box
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Turning Servo OFF, Please Wait!"]})
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 20]})
                    # Setup points for test
                    self.Conn.pSet('#p1',['joint',   0,   0,   0,   0,   0,   0,   0])
                    self.Conn.pSet('#p2',['joint',   0,   0,   0,   0,   0,   0,   0])
                    pt = ['joint', 0, 0, 0, 0, 0, 0, 0]
                    pt[tuner.AxisId] = tuner.Angle
                    self.Conn.pSet('#p3', pt)

                    # Setup test parameters
                    self.Conn.putR("m0.map.cmdMXC", 1000)
                    self.Conn.putR("m0.map.extENB", 1)

                    self.Conn.setAxis(tuner.AxisId)
                    self.Conn.putR("m@.map.extKV", [0, 0])
                    self.Conn.putR("m@.map.extKS", [0, 0])
                    self.Conn.putR("m@.map.extKG", [0, 0, 0])

                    spdlmt = ["", 500, 500, 500, 500, 500, 500, 500]
                    spdlmt[tuner.AxisId] = dctCfg["SpeedLimit"]
                    self.Conn.segR("drvSPD", spdlmt)

                    self.Conn.putR("m@.map.drvOLD", 1)# Disable Ext.Force

                    self.Conn.putR("m@.simTRQ", 0)
                    self.Conn.putR("m@.simKP" , 250)
                    self.Conn.putR("m@.simKV" , 10000)
                    self.Conn.putR("m@.simKG" , 1000)
                    self.Conn.putR("m@.simKM" , 200)
                    self.Conn.putR("m@.simKA" , 50)
                    self.Conn.putR("m@.simKS" , 50)
                    self.Conn.putR("m@.simKS0", 200)

                    dctCfg["SamplingTime"] = int(1300/dctCfg["Speed"])
                    log.debug("Joint=%d, spd=%d, dT=%d\r\n", tuner.AxisId, dctCfg["Speed"], dctCfg["SamplingTime"])

                    self.Conn.put("dasCH=6,m@.map.cmdANG,m@.map.cmdMXM,m@.map.cmdAMP,m@.map.cmdOUT,m@.map.cmdACC,m@.map.cmdVEL")

                    self.Conn.pMoveTo("#p2");     time.sleep(0.5)
                    self.Conn.dasStart(dctCfg["SamplingTime"])# Start DAS
                    self.Conn.pMoveTo("#p3", dctCfg["Speed"]); time.sleep(0.2)
                    self.Conn.pMoveTo("#p2", dctCfg["Speed"]); time.sleep(0.2)
                    tuner.DataLength=self.Conn.dasStop(); log.debug("n=%d\r\n",tuner.DataLength)
                    self.Conn.pMoveTo("#p1"); time.sleep(0.5)

                    # Get data result
                    tuner.lstData.clear()
                    tuner.lstData.append(self.Conn.dasGet(1, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(2, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(3, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(4, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(5, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(6, tuner.DataLength))
                    tuner.AxisX = np.linspace(0, tuner.DataLength*dctCfg["SamplingTime"], tuner.DataLength, endpoint = True)
                    tuner.AxisX = tuner.AxisX[0 : len(tuner.lstData[0])]

                    # Get cmdMXM value
                    for i in range(tuner.DataLength):
                        d=(tuner.lstData[1][i]>>16)&0xffff;
                        if (d&0x8000)>0: d-=0x10000;
                        tuner.lstData[1][i]=d

                    # Filter out useful data at constant velocity zone 
                    num=0; mxG=0; trq=0; thd=int(max(tuner.lstData[5])*9/10)
                    for j in range(tuner.DataLength):
                        if tuner.lstData[5][j]>thd:
                            num+=1; mxG+=tuner.lstData[1][j]; trq+=tuner.lstData[2][j]
                        if tuner.lstData[5][j]<-thd:
                            num+=1; mxG+=tuner.lstData[1][j]; trq+=tuner.lstData[2][j]
                    if num>0:
                        mxG=mxG/num; trq=trq/num
                    kG=int(trq*1000/mxG);
                    log.debug("n=%d, kG=%d, mxG=%d, trq=%d\r\n",num,kG,int(mxG),int(trq))

                    tuner.lstMeasuredGravityFactor[tuner.AxisId-1] = kG
                    tuner.SampledPoints[tuner.AxisId-1] = num
                    tuner.AverageGravity[tuner.AxisId-1] = int(mxG)
                    tuner.AverageTorque[tuner.AxisId-1] = int(trq)

                    # Show result plot
                    tuner.lstCurveLabels = ["cmdANG({})".format(dctMotionParam["cmdANG"]["Unit"]), \
                                        "cmdMXG({})".format(dctMotionParam["cmdMXG"]["Unit"]), \
                                        "cmdAMP({})".format(dctMotionParam["cmdAMP"]["Unit"]), \
                                        "cmdOUT({})".format(dctMotionParam["cmdOUT"]["Unit"]), \
                                        "cmdACC({})".format(dctMotionParam["cmdACC"]["Unit"]), \
                                        "cmdVEL({})".format(dctMotionParam["cmdVEL"]["Unit"])]
                    tuner.lstCurveColors = ["red", "green", "blue", "black", "red", "green"]
                    self.sigMotionTunerEventHandler.emit({"UpdateGravityTest":[""]})
                    self.sigMotionTunerEventHandler.emit({"ShowPlot":[""]})
                    # # Notify establish connection has success
                    # self.sigMainWinEventHandler.emit({"StatusChange":""})
                    # self.sigStartUpEventHandler.emit({"StatusChange":""})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass

            elif k == "FrictionFactorMeasure":
                log.debug("FrictionFactorMeasure: %s\r\n", str(v))
                dctCfg = self.MotionTuner.dctConfig["Friction"]
                try:
                    # # Show progress box
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Turning Servo OFF, Please Wait!"]})
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 20]})
                    # Setup points for test
                    self.Conn.pSet('#p1',['joint',   0,   0,   0,   0,   0,   0,   0])
                    pt2 = ['joint', 0, 0, 0, 0, 0, 0, 0]
                    pt2[tuner.AxisId] = tuner.Angle
                    self.Conn.pSet('#p2', pt2)
                    pt3 = ['joint', 0, 0, 0, 0, 0, 0, 0]
                    pt3[tuner.AxisId] = -tuner.Angle
                    self.Conn.pSet('#p3', pt3)
                    log.debug("tuner Condition: SampleTime=%d\r\n", dctCfg["SamplingTime"])

                    # Setup test parameters
                    self.Conn.putR("m0.map.cmdMXC", 1000)
                    self.Conn.putR("m0.map.extENB", 1)

                    self.Conn.setAxis(tuner.AxisId)
                    self.Conn.putR("m@.map.extKV", [0, 0])
                    self.Conn.putR("m@.map.extKS", [0, 0])
                    self.Conn.putR("m@.map.extKG", self.MotionTuner.dctConfig["Gravity"]["InitialGravityFactor"][tuner.AxisId-1])
                    self.Conn.putR("m@.map.extKM", [0, 0])
                    spdlmt = ["", 500, 500, 500, 500, 500, 500, 500]
                    spdlmt[tuner.AxisId] = dctCfg["SpeedLimit"]
                    self.Conn.segR("drvSPD", spdlmt)

                    self.Conn.putR("m@.simTRQ", 0)
                    self.Conn.putR("m@.simKP" , 250)
                    self.Conn.putR("m@.simKV" , 10000)
                    self.Conn.putR("m@.simKG" , 1000)
                    self.Conn.putR("m@.simKM" , 200)
                    self.Conn.putR("m@.simKA" , 50)
                    self.Conn.putR("m@.simKS" , 50)
                    self.Conn.putR("m@.simKS0", 200)
                    log.debug("Test Parameters: AxisId=%d, Angle=%d\r\n", tuner.AxisId, tuner.Angle)

                    spdP = np.zeros(10, dtype = int)
                    spdN = np.zeros(10, dtype = int)
                    velP = np.zeros(10, dtype = int)
                    velN = np.zeros(10, dtype = int)
                    outP = np.zeros(10, dtype = int)
                    outN = np.zeros(10, dtype = int)

                    nTest = dctCfg["TestSpeedSections"]
                    incSpd = round((dctCfg["MaxTestSpeed"] - dctCfg["MinTestSpeed"])/(nTest-1))
                    spdtab = list()
                    for i in range(dctCfg["MinTestSpeed"], dctCfg["MaxTestSpeed"], incSpd):
                        spdtab.append(round(i))
                    spdtab.append(dctCfg["MaxTestSpeed"])
                    log.debug("nTest=%d, spd=%s\r\n", nTest, str(spdtab))

                    # Start DAS
                    self.Conn.put("dasCH=6,m@.map.cmdANG,m@.map.cmdSPD,m@.map.cmdAMP,m@.map.cmdOUT,m@.map.cmdACC,m@.map.cmdVEL")

                    self.Conn.pMoveTo("#p2")
                    time.sleep(0.5)
                    for i in range(nTest):
                        dctCfg["SamplingTime"]=int(1300/spdtab[i])
                        log.debug("Joint=%d, spd=%d, dT=%d\r\n", tuner.AxisId, spdtab[i], dctCfg["SamplingTime"])
                        self.Conn.dasStart(dctCfg["SamplingTime"])
                        self.Conn.pMoveTo("#p3", spdtab[i])
                        time.sleep(0.2)
                        self.Conn.pMoveTo("#p2", spdtab[i])
                        time.sleep(0.2)
                        tuner.DataLength = self.Conn.dasStop()
                        log.debug("DataLength=%d\r\n", tuner.DataLength)

                        # Get test result
                        tuner.lstData.clear()
                        tuner.lstData.append(self.Conn.dasGet(1, tuner.DataLength))
                        tuner.lstData.append(self.Conn.dasGet(2, tuner.DataLength))
                        tuner.lstData.append(self.Conn.dasGet(3, tuner.DataLength))
                        tuner.lstData.append(self.Conn.dasGet(4, tuner.DataLength))
                        tuner.lstData.append(self.Conn.dasGet(5, tuner.DataLength))
                        tuner.lstData.append(self.Conn.dasGet(6, tuner.DataLength))
                        tuner.AxisX = np.linspace(0, tuner.DataLength*dctCfg["SamplingTime"], tuner.DataLength, endpoint = True)
                        tuner.AxisX = tuner.AxisX[0 : len(tuner.lstData[0])]

                        num=0; vel=0; spd=0; out=0; thd=int(max(tuner.lstData[5])*9/10)
                        for j in range(tuner.DataLength):
                            if tuner.lstData[5][j] > thd:
                                num+=1; vel+=tuner.lstData[5][j]; spd+=tuner.lstData[1][j]; out+=tuner.lstData[3][j]
                        if num>0:
                            vel=int(vel/num); spd=int(spd/num); out=int(out/num)
                        spdP[i]=spd; velP[i]=vel; outP[i]=out
                        log.debug("num=%d, spd=%d, vel=%d, out=%d\r\n", num, spd, vel, out)
                        num=0; vel=0; spd=0; out=0;
                        for j in range(tuner.DataLength):
                            if tuner.lstData[5][j]<-thd:
                                num+=1; vel+=tuner.lstData[5][j]; spd+=tuner.lstData[1][j]; out+=tuner.lstData[3][j]
                        if num>0:
                            vel=int(vel/num); spd=int(spd/num); out=int(out/num)
                        spdN[i]=spd; velN[i]=vel; outN[i]=out
                        log.debug("n=%d, spd=%d, vel=%d, out=%d\r\n", num, spd, vel, out)
                        outM=int((outP[i]+outN[i])/2)
                        outP[i]-=outM
                        outN[i]-=outM
                        log.debug("mean=%d, outP=%d, outN=%d\r\n", outM, outP[i], outN[i])

                        #Show result plot
                        tuner.lstCurveLabels = ["cmdANG({})".format(dctMotionParam["cmdANG"]["Unit"]), \
                                                "cmdSPD({})".format(dctMotionParam["cmdSPD"]["Unit"]), \
                                                "cmdAMP({})".format(dctMotionParam["cmdAMP"]["Unit"]), \
                                                "cmdOUT({})".format(dctMotionParam["cmdOUT"]["Unit"]), \
                                                "cmdACC({})".format(dctMotionParam["cmdACC"]["Unit"]), \
                                                "cmdVEL({})".format(dctMotionParam["cmdVEL"]["Unit"])]
                        tuner.lstCurveColors = ["red", "green", "blue", "black", "red", "green"]
                        self.sigMotionTunerEventHandler.emit({"ShowPlot":[""]})
                    # End of loop
                    self.Conn.pMoveTo("#p1"); time.sleep(0.5)

                    if nTest>=(dctCfg["TestSpeedSections"]-1):
                        c=np.polyfit(velP,outP,1)
                        kv =int(c[0]*1000)
                        kv0=int(c[1])
                        log.debug("kv=%d, kv0=%d\r\n",kv,kv0)
                        log.debug("vel=%d\r\n",velP)
                        log.debug("out=%d\r\n",outP)
                        err=np.polyval(c,velP)-outP
                        for i in range(nTest): err[i]=int(err[i])
                        log.debug("err=%d\r\n",err)

                        c=np.polyfit(velN,outN,1)
                        kv =int(c[0]*1000)
                        kv0=int(c[1])
                        log.debug("kv=%d, kv0=%d\r\n",kv,kv0)
                        log.debug("vel=%d\r\n",velN)
                        log.debug("out=%d\r\n",outN)
                        err=np.polyval(c,velN)-outN
                        for i in range(nTest): err[i]=int(err[i])
                        log.debug("err=%d\r\n",err)

                        c=np.polyfit(spdP,outP,1)
                        ks =int(c[0]*1000)
                        ks0=int(c[1])
                        log.debug("ks=%d, ks0=%d\r\n",ks,ks0)
                        log.debug("spd=%d\r\n",spdP)
                        log.debug("out=%d\r\n",outP)
                        err=np.polyval(c,spdP)-outP
                        for i in range(nTest): err[i]=int(err[i])
                        log.debug("err=%d\r\n",err)

                        c=np.polyfit(spdN,outN,1)
                        ks =int(c[0]*1000)
                        ks0=int(c[1])
                        log.debug("ks=%s,ks0=%s\r\n", str(ks), str(ks0))
                        log.debug("spd=%s\r\n", str(spdN))
                        log.debug("out=%s\r\n", str(outN))
                        err=np.polyval(c,spdN)-outN
                        for i in range(nTest): err[i]=int(err[i])
                        log.debug("err=%d\r\n",err)

                    tuner.lstMeasuredDynamicFriction[tuner.AxisId-1] = abs(kv)
                    tuner.lstMeasuredStaticFriction[tuner.AxisId-1] = abs(kv0)
                    tuner.lstMeasuredDraggedDynamicFriction[tuner.AxisId-1] = abs(ks)
                    tuner.lstMeasuredDraggedStaticFriction[tuner.AxisId-1] = abs(ks0)
                    log.debug("Test Result: kv=%d, kv0=%d, ks=%d, ks0=%d\r\n", \
                        tuner.lstMeasuredDynamicFriction[tuner.AxisId-1], \
                        tuner.lstMeasuredStaticFriction[tuner.AxisId-1], \
                        tuner.lstMeasuredDraggedDynamicFriction[tuner.AxisId-1], \
                        tuner.lstMeasuredDraggedStaticFriction[tuner.AxisId-1])
                    self.sigMotionTunerEventHandler.emit({"UpdateFrictionTest":[""]})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass

            elif k == "ExtForceCompensate":
                log.debug("ExtForceCompensate: %s\r\n", str(v))
                dctCfg = self.MotionTuner.dctConfig["extForce"]
                try:
                    # # Show progress box
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", "Turning Servo OFF, Please Wait!"]})
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 20]})
                    ecatExtKG =[""]
                    ecatExtKG.extend(dctCfg["GravityFactor"])
                    ecatExtKM =[""]
                    ecatExtKM.extend(dctCfg["ConcentricInertiaFactor"])
                    ecatExtKA =[""]
                    ecatExtKA.extend(dctCfg["EccentricInertiaFactor"])
                    ecatExtKV =[""]
                    ecatExtKV.extend(dctCfg["DynamicFrictionFactor"])
                    ecatExtKV0 =[""]
                    ecatExtKV0.extend(dctCfg["StaticFrictionFactor"])
                    ecatExtKS =[""]
                    ecatExtKS.extend(dctCfg["DraggedStaticFrictionFactor"])
                    ecatExtKS0 =[""]
                    ecatExtKS0.extend(dctCfg["DraggedDynamicFrictionFactor"])

                    ecatExtSPD=["", 200, 200, 200, 200, 200, 200, 200]
                    ecatExtSP0=["",  10,  10,  10,  10,  10,  10,  10]
                    ecatExtBRK=["", 200, 200, 200, 200, 200, 200, 200]
                    ecatExtMXC=["", 0, 0, 0, 0, 0, 0, 0]
                    ecatExtHLD=["",  20,  20,  20,  20,  20,  20,  20]
                    
                    self.Conn.segR("extKG", ecatExtKG)
                    self.Conn.segR("extKM", ecatExtKM)
                    self.Conn.segR("extKA", ecatExtKA)
                    self.Conn.segR("extKV", ecatExtKV)
                    self.Conn.segR("extKV0", ecatExtKV0)
                    self.Conn.segR("extKS", ecatExtKS)
                    self.Conn.segR("extKS0", ecatExtKS0)

                    self.Conn.segR("extSPD", ecatExtSPD)
                    self.Conn.segR("extSPD0", ecatExtSP0)
                    self.Conn.segR("extBRK", ecatExtBRK)
                    self.Conn.segR("extMXC", ecatExtMXC)
                    self.Conn.segR("extHLD", ecatExtHLD)

                    # Setup points for test
                    self.Conn.pSet('#p1',['joint',   0,   0,   0,   0,   0,   0,   0])
                    pt2 = ['joint', 0, 0, 0, 0, 0, 0, 0]
                    pt2[tuner.AxisId] = tuner.Angle
                    self.Conn.pSet('#p2', pt2)
                    pt3 = ['joint', 0, 0, 0, 0, 0, 0, 0]
                    pt3[tuner.AxisId] = -tuner.Angle
                    self.Conn.pSet('#p3', pt3)

                    # Setup test condition
                    log.debug("Test Condition: Speed=%d, SampleTime=%d\r\n", dctCfg["Speed"], dctCfg["SamplingTime"])

                    self.Conn.segR("drvSPD",["", 500, 500, 500, 500, 500, 500, 500])
                    self.Conn.putR("m0.map.cmdMXC", dctCfg["extForceSwitch"])
                    self.Conn.putR("m0.map.extENB", 1)
                    self.Conn.putR("m0.map.almENB", dctCfg["EnbAlarmMode"])

                    self.Conn.setAxis(tuner.AxisId)
                    self.Conn.putR("m@.map.drvOLD", 0)# Enable Ext.Force
                    self.Conn.putR("m@.map.extKV", \
                        [dctCfg["DynamicFrictionFactor"][tuner.AxisId-1], dctCfg["StaticFrictionFactor"][tuner.AxisId-1]])
                    self.Conn.putR("m@.map.extKS", \
                        [dctCfg["DraggedDynamicFrictionFactor"][tuner.AxisId-1], dctCfg["DraggedStaticFrictionFactor"][tuner.AxisId-1]])
                    # self.Conn.putR("m@.map.extSPD", [dctCfg["SpeedLimit"], dctCfg["DecelerationLimit"]])
                    self.Conn.putR("m@.map.extKG", dctCfg["GravityFactor"][tuner.AxisId-1])
                    self.Conn.putR("m@.map.extKM", \
                        [dctCfg["ConcentricInertiaFactor"][tuner.AxisId-1], dctCfg["EccentricInertiaFactor"][tuner.AxisId-1]])

                    self.Conn.putR("m@.simTRQ", 0)      #**simTRQ=外力干擾(單位=0.1%)
                    self.Conn.putR("m@.simKP" , 250)    #**simKP =位置環路的增益
                    self.Conn.putR("m@.simKV" , 10000)  #**simKV =速度環路的增益
                    self.Conn.putR("m@.simKG" , 1000)   #**simKG =重力計算的增益
                    self.Conn.putR("m@.simKM", 200)     #**simKM=同軸慣量(單位=0.1%)
                    self.Conn.putR("m@.simKA" , 50)     #**simKA =偏心慣量的增益
                    self.Conn.putR("m@.simKS" , 50)     #**simKS =動摩擦值的增益
                    self.Conn.putR("m@.simKS0", 200)    #**simKS0=靜摩擦值(單位=0.1%)

                    # Start test and measurement
                    self.Conn.put("dasCH=9, \
                        m@.map.cmdANG, \
                        m@.map.cmdSPD, \
                        m@.map.cmdAMP, \
                        m@.map.cmdOUT, \
                        m@.map.cmdMXD, \
                        m@.map.cmdTRQ, \
                        m@.map.cmdACC, \
                        m@.map.cmdVEL, \
                        m@.map.cmdERR")

                    self.Conn.pMoveTo("#p2")
                    time.sleep(0.5)
                    self.Conn.dasStart(dctCfg["SamplingTime"])
                    self.Conn.pMoveTo("#p3", dctCfg["Speed"])
                    time.sleep(0.8)

                    if dctCfg["CollisionTestTorque"][tuner.AxisId-1] != 0:
                        self.Conn.putR("m@.map.drvTRQ", dctCfg["CollisionTestTorque"][tuner.AxisId-1])
                        time.sleep(1.0)
                        self.Conn.putR("m@.map.drvTRQ", 0)

                    self.Conn.pMoveTo("#p2", dctCfg["Speed"])
                    time.sleep(2.0)
                    tuner.DataLength = self.Conn.dasStop()
                    log.debug("DataLength=%d\r\n", tuner.DataLength)
                    self.Conn.pMoveTo("#p1")
                    time.sleep(0.5)

                    # Get data result
                    tuner.lstData.clear()
                    tuner.lstData.append(self.Conn.dasGet(1, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(2, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(3, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(4, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(5, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(6, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(7, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(8, tuner.DataLength))
                    tuner.lstData.append(self.Conn.dasGet(9, tuner.DataLength))

                    # Get Axis-X data
                    tuner.AxisX = np.linspace(0, tuner.DataLength*dctCfg["SamplingTime"], tuner.DataLength, endpoint = True)
                    tuner.AxisX = tuner.AxisX[0 : len(tuner.lstData[0])]

                    self.Conn.putR("m0.map.almENB", 0)
                    self.Conn.putR("m@.map.drvOLD", 1)# Disable Ext.Force
                    # self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 50]})

                    # Show result plot
                    tuner.lstCurveLabels = ["cmdANG({})".format(dctMotionParam["cmdANG"]["Unit"]), \
                                        "cmdSPD({})".format(dctMotionParam["cmdSPD"]["Unit"]), \
                                        "cmdAMP({})".format(dctMotionParam["cmdAMP"]["Unit"]), \
                                        "cmdOUT({})".format(dctMotionParam["cmdOUT"]["Unit"]), \
                                        "cmdMXD({})".format(dctMotionParam["cmdMXD"]["Unit"]), \
                                        "cmdTRQ({})".format(dctMotionParam["cmdTRQ"]["Unit"]), \
                                        "cmdACC({})".format(dctMotionParam["cmdACC"]["Unit"]), \
                                        "cmdVEL({})".format(dctMotionParam["cmdVEL"]["Unit"]), \
                                        "cmdERR({})".format(dctMotionParam["cmdERR"]["Unit"])]
                    tuner.lstCurveColors = ["red", "green", "blue", "black", "red", "green", "blue", "black", "red"]
                    self.sigMotionTunerEventHandler.emit({"ShowPlot":[""]})

                    # # Notify establish connection has success
                    # self.sigMainWinEventHandler.emit({"StatusChange":""})
                    # self.sigStartUpEventHandler.emit({"StatusChange":""})
                except Exception as e:
                    self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                    break
                finally:
                    pass
        # End of command loop
        self.SuspendRealTimeUpdate = 0

############ For Upgrade
    sigUpgradeEventHandler = pyqtSignal(dict)
    def BindUpgrade(self, pUpgrade):
        self.Upgrade = pUpgrade
        self.sigUpgradeEventHandler.connect(pUpgrade.sltEventHandler)

    @pyqtSlot(dict)
    def sltUpgradeProcess(self, dctCmd):
        Result = -1
        self.SuspendRealTimeUpdate = 1
        for k, v in dctCmd.items():
            if k == "DownloadFirmware":
                log.debug("sltUpgradeProcess.DownloadFirmware: %s\r\n", v[0])
                # Change status first
                self.MotionData.SystemState = dctSYSTEM_STATE["UPGRADING"]
                time.sleep(0.1)

                # Download Single Servo firmware
                if v[0] > 2:
                    try:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", \
                            "Downloading Servo {} Firmware, Please Wait!".format(v[0]-2)]})

                        log.debug("Download Single Servo firmware: %s, %s\r\n", \
                            dctAPP_CFIG["SERVO_FW_PATH"], "m"+str(v[0]-2))
                        # exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"escTest0.py","rb").read(), globals())
                        exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"foeTest0.py","rb").read(), globals())
                        self.Conn.foeWrite(dctAPP_CFIG["SERVO_FW_PATH"], "m"+str(v[0]-2), self.SetUpgradingProgress)
                        # Wait Servo restart up completed
                        time.sleep(0.5)
                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass

                # Download All Servo firmware
                elif v[0] > 0:
                    try:
                        for i in range(self.StartUp.OnlineServoCount-1,-1,-1):
                            self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", \
                                "Downloading Servo {} Firmware, Please Wait!".format(i+1)]})

                            log.debug("Download Servo_%d firmware: %s, %s\r\n", \
                                i+1, dctAPP_CFIG["SERVO_FW_PATH"], "m"+str(i+1))
                            # exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"escTest0.py","rb").read(), globals())
                            exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"foeTest0.py","rb").read(), globals())
                            self.Conn.foeWrite(dctAPP_CFIG["SERVO_FW_PATH"], "m"+str(i+1), self.SetUpgradingProgress)
                            # Wait Servo restart up completed
                            time.sleep(0.5)
                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass
                    if (v[0] == 2) and (i == 0):
                        Result = 0

                # Download EtherCAT Master firmware
                if v[0] <= 1:
                    try:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", \
                            "Downloading Master Firmware, Please Wait!"]})

                        log.debug("Download EtherCAT Master firmware: %s, m0\r\n", v[0])
                        exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"foeTest0.py","rb").read(), globals())
                        self.Conn.foeWrite(dctAPP_CFIG["ECAT_MASTER_FW_PATH"], "m0", self.SetUpgradingProgress)
                        # Wait serial port restart ready
                        Result = 0
                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass
            elif k == "DownloadParameter":
                log.debug("sltUpgradeProcess.DownloadParameter: %s\r\n", v[0])
                # Change status first
                self.MotionData.SystemState = dctSYSTEM_STATE["UPGRADING"]
                time.sleep(0.1)

                # Download Single Servo Parameter
                if v[0] > 0:
                    self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", \
                        "Downloading Servo {} Parameter, Please Wait!".format(v[0])]})
                    try:
                        log.debug("Download Single Servo Parameter: %s, %s\r\n", \
                            dctAPP_CFIG["SERVO_PARAM_PATH"][v[0]-1], "m"+str(v[0]))
                        # exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"escTest0.py","rb").read(), globals())
                        exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"foeTest0.py","rb").read(), globals())
                        self.Conn.foeWrite(dctAPP_CFIG["SERVO_PARAM_PATH"][v[0]-1], "m"+str(v[0]), self.SetUpgradingProgress)
                        # Wait Servo restart up completed
                        time.sleep(0.5)
                        Result = 0
                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass
                # Download All Servo Parameter
                else:
                    try:
                        for i in range(self.StartUp.OnlineServoCount-1, -1, -1):
                            self.sigMainWinEventHandler.emit({"SetProgressBox":["Open", \
                                "Downloading Servo {} Parameter, Please Wait!".format(i+1)]})
                            log.debug("Download Servo_%d Parameter: %s, %s\r\n", \
                                i+1, dctAPP_CFIG["SERVO_PARAM_PATH"][i], "m"+str(i+1))
                            # exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"escTest0.py","rb").read(), globals())
                            exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"foeTest0.py","rb").read(), globals())
                            self.Conn.foeWrite(dctAPP_CFIG["SERVO_PARAM_PATH"][i], "m"+str(i+1), self.SetUpgradingProgress)
                            # Wait Servo restart up completed
                            time.sleep(0.5)

                    except Exception as e:
                        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", 100]})
                        self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
                        break
                    finally:
                        pass
                    if i == 0:
                        Result = 0
        # End of command loop
        # Close progress box
        self.sigMainWinEventHandler.emit({"SetProgressBox":["Close"]})
        if Result == 0:
            # Reconnect and enter OP mode
            self.StartUp.sigEventHandler.emit({"Disconnect":[""]})
            self.StartUp.sigEventHandler.emit({"Reconnect":[""]})
        self.SuspendRealTimeUpdate = 0

    def SetUpgradingProgress(self, val):
        self.sigMainWinEventHandler.emit({"SetProgressBox":["SetValue", val]})
############ For Information
    sigInformationEventHandler = pyqtSignal(dict)
    def BindInformation(self, pInformation):
        self.Information = pInformation
        self.sigInformationEventHandler.connect(pInformation.sltEventHandler)

    @pyqtSlot(dict)
    def sltInformationProcess(self, dctCmd):
        pass

############ For Jog Control
    sigJogControlEventHandler = pyqtSignal(dict)
    def BindJogControl(self, pJogControl):
        self.JogControl = pJogControl
        self.sigJogControlEventHandler.connect(pJogControl.sltEventHandler)

    #
    # General command format: {"Cmd":"Joint"/"TCP", "JogOffset":[], "Speed": int, "Acc": int}
    #
    @pyqtSlot(dict)
    def sltJogProcess(self, dctCmd):
        # Check empty jog command
        if len(dctCmd) == 0 or dctCmd["JogOffset"] == None:
            return

        tempState = self.MotionData.SystemState
        self.MotionData.SystemState = dctSYSTEM_STATE["RUN_JOG"]
        self.sigMainWinEventHandler.emit({"StatusChange":""})

        try:
            track = copy.deepcopy(self.Conn._track)
            if dctCmd["Cmd"] == "Joint":
                for j in range(len(track[1:])):
                    track[j+1] += dctCmd["JogOffset"][j]
                if "Speed" not in dctCmd:
                    self.Conn.pMoveTo(track)
                elif "Acc" not in dctCmd:
                    self.Conn.pMoveTo(track, dctCmd["Speed"])
                else:
                    self.Conn.pMoveTo(track, dctCmd["Speed"], dctCmd["Acc"])

            elif dctCmd["Cmd"] == "TCP":
                # Convert joint to XYZ coordination
                PointXYZ = self.Conn.pTo(track, "work")

                for j in range(len(PointXYZ[1:])):
                    PointXYZ[j+1] += dctCmd["JogOffset"][j]
                log.debug("sltJogProcess: PointXYZ=%s\r\n", str(PointXYZ))

                if "Speed" not in dctCmd:
                    self.Conn.pMoveLn(PointXYZ)
                elif "Acc" not in dctCmd:
                    self.Conn.pMoveLn(PointXYZ, dctCmd["Speed"])
                else:
                    self.Conn.pMoveLn(PointXYZ, dctCmd["Speed"], dctCmd["Acc"])
        except Exception as e:
            self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
        finally:
            pass

        self.MotionData.SystemState = tempState
        self.sigMainWinEventHandler.emit({"StatusChange":""})

        log.debug("sltJogProcess: dctCmd=%s\r\n", str(dctCmd))

############ For Script Editor
    sigScriptEditorEventHandler = pyqtSignal(dict)
    def BindScriptEditor(self, pScriptEditor):
        self.ScriptEditor = pScriptEditor
        self.sigScriptEditorEventHandler.connect(pScriptEditor.sltEventHandler)

    @pyqtSlot(list)
    def sltScriptProcess(self, lstCmd):
        from frmScriptEditor import RunScriptStateDef
        # Check empty script
        if len(lstCmd) == 0:
            self.sigScriptEditorEventHandler.emit({"Ready":""})
            self.sigMainWinEventHandler.emit({"SetMsgBox":["Warning", "Cannot run empty script"]})
            return        
        tempState = self.MotionData.SystemState
        self.MotionData.SystemState = dctSYSTEM_STATE["RUN_SCRIPT"]
        self.sigMainWinEventHandler.emit({"StatusChange":""})
        
        try:
            # Run script
            ln = 0
            while True:
                if ln >= len(lstCmd):
                    break
                idcNum = ln

                # Detect stop event
                if self.ScriptEditor.RunScriptState == RunScriptStateDef["Stop"]:
                    ln = len(lstCmd)
                    log.debug("Terminated by stop event\r\n")
                    break

                # Detect pause event
                while self.ScriptEditor.RunScriptState == RunScriptStateDef["Pause"]:
                    self.sigScriptEditorEventHandler.emit({"SetRowColor":[idcNum, Qt.yellow]})
                    time.sleep(0.5)
                    self.sigScriptEditorEventHandler.emit({"SetRowColor":[idcNum, Qt.white]})
                    time.sleep(0.5)

                # Highlight current row
                self.sigScriptEditorEventHandler.emit({"SetRowColor":[idcNum, Qt.green]})

                # Parsing each fields
                fields = lstCmd[ln]
                log.debug("Run line[%d]: cmd=%s, param=%s\r\n", ln+1, fields[0], str(fields[1:]))
                ln += 1
                if fields[0] == "MOVJNT":
                    # Find speed and acceleration settings
                    spd=self.ScriptEditor.DefaultSpeed
                    acc=0
                    for pn in fields[1:]:
                        sfs = pn.split("=")
                        if len(sfs) > 1:
                            if sfs[0] == "SPD":
                                spd = float(sfs[1])
                            elif sfs[0] == "ACC":
                                acc = float(sfs[1])

                    # Get current joint angles
                    joint_motion = self.Conn._track

                    # Added specified offset and execute joint motion
                    for f in fields[1:]:
                        j = f.split("=")
                        if j[0] == "SPD" or j[0] == "ACC":
                            continue
                        j[0] = int(j[0][1:])
                        j[1] = int(j[1])
                        joint_motion[j[0]] = j[1]
                    log.debug("%s: joint_motion=%s, spd=%d, acc=%d\r\n", fields[0], joint_motion, spd, acc)
                    if acc == 0:
                        self.Conn.pMoveTo(joint_motion, spd)
                    else:
                        self.Conn.pMoveTo(joint_motion, spd, acc)

                elif fields[0] == "MOVPT":
                    # Find speed and acceleration settings
                    spd=self.ScriptEditor.DefaultSpeed
                    acc=0
                    pns = fields[1]
                    for pn in fields[2:]:
                        sfs = pn.split("=")
                        if len(sfs) > 1:
                            if sfs[0] == "SPD":
                                spd = float(sfs[1])
                            elif sfs[0] == "ACC":
                                acc = float(sfs[1])
                            continue
                        pns += ","+pn
                    log.debug("%s: pns=%s, spd=%d, acc=%d\r\n", fields[0], pns, spd, acc)
                    if acc == 0:
                        self.Conn.pMoveTo(pns, spd)
                    else:
                        self.Conn.pMoveTo(pns, spd, acc)

                elif fields[0] == "MOVLN":
                    # Find speed and acceleration settings
                    spd=self.ScriptEditor.DefaultSpeed
                    acc=0
                    pv = [""]
                    for pn in fields[1:]:
                        sfs = pn.split("=")
                        if len(sfs) > 1:
                            if sfs[0] == "SPD":
                                spd = float(sfs[1])
                            elif sfs[0] == "ACC":
                                acc = float(sfs[1])
                        else:
                            pv = self.Conn.pGet(pn,"work")
                    log.debug("%s: pv=%s, spd=%d, acc=%d\r\n", fields[0], pv, spd, acc)
                    if acc == 0:
                        self.Conn.pMoveLn(pv, spd)
                    else:
                        self.Conn.pMoveLn(pv, spd, acc)

                elif fields[0] == "DELAY":
                    time.sleep(fields[1]*0.001)

                elif fields[0] == "LOOP":
                    # Reset loop count at LOOPEND line
                    lstCmd[fields[2]][1] = fields[1]

                elif fields[0] == "LOOPEND":
                    # Check loop count
                    if fields[1] > 1:
                        fields[1] -= 1
                        # Jump to loop command next line
                        ln = fields[2]+1

                elif fields[0][0] == "#":
                    pass

                else:
                    pass

                self.sigScriptEditorEventHandler.emit({"SetRowColor":[idcNum, Qt.white]})
            # End of script loop
            self.MotionData.SystemState = tempState
            self.sigMainWinEventHandler.emit({"StatusChange":""})
            self.sigScriptEditorEventHandler.emit({"Ready":""})
      
        except Exception as e:
            self.sigMainWinEventHandler.emit({"SetMsgBox":["Exception", self.GetMsgWithLineNumber(e)]})
        finally:
            pass
#End of Class MotionCtrl
