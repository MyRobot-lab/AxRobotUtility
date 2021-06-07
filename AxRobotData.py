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
import sys, logging, os
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.setLevel(logging.CRITICAL)

# Global variable
MaxAxisNum = 7
SimulationModeEnabled = False
Joint3AngLimit = 0

# Default Application Configuration
dctAPP_CFIG = {
    # Application Information
    "APP_NAME":"AxRobotUtility",
    "APP_VER":"1.0.0",

    # COM port configuration
    "USB_CDC_IDENTIFY":"VID:PID=0B95:5820",

    # Resource file path
    "IMG_PATH":"./img/",
    "MODEL_PATH":"./model/",
    "PARAM_PATH":"./param/",
    "SCRIPT_PATH":"./script/",
    "SIMU3D_PATH":"./simu/",
    "ECAT_MASTER_FW_PATH":"../../../Firmware/Binary/EtherCAT_Master_Firmware/AX58200_EtherCATMaster_Firmware_v100.bin",
    "SERVO_FW_PATH":"../../../Firmware/Binary/EtherCAT_Slave_ServoDrive_Firmware/AX58200_ServoDrive_Firmware_v100.bin",
    "SERVO_PARAM_PATH": [ \
        "./param/AxisParam1.txt", \
        "./param/AxisParam2.txt", \
        "./param/AxisParam3.txt", \
        "./param/AxisParam4.txt", \
        "./param/AxisParam5.txt", \
        "./param/AxisParam6.txt", \
        "./param/AxisParam7.txt" \
    ],
    "MOTION_CONFIG_PATH":"./param/motion_cfg.mcf",

    # External python file path
    "Ext_PY_PATH":"./program/",

    #Document path
    "USER_GUIDE_PATH":"..\\..\\..\\Document\\AxRobot_UserGuide_v100.pdf"
    }

# Flags Definition
flgREAD          = 0x0000
flgWRITE         = 0x0001
flgSATUS         = 0x0000
flgCTRL          = 0x0001
flgCFIG          = 0x0002
flgSHOW_AS_INT   = 0x0000
flgSHOW_AS_FLT   = 0x0010
flgSHOW_AS_HEX   = 0x0020
flgCFIG_RESET    = 0x0100

# System State Definition
dctSYSTEM_STATE = {
    "DISCONNECTED"  :0,
    "CONNECTED"     :1,
    "UPGRADING"     :2,
    "SERVO_OFF"     :3,
    "SERVO_ON"      :4,
    "RUN_JOG"       :5,
    "RUN_SCRIPT"    :6,
    "RUN_TUNER"     :7,
    "SAFE_STATE"    :8,
    "SAFE_RECOVERY" :9,
}

