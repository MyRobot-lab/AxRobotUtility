import time
from AxRobotData import *

print("***** escTest0()");
                   #**預設機械手定義和網路裝置
exec(open(dctAPP_CFIG["MODEL_PATH"]+"RobotParam_AxRobot.py","rb").read())
exec(open(dctAPP_CFIG["MODEL_PATH"]+"MotionParam_AxRobot.py","rb").read())
                   #**重設開機參數
s=esc.put ("m0.map.pdoCMD=0");             time.sleep(0.2) #**關閉通訊
s=esc.put ("m0.map.pdoNUM=0")
s=esc.put ("m0.map.netCMD=0");                             #**關閉伺服和模擬
s=esc.put ("m0.map.almENB=0");                             #**關閉警報
s=esc.put ("m0.map.netSTS=0");             time.sleep(0.2)
d=esc.getR("netSTS")
if d==0:           #**啟動ESC連線
    s=esc.put ("m0.esc.0xffff.0.B");           time.sleep(0.1) #**執行Close()
    s=esc.put ("m0.esc.0xffff.1.B");           time.sleep(3.0) #**執行Open()
s=esc.put ("m0.esc.0xffff.9.B"); print(s); time.sleep(0.1) #**讀取ESC並顯示回覆
                   #**顯示驅動器個數
ecatServoN = 0
ecatDeviceN=esc.getR("m0.esc.0xffff.9.B")

ecatServoN = ecatDeviceN
print("ecatDeviceN={}, ecatServoN={}".format(ecatDeviceN, ecatServoN))

if ecatServoN == modelAxis:
    s=esc.put("m0.map.netSTS=1");#**標示網路狀態=1
else:
    print("The found number of servo driver not equal to modelAxis({})\r\n".format(modelAxis));
