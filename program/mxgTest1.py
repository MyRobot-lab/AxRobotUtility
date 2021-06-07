from AxRobotData import *
#**********************************************************
# mxgTest1.py : XY-plot of mxG[j@] with @=1~6
#
                             #**導入Library
import numpy             as np
import matplotlib
import matplotlib.pyplot as plt
import time
from types import *

#kg=0; s=input("kg= ")        #**參數設置(夾爪重量)
#if len(s)>0:
#    ss=s.split(','); n=len(ss)
#    if n>0: kg=int(ss[0])    #**設置base和tool
esc.pSet("tool",["robot",35.,0.,80.,0.,0.,0.,0.])
esc.pSet("base",["world", 0.,0.,50.,0.,0.,0.,0.]); esc.modelToolM([1,kg,0,0,0]);

x=np.zeros(361);   ch1=np.zeros(361); ch2=np.zeros(361); ch3=np.zeros(361)
ch4=np.zeros(361); ch5=np.zeros(361); ch6=np.zeros(361); ch7=np.zeros(361)
timestart=time.time()
print("for Start:")
for i in range(361):
    esc.pSet("base",["world",0.,0.,500.,0.,90.,0.,0.]); esc.modelToolM([1,kg,0,0,0]);
    x[i]=i-180;  p=[x[i],90, 0, 0, 0, 0, 0]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    esc.pSet("base",["world",0.,0.,50., 0.,0., 0.,0.]); esc.modelToolM([1,kg,0,0,0]);
    ch1[i]=d[0]; p=[ 0,x[i], 0, 0, 0, 0, 0]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    ch2[i]=d[1]; p=[ 0,90,x[i],90, 0, 0, 0]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    ch3[i]=d[2]; p=[ 0, 0, 0,x[i], 0, 0, 0]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    ch4[i]=d[3]; p=[ 0, 0, 0,90,x[i],90, 0]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    ch5[i]=d[4]; p=[ 0, 0, 0, 0, 0,x[i], 0]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    ch6[i]=d[5]; p=[ 0, 0, 0, 0, 0,90,x[i]]; d=esc.getM(20,p); d=esc.getM(21); d=esc.getM(22);
    ch7[i]=d[6];
print("for End:",time.time()-timestart)
                                           #**繪圖處理
#plt.figure(figsize=(6,3),dpi=80)
#plt.subplot(711);                      #**subplot#1
#plt.plot(x,ch1,color="red",  label="mxG(1)")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(712);                      #**subplot#2
#plt.plot(x,ch2,color="green",label="mxG(2)")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(713);                      #**subplot#3
#plt.plot(x,ch3,color="blue", label="mxG(3)")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(714);                      #**subplot#4
#plt.plot(x,ch4,color="black",label="mxG(4)")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(715);                      #**subplot#5
#plt.plot(x,ch5,color="red",  label="mxG(5)")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(716);                      #**subplot#6
#plt.plot(x,ch6,color="green",label="mxG(6)")
#plt.grid(True); plt.legend(loc="upper right")
#plt.subplot(717);                      #**subplot#7
#plt.plot(x,ch7,color="blue", label="mxG(7)")
#plt.grid(True); plt.legend(loc="upper right")
#
#plt.show()                             #**顯示畫面
