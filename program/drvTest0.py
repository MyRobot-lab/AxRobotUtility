import time,copy
from AxRobotData import *

print("***** drvTest0()");
                             #**輸出保護(命令=回授:限制出力為零)
esc.segR("drvSPD",["",0,0,0,0,0,0,0])

for i in range(1,8):         #**模擬軸取消電子齒輪(預設1:1)
    if i<=ecatServoN:
        if ecatCmdSIM[i]!=0:
            ecatCmdSIM[i]=0
            esc.put("m{}.sdo.cmdSIM=1".format(i))
        else:
            esc.put("m{}.sdo.cmdSIM=0".format(i))
        time.sleep(0.5)
        continue
    ecatDrvKpN[i]=1; ecatDrvKpD[i]=1;
    ecatDrvKvN[i]=1; ecatDrvKvD[i]=1;
    ecatDrvKsN[i]=1; ecatDrvKsD[i]=1; ecatDrvINV[i]=0;

for i in range(1,8):         #**速度限制的單位調整
    ecatSpdBRK[i]=ecatSpdBRK[i]*ecatDrvKpN[i]/ecatDrvKpD[i];
    ecatSpdMOV[i]=ecatSpdMOV[i]*ecatDrvKpN[i]/ecatDrvKpD[i];
    
    ecatDrvMxH[i]=modelMotor[i-1][1]*1000
    ecatDrvMxL[i]=modelMotor[i-1][2]*1000

#角度極限保護
esc.segR("drvMxH",ecatDrvMxH)
esc.segR("drvMxL",ecatDrvMxL)
                             #**電子齒輪/開機角度/轉動極性
esc.segR("drvKpN",ecatDrvKpN)
esc.segR("drvKpD",ecatDrvKpD)
esc.segR("drvKvN",ecatDrvKvN)
esc.segR("drvKvD",ecatDrvKvD)
esc.segR("drvKsN",ecatDrvKsN)
esc.segR("drvKsD",ecatDrvKsD)
esc.segR("drvPOS",ecatDrvPOS)
esc.segR("drvINV",ecatDrvINV)
                             #**剛性/模擬設置
esc.segR("simANG",["",0,0,0,0,0,0,0])
esc.segR("simSPD",["",0,0,0,0,0,0,0])
esc.segR("cmdRST",["",0,0,0,0,0,0,0])
esc.segR("drvOLD",ecatDrvOLD)
esc.segR("cmdSIM",ecatCmdSIM)
esc.segR("simKP", ecatSimKP)
esc.segR("simKV", ecatSimKV)
esc.segR("simKG", ecatSimKG)
esc.segR("simKM", ecatSimKM)
esc.segR("simKA", ecatSimKA)
esc.segR("simKS", ecatSimKS)
esc.segR("simKS0",ecatSimKS0)
                             #**清除error
esc.put("m0.map.netCMD=0x06"); time.sleep(1.0)
esc.put("m0.map.netCMD=0x80"); time.sleep(0.1)
esc.put("m0.map.netCMD=0x06"); time.sleep(0.1)
                   #**進入控制模式
n=ecatServoN;                #**實際軸數
for i in range(1,n+1):       #**設置CSP模式
    esc.setAxis(i); esc.put("m@.sdo.0x6060.B=8")
    esc.put("m@.map.cmdOFF=0")         #**開啟doCommand() =啟動運動控制
esc.put("m0.map.netCMD=0x07"); time.sleep(2.0)   #**這時剎車脫離
esc.put("m0.map.netCMD=0x0f");                   #**這時伺服作動
                             #**開機對位(以目前角度設置起始命令)
#esc.drvPOS(ecatDrvPOS)       #**機械零點
#esc.segANG(ecatDrvPOS)       #**模擬角度(開機零點)

x=esc.segR("cmdANG"); d=[""]+list(x)   #**讀取目前角度
esc.segR("cmdPOS",d)                   #**重設開機命令
#esc.segR("drvSPD",ecatSpdMOV)          #**取消輸出保護,恢復正常
esc.segR("drvSPD",["",2500,2500,2500,2500,2500,2500,2500])

#目前已取消                   #**剎車脫離(POS正負晃動)
#esc.segR("drvSPD",ecatSpdBRK)
#x=esc.segR("cmdPOS"); dx=ecatAngBRK; dt=ecatTimBRK;
#d=[""]+list(x+dx); esc.segR("cmdPOS",d); time.sleep(dt)    #**先正轉
#d=[""]+list(x-dx); esc.segR("cmdPOS",d); time.sleep(dt)    #**再反轉
#d=[""]+list(x);    esc.segR("cmdPOS",d); time.sleep(dt)    #**再還原
#esc.segR("drvSPD",ecatSpdMOV)
