
                   #**導入Library
import numpy             as np
import matplotlib
import matplotlib.pyplot as plt
import time
from AxRobotData import *

spd=50; dT=int(2000/spd)
print("Joint=",jN,"spd=",spd,"dT=",dT)

esc.setAxis(jN)
esc.put("dasCH=6,m@.map.cmdANG,m@.map.cmdMXM,m@.map.cmdAMP,m@.map.cmdOUT,m@.map.cmdACC,m@.map.cmdVEL")

esc.pMoveTo("p2");     time.sleep(0.5) #**進入起點
esc.dasStart(dT);                      #**DAS啟動
esc.pMoveTo("p3",spd); time.sleep(0.2) #**移動至終點
esc.pMoveTo("p2",spd); time.sleep(0.2) #**移動回起點
n=esc.dasStop(); print("das=",n)       #**DAS關閉
esc.pMoveTo("p1"); time.sleep(0.5)     #**回至零點
    
ch1=esc.dasGet(1,n)                #取得DAS記錄
ch2=esc.dasGet(2,n)
ch3=esc.dasGet(3,n)
ch4=esc.dasGet(4,n)
ch5=esc.dasGet(5,n)
ch6=esc.dasGet(6,n)
x=np.linspace(0,n*dT,n,endpoint=True)
x=x[0:len(ch1)]

for i in range(n):
    d=(ch2[i]>>16)&0xffff;
    if (d&0x8000)>0: d-=0x10000;
    ch2[i]=d

num=0; mxG=0; trq=0; thd=int(max(ch6)*9/10)
for j in range(n):
    if ch6[j]>thd:                           #**找出正向等速區
        num+=1; mxG+=ch2[j]; trq+=ch3[j]
    if ch6[j]<-thd:                          #**找出負向等速區
        num+=1; mxG+=ch2[j]; trq+=ch3[j]
if num>0:
    mxG=mxG/num; trq=trq/num
kG=int(trq*1000/mxG);                        #**計算統計值
print("n=",num,"kG=",kG,"mxG=",int(mxG),"trq=",int(trq))

                                       #**繪圖處理
#plt.figure(figsize=(6,8),dpi=80)
#plt.subplot(611)                   #**subplot#1
#plt.plot(x,ch1,color="red",  label="cmdANG")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(612)                   #**subplot#2
#plt.plot(x,ch2,color="green",label="cmdMXG")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(613)                   #**subplot#3
#plt.plot(x,ch3,color="blue", label="cmdAMP")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(614)                   #**subplot#4
#plt.plot(x,ch4,color="black",label="cmdOUT")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(615)                   #**subplot#5
#plt.plot(x,ch5,color="red",  label="cmdACC")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(616);                  #**subplot#6
#plt.plot(x,ch6,color="green",label="cmdVEL")
#plt.grid(True); plt.legend(loc="upper right")
#
#plt.show()                         #**顯示畫面
