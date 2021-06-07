
import time

print("***** offTest0()\r\n");
esc.put("m0.map.almENB=0");            #**關閉doAlarm()  =切斷警報裝置

for i in range(ecatServoN):                     #**依序設置各軸
    esc.setAxis(i+1)                   #**預設軸號
    esc.put("m@.map.cmdOFF=1")         #**關閉doCommand() =切斷運動控制
    esc.put("m@.map.escCMD=0")         #**設置map.escCMD=0=切斷伺服控制
    esc.putSDO("cmdCMD",0)             #**設置sdo.cmdCMD=0=OFF
    esc.putSDO("cmdON", 0)             #**設置sdo.cmdON =0=剎車

#Check CiA402 Contorl word and braker status
for i in range(ecatServoN):
    if i>=7: break
    esc.setAxis(i+1)
    print("Axis",(i+1),"pdoCMD=",hex(esc.getR("m@.sdo.pdoCMD")),"pdoSTS=",hex(esc.getR("m@.sdo.pdoSTS")),"pwmBRK=",esc.getR("m@.sdo.pwmBRK"),"0x6060=",esc.getR("m@.sdo.0x6060"))

