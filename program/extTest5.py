
import time
from AxRobotData import *

                   #**   j1   j2   j3   j4   j5   j6   j7        設置測試點
esc.pSet('p1',['joint',   0,   0,   0,   0,   0,   0,   0])   #**p1=零點
esc.pSet('p2',['joint',   0,   0,   0,   0,  degEnd,   0,   0])   #**p2=起點
esc.pSet('p3',['joint',   0,   0,   0,   0, -degEnd,   0,   0])   #**p3=終點
jS='5'; jN=5; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[dynamicfriction,staticfriction])    #**設置摩擦補償
esc.putR("m@.map.extKS",[suspensiondynamicfriction,suspensionstaticfriction])
esc.putR("m@.map.extSPD",[speedlimit,decelerationlimit])
esc.putR("m@.map.extKG", gravity)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

                   #**設置模擬參數
esc.putR("m@.simTRQ",0)      #**simTRQ=外力干擾(單位=0.1%)
esc.putR("m@.simKP" ,250)    #**simKP =位置環路的增益
esc.putR("m@.simKV" ,10000)  #**simKV =速度環路的增益
esc.putR("m@.simKG" ,1000)   #**simKG =重力計算的增益
esc.putR("m@.simKA0",200)    #**simKA0=同軸慣量(單位=0.1%)
esc.putR("m@.simKA" ,50)     #**simKA =偏心慣量的增益
esc.putR("m@.simKS" ,50)     #**simKS =動摩擦值的增益
esc.putR("m@.simKS0",200)    #**simKS0=靜摩擦值(單位=0.1%)

nTest=1
for i in range(nTest):       #**測試執行
    spd=100*(i+1); 
    glo2={"jN":jN, "spd":spd}
    exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"extTestX.py","rb").read(), glo2)
