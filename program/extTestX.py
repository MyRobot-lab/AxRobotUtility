
                   #**導入Library
import numpy             as np
import matplotlib
import matplotlib.pyplot as plt
import time
from AxRobotData import *

esc.setAxis(jN)
esc.put("dasCH=9,m@.map.cmdANG,m@.map.cmdSPD,m@.map.cmdAMP,m@.map.cmdOUT,m@.map.cmdMXD,m@.map.cmdTRQ,m@.map.cmdACC,m@.map.cmdVEL,m@.map.cmdERR")

dT=int(2000/spd)
print("Joint=",jN,"spd=",spd,"dT=",dT)

esc.pMoveTo("p2");     time.sleep(0.5) #**進入起點
esc.dasStart(dT);                      #**DAS啟動
esc.pMoveTo("p3",spd); time.sleep(0.8) #**移動至終點
esc.pMoveTo("p2",spd); time.sleep(2.0) #**移動回起點
n=esc.dasStop();  print("das=",n)      #**DAS關閉
esc.pMoveTo("p1");     time.sleep(0.5) #**回至零點

ch1=esc.dasGet(1,n)                    #取得DAS記錄
ch2=esc.dasGet(2,n)
ch3=esc.dasGet(3,n)
ch4=esc.dasGet(4,n)
ch5=esc.dasGet(5,n)
ch6=esc.dasGet(6,n)
ch7=esc.dasGet(7,n)
ch8=esc.dasGet(8,n)
ch9=esc.dasGet(9,n)
x=np.linspace(0,n*dT,n,endpoint=True)
x=x[0:len(ch1)]
                                       #**繪圖處理
#plt.figure(figsize=(6,8),dpi=80)
#plt.subplot(911)             #**subplot#1
#plt.plot(x,ch1,color="red",  label="cmdANG")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(912)             #**subplot#2
#plt.plot(x,ch2,color="green",label="cmdSPD")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(913)             #**subplot#3
#plt.plot(x,ch3,color="blue", label="cmdAMP")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(914)             #**subplot#4
#plt.plot(x,ch4,color="black",label="cmdOUT")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(915);            #**subplot#5
#plt.plot(x,ch5,color="red",  label="cmdMXD")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(916)             #**subplot#6
#plt.plot(x,ch6,color="green",label="cmdTRQ")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(917)             #**subplot#7
#plt.plot(x,ch7,color="blue", label="cmdACC")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(918);            #**subplot#8
#plt.plot(x,ch8,color="black",label="cmdVEL")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(919)             #**subplot#9
#plt.plot(x,ch9,color="red",  label="cmdERR")
#plt.grid(True); plt.legend(loc="upper right")
#
#plt.show()                             #**顯示畫面
