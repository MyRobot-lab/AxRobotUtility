from AxRobotData import *

esc.putR("m0.map.cmdMXC",1000)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.extKV",[0,0])         #**取消摩擦補償
esc.putR("m@.map.extKS",[0,0])
esc.putR("m@.map.extKG",-1143)     #**取消重力和慣量

esc.segR("drvSPD",["",50000,500,500,500,500,500,500])

                   #**設置模擬參數
esc.putR("m@.simTRQ",0)      #**simTRQ=外力干擾(單位=0.1%)
esc.putR("m@.simKP" ,250)    #**simKP =位置環路的增益
esc.putR("m@.simKV" ,10000)  #**simKV =速度環路的增益
esc.putR("m@.simKG" ,1000)   #**simKG =重力計算的增益
esc.putR("m@.simKM" ,200)    #**simKM =同軸慣量
esc.putR("m@.simKA" ,50)     #**simKA =偏心慣量的增益
esc.putR("m@.simKS" ,50)     #**simKS =動摩擦值的增益
esc.putR("m@.simKS0",200)    #**simKS0=靜摩擦值(單位=0.1%)