class MotionData(QObject):
    # Motion controller Parameter defination
    dctMotionParam = {
        "blkSeg": {"Index":    0, "Flag":0x1000, "ItemCnt":9, "Name" :"Motion Segment Parameter Block"},
        "segDEC": {"Index":    1, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segK"  : {"Index":    2, "Value":0, "Max":0, "Min":0, "Unit":"times", "Flag":0, "Note":""},
        "segMS" : {"Index":    3, "Value":0, "Max":0, "Min":0, "Unit":"ms", "Flag":0, "Note":""},
        "segSTS": {"Index":    4, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segMOD": {"Index":    5, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "segCMD": {"Index":    6, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segI"  : {"Index":    7, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segN"  : {"Index":    8, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "netSTS": {"Index":    9, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkCmd": {"Index":   10, "ItemCnt":9, "Name" :"Command Parameter Block"},
        "cmdPOS": {"Index":   10, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":flgCTRL, "Note":"Position command to joint 1~7"},
        "cmdVEL": {"Index":   11, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1deg/s", "Flag":flgCTRL, "Note":"Speed command from joint 1~7"},
        "cmdACC": {"Index":   12, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1deg/s^2", "Flag":flgCTRL, "Note":"Extended acceleration to joint 1~7"},
        "cmdTRQ": {"Index":   13, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Note":"Extended torque compensation to joint 1~7"},
        "cmdMXD": {"Index":   14, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Note":"Maximum close loop output current at joint 1~7"},
        "cmdANG": {"Index":   15, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":0, "Note":"Angle feedback from joint 1~7"},
        "cmdSPD": {"Index":   16, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1deg/s", "Flag":0, "Note":"Speed feedback from joint 1~7"},
        "cmdAMP": {"Index":   17, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Note":"Total output current on joint 1~7"},
        "cmdOUT": {"Index":   18, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Note":"Close loop output current on joint 1~7"},

        "cmdMXC": {"Index":   90, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Note":"Common maximum close loop output current"},
        "cmdMXM": {"Index":   91, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"gain*kg*m^2", "Flag":0, "Note":"Current inertia value at joint 1~7"},
        "cmdMXG": {"Index":   92, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"gain*N/kg", "Flag":0, "Note":"Current gravity value at joint 1~7"},

        "cmdERR": {"Index":  100, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":0, "Note":"Position error at motion controller side for joint 1~7"},
        "cmdTG" : {"Index":  101, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Note":""},
        "cmdTI" : {"Index":  102, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Note":""},
        "cmdTF" : {"Index":  103, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Note":""},
        "cmdDT" : {"Index":  104, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":0, "Note":""},
        "cmdSIM": {"Index":  105, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "cmdRST": {"Index":  106, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "cmdOLD": {"Index":  107, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "cmdOFF": {"Index":  108, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkSdo": {"Index":  110, "ItemCnt":8, "Name" :"ESC SDO/PDO Parameter Block"},
        "sdoRx0": {"Index":  110, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "sdoRxN": {"Index":  111, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "sdoTx0": {"Index":  112, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "sdoTxN": {"Index":  113, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "pdoRx0": {"Index":  114, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "pdoRxN": {"Index":  115, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "pdoTx0": {"Index":  116, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "pdoTxN": {"Index":  117, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
                
        "blkDrv": {"Index":  120, "ItemCnt":16, "Name" :"Electrical Gear Parameter Block"},
        "drvORG": {"Index":  120, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvINV": {"Index":  121, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvMxH": {"Index":  122, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":flgCFIG, "Note":"Positive angle limitation"},
        "drvMxL": {"Index":  123, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":flgCFIG, "Note":"Negtive angle limitation"},
        "drvKpN": {"Index":  124, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvKpD": {"Index":  125, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvKvN": {"Index":  126, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvKvD": {"Index":  127, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvKsN": {"Index":  128, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvKsD": {"Index":  129, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvPOS": {"Index":  130, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":flgCFIG, "Note":""},
        "drvSPD": {"Index":  131, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1deg/s", "Flag":flgCFIG, "Note":""},
        "drvTRQ": {"Index":  132, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvOLD": {"Index":  133, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvHLD": {"Index":  134, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "drvERR": {"Index":  135, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},

        "blkExt" : {"Index":  140, "ItemCnt":20, "Name" :"Extended Force Parameter Block"},
        "extKG"  : {"Index":  140, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extKM"  : {"Index":  141, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extKA"  : {"Index":  142, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extKV"  : {"Index":  143, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extKV0" : {"Index":  144, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extKS"  : {"Index":  145, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extKS0" : {"Index":  146, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extSPD" : {"Index":  147, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extSPD0": {"Index":  148, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extBRK" : {"Index":  149, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extMXC" : {"Index":  150, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "extHLD" : {"Index":  151, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":flgCFIG, "Note":""},
        "oldVEL" : {"Index":  152, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldOUT" : {"Index":  153, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldV0"  : {"Index":  154, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldP1"  : {"Index":  155, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldP2"  : {"Index":  156, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldP3"  : {"Index":  157, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldM1"  : {"Index":  158, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "oldM2"  : {"Index":  159, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkSegExt": {"Index":  160, "ItemCnt":8, "Name" :"Extended Motion Segment Parameter Block"},
        "segPOS": {"Index":  160, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":0, "Note":""},
        "segSPD": {"Index":  161, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1deg/s", "Flag":0, "Note":""},
        "segACC": {"Index":  162, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1deg/s^2", "Flag":0, "Note":""},
        "segF0" : {"Index":  163, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segP0" : {"Index":  164, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segS0" : {"Index":  165, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segS1" : {"Index":  166, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "segHLD": {"Index":  167, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkEsc": {"Index":  170, "ItemCnt":10, "Name" :"EtherCAT Parameter Block"},
        "escCMD": {"Index":  170, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "escPOS": {"Index":  171, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escVEL": {"Index":  172, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escTRQ": {"Index":  173, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escMXC": {"Index":  174, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escANG": {"Index":  175, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escSPD": {"Index":  176, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escAMP": {"Index":  177, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escOUT": {"Index":  178, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "escSTS": {"Index":  179, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},

        "blkSim" : {"Index":  180, "ItemCnt":11, "Name" :"Simulation Parameter Block"},
        "simTRQ" : {"Index":  180, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simSPD" : {"Index":  181, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "simANG" : {"Index":  182, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "simKP"  : {"Index":  183, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simKV"  : {"Index":  184, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simKG"  : {"Index":  185, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simKM"  : {"Index":  186, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simKA"  : {"Index":  187, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simKS"  : {"Index":  188, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simKS0" : {"Index":  189, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "simANG0": {"Index":  190, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkAlm" : {"Index":  900, "ItemCnt":10, "Name" :"Alarm Parameter Block"},
        "almENB" : {"Index":  900, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "almMSK" : {"Index":  901, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Note":""},
        "almANG1": {"Index":  902, "Value":0, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":flgCFIG, "Note":""},
        "almANG2": {"Index":  903, "Value":0, "Max":0, "Min":0, "Unit":"0.1%deg", "Flag":flgCFIG, "Note":""},
        "almSPD0": {"Index":  904, "Value":0, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":flgCFIG, "Note":""},
        "almMS"  : {"Index":  905, "Value":0, "Max":0, "Min":0, "Unit":"ms", "Flag":flgCFIG, "Note":""},
        "almMOD" : {"Index":  906, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        # "alm907" : {"Index":  907, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "alm908" : {"Index":  908, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
#        "almRUN" : {"Index":  908, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "almBRK" : {"Index":  909, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkSys" : {"Index": 1000, "ItemCnt":10, "Name" :"System Parameter Block"},
        "sysCLK" : {"Index": 1000, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "sys20K" : {"Index": 1001, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "sysLOP" : {"Index": 1002, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "sysKHZ" : {"Index": 1003, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "sysON"  : {"Index": 1004, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "sysOFF" : {"Index": 1005, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "sys1006" : {"Index": 1006, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "sys1007" : {"Index": 1007, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "sys1008" : {"Index": 1008, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "powerON": {"Index": 1009, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkLed" : {"Index": 1010, "ItemCnt":10, "Name" :"LED Parameter Block"},
        "ledR"   : {"Index": 1010, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "ledG"   : {"Index": 1011, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "ledY"   : {"Index": 1012, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "ledB"   : {"Index": 1013, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "ledMS"  : {"Index": 1014, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "ledBITS": {"Index": 1015, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "pKey"   : {"Index": 1016, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "pMask"  : {"Index": 1017, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "pInput" : {"Index": 1018, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "pOutput": {"Index": 1019, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},

        "blkSysExt" : {"Index": 1020, "ItemCnt":10, "Name" :"System Extended Parameter Block"},
        "sysVERS": {"Index": 1020, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":"AX58200 master F/W version"},
        "sysDATE": {"Index": 1021, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":"F/W timestamp"},
        "romVERS": {"Index": 1022, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":"AX58200 master parameter version"},
        "romDATE": {"Index": 1023, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":"Parameter file timestamp"},
        "pdoCMD" : {"Index": 1024, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "pdoNUM" : {"Index": 1025, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
        "sdoSTS" : {"Index": 1026, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "sdoERR" : {"Index": 1027, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "netCMD" : {"Index": 1028, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Note":""},
        "extENB" : {"Index": 1029, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},

        "blkDas" : {"Index": 1100, "ItemCnt":20, "Name" :"DAS Parameter Block"},
        "dasN"   : {"Index": 1100, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "dasCMD" : {"Index": 1101, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasMS"  : {"Index": 1102, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasDT"  : {"Index": 1103, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "dasMAX" : {"Index": 1104, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "dasSIZ" : {"Index": 1105, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "das1106" : {"Index": 1106, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "das1107" : {"Index": 1107, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "das1108" : {"Index": 1108, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "das1109" : {"Index": 1109, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "dasCH"  : {"Index": 1110, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV1"  : {"Index": 1111, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV2"  : {"Index": 1112, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV3"  : {"Index": 1113, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV4"  : {"Index": 1114, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV5"  : {"Index": 1115, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV6"  : {"Index": 1116, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV7"  : {"Index": 1117, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV8"  : {"Index": 1118, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},
        "dasV9"  : {"Index": 1119, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Note":""},

        "blkMSC" : {"Index": 1150, "ItemCnt":20, "Name" :"Misc. Parameter Block"},
        "nAxis"  : {"Index": 1150, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},
#        "maxSPD" : {"Index": 1151, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Note":""},

        "mmNum"  : {"Index": 1160, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "mmSpd"  : {"Index": 1161, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "mmAcc"  : {"Index": 1162, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "mmDec"  : {"Index": 1163, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "spdM"   : {"Index": 1164, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        # "msc1165": {"Index": 1165, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "t0M"    : {"Index": 1166, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "t1M"    : {"Index": 1167, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "t2M"    : {"Index": 1168, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "t9M"    : {"Index": 1169, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},

        "blkDGN" : {"Index": 1400, "ItemCnt":3, "Name" :"Diagnostic Parameter Block"},
        "coeERR" : {"Index": 1400, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "ldpERR" : {"Index": 1401, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
        "foeERR" : {"Index": 1402, "Value":0, "Max":0, "Min":0, "Unit":"", "Flag":0, "Note":""},
    }

    # Real time status defination
    dctRtStatus = {
        "Segment": {"Value":[0]*9, "Unit":"% N/A times ms N/A N/A N/A N/A N/A", \
                                    "Item":"Ratio segDEC segK segMS segSTS segMOD segCMD segI segN", \
                                    "Name": "Motion segment status", \
                                    "Note":"Current motion segment status"},
        "TCP"    : {"Value":[0]*6, "Unit":"mm mm mm deg deg deg", \
                                    "Item":"X Y Z Rx Ry Rz", \
                                    "Name": "Tool Center Posision", \
                                    "Note":"Current tool center position"},
        "Track"  : {"Value":[0]*MaxAxisNum, "Unit":"deg", "Name":" ", "Note":"Position command to joint 1~7"},
        "Joint"  : {"Value":[0]*MaxAxisNum, "Unit":"deg", "Name":" ", "Note":"Angle feedback from joint 1~7"},
        "Diagnostic": {"Value":[0]*6, "Unit":"N/A N/A N/A N/A N/A N/A", \
                                    "Item":"CommColiErr SegLostErr PtCnvColiErr PtCnvErr CommTimeOut FoeTimeOut", \
                                    "Name": "", \
                                    "Note":"Diagnostic count/status"},
        ""  : {"Value":[0], "Unit":"", "Name":" ", "Note":"VCP command collision error count"},
   }
    
    # Real time status items
    lstRtStatusShowItems = [ \
                            # Misc. variables
                            "Segment","Track","TCP","Joint", \

                            # Diagnostic variables
                            "Diagnostic", \
                            
                            # Servo parameters
                            "iopPWR","iopTMP", \

                            # Master paramerers
                            "cmdVEL","cmdACC","cmdTRQ","cmdMXD","cmdSPD","cmdAMP", \
                            "cmdOUT","cmdMXG","cmdMXM","cmdERR"]

    dctServoParam = {
        "blkSdo" : {"Index": 0, "ItemCnt":7, "Name" :"SDO Parameter Block"},
        "sdo1000": {"Index": 10, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Name":"", "Note":""},
        "sdo6502": {"Index": 29, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Name":"", "Note":""},
        "sdo1018": {"Index": 30, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Name":"", "Note":""},
        "vendor" : {"Index": 31, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "product": {"Index": 32, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "version": {"Index": 33, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "series" : {"Index": 34, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},

        "blkDas" : {"Index": 200, "ItemCnt":20, "Name" :"DAS Parameter Block"},
        "dasN"   : {"Index": 200, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"pt", "Flag":0, "Name":"", "Note":""},
        "dasCMD" : {"Index": 201, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasMS"  : {"Index": 202, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasDT"  : {"Index": 203, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":0, "Name":"", "Note":""},
        "dasMAX" : {"Index": 204, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"pts", "Flag":0, "Name":"", "Note":""},
        "dasSIZ" : {"Index": 205, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"pts", "Flag":0, "Name":"", "Note":""},
        # "das206" : {"Index": 206, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "das207" : {"Index": 207, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "das208" : {"Index": 208, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "das209" : {"Index": 209, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "dasCH"  : {"Index": 210, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"chs", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV1"  : {"Index": 211, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV2"  : {"Index": 212, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV3"  : {"Index": 213, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV4"  : {"Index": 214, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV5"  : {"Index": 215, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV6"  : {"Index": 216, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV7"  : {"Index": 217, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV8"  : {"Index": 218, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "dasV9"  : {"Index": 219, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},

        "blkPdo" : {"Index": 220, "ItemCnt":10, "Name" :"PDO Parameter Block"},
        "pdoCMD" : {"Index": 220, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL|flgSHOW_AS_HEX, "Name":"", "Note":""},
        "pdoSTS" : {"Index": 221, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "pdoPOS" : {"Index": 222, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCFIG|flgCFIG_RESET, "Name":"", "Note":""},
        "pdoVEL" : {"Index": 223, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":flgCFIG|flgCFIG_RESET, "Name":"", "Note":""},
        "pdoTRQ" : {"Index": 224, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCFIG|flgCFIG_RESET, "Name":"", "Note":""},
        "pdoMXC" : {"Index": 225, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCFIG, "Name":"", "Note":""},
        "pdoANG" : {"Index": 226, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "pdoSPD" : {"Index": 227, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":0, "Name":"", "Note":""},
        "pdoAMP" : {"Index": 228, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Name":"", "Note":""},
        "pdoOUT" : {"Index": 229, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Name":"", "Note":""},

        "blkCmd" : {"Index": 240, "ItemCnt":10, "Name" :"Command Parameter Block"},
        "cmdCMD" : {"Index": 240, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL|flgCFIG_RESET, "Name":"", "Note":""},
        "cmdPOS" : {"Index": 241, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCTRL, "Name":"", "Note":""},
        "cmdVEL" : {"Index": 242, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":flgCTRL, "Name":"", "Note":""},
        "cmdACC" : {"Index": 243, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s^2", "Flag":flgCTRL, "Name":"", "Note":""},
        "cmdTRQ" : {"Index": 244, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "cmdMXC" : {"Index": 245, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "cmdSIM" : {"Index": 246, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        # "cmd247" : {"Index": 247, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "cmd248" : {"Index": 248, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "cmdON"  : {"Index": 249, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},

        "blkSeg" : {"Index": 260, "ItemCnt":13, "Name" :"Segment Parameter Block"},
        "segCMD" : {"Index": 260, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "segPOS" : {"Index": 261, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCTRL, "Name":"", "Note":""},
        "segVEL" : {"Index": 262, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":flgCTRL, "Name":"", "Note":""},
        "segMAX" : {"Index": 263, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":flgCTRL, "Name":"", "Note":""},
        "segACC" : {"Index": 264, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":flgCTRL, "Name":"", "Note":""},
        "segDEC" : {"Index": 265, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":flgCTRL, "Name":"", "Note":""},
        "segSTS" : {"Index": 266, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "seg267" : {"Index": 267, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "seg268" : {"Index": 268, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "seg269" : {"Index": 269, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "segALM" : {"Index": 270, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "segERR" : {"Index": 271, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "segMXC" : {"Index": 272, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "segMS"  : {"Index": 273, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},

        "blkExt" : {"Index": 280, "ItemCnt":18, "Name" :"Single Axis Extended Force Parameter Block"},
        "extTRQ" : {"Index": 280, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "extOUT" : {"Index": 281, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "extTG"  : {"Index": 282, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extTI"  : {"Index": 283, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extTF"  : {"Index": 284, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extMXC" : {"Index": 285, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "extMXG" : {"Index": 286, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "extMXM" : {"Index": 287, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "extMAX" : {"Index": 288, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "extPPR" : {"Index": 289, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "extKG"  : {"Index": 290, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extKA"  : {"Index": 291, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extKV"  : {"Index": 292, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extKV0" : {"Index": 293, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extKS"  : {"Index": 294, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extKS0" : {"Index": 295, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "extDT"  : {"Index": 296, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "extMS"  : {"Index": 297, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkPos" : {"Index": 300, "ItemCnt":10, "Name" :"Position Control Loop Parameter Block"},
        "posCMD" : {"Index": 300, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCTRL, "Name":"", "Note":""},
        "posERR" : {"Index": 301, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "posSUM" : {"Index": 302, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "posOUT" : {"Index": 303, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":0, "Name":"", "Note":""},
        "posMXE" : {"Index": 304, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "posMXI" : {"Index": 305, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "posMXO" : {"Index": 306, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "posKP"  : {"Index": 307, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "posKI"  : {"Index": 308, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "posDIV" : {"Index": 309, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},

        "blkSpd" : {"Index": 320, "ItemCnt":10, "Name" :"Speed Control Loop Parameter Block"},
        "spdCMD" : {"Index": 320, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":flgCTRL, "Name":"", "Note":""},
        "spdERR" : {"Index": 321, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":0, "Name":"", "Note":""},
        "spdSUM" : {"Index": 322, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "spdOUT" : {"Index": 323, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Name":"", "Note":""},
        "spdMXE" : {"Index": 324, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "spdMXI" : {"Index": 325, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "spdMXO" : {"Index": 326, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "spdKP"  : {"Index": 327, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "spdKI"  : {"Index": 328, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "spdFLT" : {"Index": 329, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},

        "blkAmp" : {"Index": 340, "ItemCnt":10, "Name" :"Current Control Loop Parameter Block"},
        "ampCMD" : {"Index": 340, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "ampSD"  : {"Index": 341, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ampSQ"  : {"Index": 342, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ampLMT" : {"Index": 343, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Name":"", "Note":""},
        "ampMXE" : {"Index": 344, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCFIG, "Name":"", "Note":""},
        "ampMXI" : {"Index": 345, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "ampMXO" : {"Index": 346, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCFIG, "Name":"", "Note":""},
        "ampKP"  : {"Index": 347, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCFIG, "Name":"", "Note":""},
        "ampKI"  : {"Index": 348, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "ampFLT" : {"Index": 349, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},

        "blkEsm" : {"Index": 380, "ItemCnt":18, "Name" :"EtherCAT Parameter Block"},
        "esmEVT" : {"Index": 380, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmREQ" : {"Index": 381, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "esmSTS" : {"Index": 382, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmERR" : {"Index": 383, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmSDO" : {"Index": 384, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmFOE" : {"Index": 385, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmCOE" : {"Index": 386, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmRXP" : {"Index": 387, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmTXP" : {"Index": 388, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "esmDOG" : {"Index": 389, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "rxSDO0" : {"Index": 390, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "rxSDON" : {"Index": 391, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "txSDO0" : {"Index": 392, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "txSDON" : {"Index": 393, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "rxPDO0" : {"Index": 394, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "rxPDON" : {"Index": 395, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "txPDO0" : {"Index": 396, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},
        "txPDON" : {"Index": 397, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgSHOW_AS_HEX, "Name":"", "Note":""},

        "blkIop" : {"Index": 400, "ItemCnt":16, "Name" :"Hardware I/O Parameter Block"},
        "iopANG" : {"Index": 400, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "iopSPD" : {"Index": 401, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks/s", "Flag":0, "Name":"", "Note":""},
        "iopID"  : {"Index": 402, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Name":"", "Note":""},
        "iopIQ"  : {"Index": 403, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":0, "Name":"", "Note":""},
        "iopVD"  : {"Index": 404, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "iopVQ"  : {"Index": 405, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"0.1%", "Flag":flgCTRL, "Name":"", "Note":""},
        "iopPWR" : {"Index": 406, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"V", "Flag":0, "Name":"ServoDrive Power Voltage", "Note":"Current DC power voltage"},
        "iopTMP" : {"Index": 407, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"degC", "Flag":0, "Name":"ServoDrive Temperature", "Note":"Current temperature"},
        "iopI2T" : {"Index": 408, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "iopALM" : {"Index": 409, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "iopREL" : {"Index": 410, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "iopIDX" : {"Index": 411, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "iopABS" : {"Index": 412, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "iopMOD" : {"Index": 413, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "iopPWM" : {"Index": 414, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "iopRST" : {"Index": 415, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkPwm" : {"Index": 420, "ItemCnt":9, "Name" :"SVPWM Parameter Block"},
        "pwmU"   : {"Index": 420, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"tick", "Flag":0, "Name":"", "Note":""},
        "pwmV"   : {"Index": 421, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"tick", "Flag":0, "Name":"", "Note":""},
        "pwmW"   : {"Index": 422, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"tick", "Flag":0, "Name":"", "Note":""},
        "pwmDEG" : {"Index": 423, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"edeg", "Flag":flgCTRL, "Name":"", "Note":""},
        "pwmCMD" : {"Index": 424, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"tick", "Flag":flgCTRL, "Name":"", "Note":""},
        "pwmMS"  : {"Index": 425, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ms", "Flag":flgCTRL, "Name":"", "Note":""},
        "pwmANG" : {"Index": 426, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"edeg", "Flag":flgCTRL, "Name":"", "Note":""},
        "pwmENB" : {"Index": 427, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "pwmBRK" : {"Index": 428, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},

        "pwmMAX" : {"Index": 430, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":0, "Name":"", "Note":""},
        "pwmINV" : {"Index": 431, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "pwmRST" : {"Index": 432, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "pwmFLT" : {"Index": 433, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkUvw" : {"Index": 440, "ItemCnt":7, "Name" :"Vector Control Parameter Block"},
        "uvwDEG" : {"Index": 440, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"edeg", "Flag":0, "Name":"", "Note":""},
        "uvwSIN" : {"Index": 441, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "uvwCOS" : {"Index": 442, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "uvwRDY" : {"Index": 443, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL|flgCFIG|flgCFIG_RESET, "Name":"", "Note":""},
        "uvwKI"  : {"Index": 444, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "uvwKO"  : {"Index": 445, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCTRL, "Name":"", "Note":""},
        "uvwDEG0": {"Index": 446, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
         
        "blkAdc" : {"Index": 460, "ItemCnt":16, "Name" :"ADC Parameter Block"},
        "adcU"   : {"Index": 460, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcV"   : {"Index": 461, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcW"   : {"Index": 462, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcP"   : {"Index": 463, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcT"   : {"Index": 464, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        # "adc465" : {"Index": 465, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        # "adc466" : {"Index": 466, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "adcK0"  : {"Index": 467, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "adcK"   : {"Index": 468, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "adcSTD" : {"Index": 469, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"A", "Flag":flgCFIG, "Name":"", "Note":""},
        "adcIU"  : {"Index": 470, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcIV"  : {"Index": 471, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcIW"  : {"Index": 472, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcSUM" : {"Index": 473, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"dig", "Flag":0, "Name":"", "Note":""},
        "adcDLY" : {"Index": 474, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "adcFLT" : {"Index": 475, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkAng"  : {"Index": 480, "ItemCnt":10, "Name" :"Angle Parameter Block"},
        "angABS0" : {"Index": 480, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCFIG, "Name":"", "Note":""},
        "angIDX0" : {"Index": 481, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCFIG, "Name":"", "Note":""},
        "angREL0" : {"Index": 482, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCFIG, "Name":"", "Note":""},
        "angABS"  : {"Index": 483, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCFIG, "Name":"", "Note":""},
        "angREL"  : {"Index": 484, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"ticks", "Flag":flgCFIG, "Name":"", "Note":""},
        "angPOLE" : {"Index": 485, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"pairs", "Flag":flgCFIG, "Name":"", "Note":""},
        "angGEAR" : {"Index": 486, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "angINV"  : {"Index": 487, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG|flgSHOW_AS_HEX, "Name":"", "Note":""},
        "angKN"   : {"Index": 488, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "angKD"   : {"Index": 489, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},

        "blkAbz" : {"Index": 500, "ItemCnt":5, "Name" :"Incremental Encoder Parameter Block"},
        "abzENB" : {"Index": 500, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "abzFLT" : {"Index": 501, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "abzINV" : {"Index": 502, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "abzOUT" : {"Index": 503, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "abzPRD" : {"Index": 504, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
#        "abzINP" : {"Index": 505, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkHal" : {"Index": 520, "ItemCnt":10, "Name" :"Hall Sensor Parameter Block"},
        "halENB" : {"Index": 520, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "halINP" : {"Index": 521, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halSEQ" : {"Index": 522, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halANG" : {"Index": 523, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halSPD" : {"Index": 524, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halPRD" : {"Index": 525, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halP"   : {"Index": 526, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halN"   : {"Index": 527, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halCAP" : {"Index": 528, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "halRST" : {"Index": 529, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkBis"  : {"Index": 540, "ItemCnt":9, "Name" :"BiSS-C abolute encoder Parameter Block"},
        "bisENB"  : {"Index": 540, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "bisBITS" : {"Index": 541, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "bisMASK" : {"Index": 542, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "bisMULT" : {"Index": 543, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "bisBUF0" : {"Index": 544, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "bisBUF"  : {"Index": 545, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "bisACK"  : {"Index": 546, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "bisCRC"  : {"Index": 547, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "bisERR"  : {"Index": 578, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkDbg"  : {"Index": 990, "ItemCnt":5, "Name" :"Debug Parameter Block"},
        "coeERR"  : {"Index": 990, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "pdiLOK"  : {"Index": 991, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "pdiERR"  : {"Index": 992, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ldpERR"  : {"Index": 993, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "foeERR"  : {"Index": 994, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
       
        "blkSys"  : {"Index": 1000, "ItemCnt":6, "Name" :"System Parameter Block"},
        "sysCLK"  : {"Index": 1000, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "sys20K"  : {"Index": 1001, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "sysLOP"  : {"Index": 1002, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "sysKHZ"  : {"Index": 1003, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "sysON"   : {"Index": 1004, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "sysOFF"  : {"Index": 1005, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkLed"  : {"Index": 1010, "ItemCnt":6, "Name" :"LED Parameter Block"},
        "ledR"    : {"Index": 1010, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ledO"    : {"Index": 1011, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ledY"    : {"Index": 1012, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ledG"    : {"Index": 1013, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ledMS"   : {"Index": 1014, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "ledBITS" : {"Index": 1015, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},

        "blkSysExt"  : {"Index": 1020, "ItemCnt":4, "Name" :"System Extendtion Parameter Block"},
        "sysVERS" : {"Index": 1020, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "sysDATE" : {"Index": 1021, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":0, "Name":"", "Note":""},
        "romVERS" : {"Index": 1022, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
        "romDATE" : {"Index": 1023, "Value":[0]*MaxAxisNum, "Max":0, "Min":0, "Unit":"", "Flag":flgCFIG, "Name":"", "Note":""},
    }

    sigEventHandler = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(MotionData, self).__init__(parent)
        # System
        self.SystemState = dctSYSTEM_STATE["DISCONNECTED"]

        # Motion controller
        self.AxisNumber = 7
        self.extForceEnabled = 0

    def GetLogLevel(self):
        global log
        return log.level

#End of Class MotionData

