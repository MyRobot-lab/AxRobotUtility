
                   #**導入Library
import numpy             as np
import matplotlib
import matplotlib.pyplot as plt
import time
from AxRobotData import *

spdP=np.zeros(10,dtype=int); spdN=np.zeros(10,dtype=int)
velP=np.zeros(10,dtype=int); velN=np.zeros(10,dtype=int)
outP=np.zeros(10,dtype=int); outN=np.zeros(10,dtype=int)
tab=[20,40,60,80,100,120,140,160,180,200]
nTest=10

esc.setAxis(jN)
esc.put("dasCH=6,m@.map.cmdANG,m@.map.cmdSPD,m@.map.cmdAMP,m@.map.cmdOUT,m@.map.cmdACC,m@.map.cmdVEL")

esc.pMoveTo("p2");         time.sleep(0.5) #**進入起點
for i in range(nTest):
    spd=tab[i]; dT=int(2000/spd)
    print("Joint=",jN,"spd=",spd,"dT=",dT)
    esc.dasStart(dT);                  #DAS啟動
    esc.pMoveTo("p3",spd); time.sleep(0.2) #**移動至終點
    esc.pMoveTo("p2",spd); time.sleep(0.2) #**移動回起點
    n=esc.dasStop();                   #DAS關閉
    print("das=",n)
    ch1=esc.dasGet(1,n)                #取得DAS記錄
    ch2=esc.dasGet(2,n)
    ch3=esc.dasGet(3,n)
    ch4=esc.dasGet(4,n)
    ch5=esc.dasGet(5,n)
    ch6=esc.dasGet(6,n)
    x=np.linspace(0,n*dT,n,endpoint=True)
    x=x[0:len(ch1)]

    num=0; vel=0; spd=0; out=0; thd=int(max(ch6)*9/10)
    for j in range(n):                           #**找出正向等速區
        if ch6[j]>thd:
            num+=1; vel+=ch6[j]; spd+=ch2[j]; out+=ch4[j]
    if num>0:
        vel=int(vel/num); spd=int(spd/num); out=int(out/num)
    spdP[i]=spd; velP[i]=vel; outP[i]=out        #**計算統計值
    print("n=",num,"spd=",spd,"vel=",vel,"out=",out)
    numIP = num
    spdIP = spd
    velIP = vel
    outIP = out
    num=0; vel=0; spd=0; out=0; 
    print("xn=", n) 
    print("xxn=", len(ch6))
    for j in range(n):                           #**找出負向等速區
        if ch6[j]<-thd:
            num+=1; vel+=ch6[j]; spd+=ch2[j]; out+=ch4[j]
    if num>0:
        vel=int(vel/num); spd=int(spd/num); out=int(out/num)
    print("xx")
    spdN[i]=spd; velN[i]=vel; outN[i]=out        #**計算統計值
    print("n=",num,"spd=",spd,"vel=",vel,"out=",out)
    numIN = num
    spdIN = spd
    velIN = vel
    outIN = out

    outM=int((outP[i]+outN[i])/2)
    outP[i]-=outM
    outN[i]-=outM
    print("mean=",outM,"outP=",outP[i],"outN=",outN[i])
    outM = num
    outMP = outP
    outMN = outN
                                       #**繪圖處理
    #plt.figure(figsize=(6,8),dpi=80)
    #plt.subplot(611)                   #**subplot#1
    #plt.plot(x,ch1,color="red",  label="cmdANG")
    #plt.grid(True); plt.legend(loc="upper right")
    #plt.subplot(612)                   #**subplot#2
    #plt.plot(x,ch2,color="green",label="cmdSPD")
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

    #plt.show()                         #**顯示畫面

esc.pMoveTo("p1"); time.sleep(0.5)     #**回至零點

if nTest>=9:
    c=np.polyfit(velP,outP,1)                  #**參數統計
    kv =int(c[0]*1000)
    kv0=int(c[1])
    print("kv=",kv,"kv0=",kv0)
    print("vel=",velP)
    print("out=",outP)
    kvP = kv
    kv0P = kv0
    velP = velP
    outVP = outP

    err=np.polyval(c,velP)-outP
    for i in range(nTest): err[i]=int(err[i])
    print("err=",err)
    errVP = err

    c=np.polyfit(velN,outN,1)                  #**參數統計
    kv =int(c[0]*1000)
    kv0=int(c[1])
    print("kv=",kv,"kv0=",kv0)
    print("vel=",velN)
    print("out=",outN)
    kvN = kv
    kv0N = kv0
    velN = velN
    outVN = outN

    err=np.polyval(c,velN)-outN
    for i in range(nTest): err[i]=int(err[i])
    print("err=",err)
    errVN = err

    c=np.polyfit(spdP,outP,1)                  #**參數統計
    ks =int(c[0]*1000)
    ks0=int(c[1])
    print("ks=",ks,"ks0=",ks0)
    print("spd=",spdP)
    print("out=",outP)
    ksP = ks
    ks0P = ks0
    spdP = spdP
    outSP = outP

    err=np.polyval(c,spdP)-outP
    for i in range(nTest): err[i]=int(err[i])
    print("err=",err)
    errSP = err

    c=np.polyfit(spdN,outN,1)                  #**參數統計
    ks =int(c[0]*1000)
    ks0=int(c[1])
    print("ks=",ks,"ks0=",ks0)
    print("spd=",spdN)
    print("out=",outN)
    ksN = ks
    ks0N = ks0
    spdN = spdN
    outSN = outN
    

    err=np.polyval(c,spdN)-outN
    for i in range(nTest): err[i]=int(err[i])
    print("err=",err)
    errSN = err

print("hhh")