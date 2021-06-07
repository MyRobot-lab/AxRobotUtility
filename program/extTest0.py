from AxRobotData import *

print("***** extTest0()");

for i in range(1,8):         #**預設模擬部分的助力參數
    if ecatCmdSIM[i]==0:
        continue
    ecatExtKG [i]=   -ecatSimKG [i];
    ecatExtKM [i]=    ecatSimKM [i];
    ecatExtKA [i]=    ecatSimKA [i];
    ecatExtKV [i]=    ecatSimKS [i];
    ecatExtKV0[i]=    ecatSimKS0[i];
    ecatExtKS [i]=int(ecatSimKS [i]*0.8);
    ecatExtKS0[i]=int(ecatSimKS0[i]*0.8);
    ecatExtSPD[i]=300;
    ecatExtSP0[i]= 20;
    ecatExtBRK[i]=200;
    ecatExtMXC[i]=  0;
    ecatExtHLD[i]= 20;
                             #**設置助力參數
esc.segR("extKG",  ecatExtKG);  #print("extKG=", ecatExtKG)
esc.segR("extKM",  ecatExtKM);  #print("extKM=", ecatExtKM)
esc.segR("extKA",  ecatExtKA);  #print("extKA=", ecatExtKA)
esc.segR("extKV",  ecatExtKV);  #print("extKV=", ecatExtKV)
esc.segR("extKV0", ecatExtKV0); #print("extKV0=",ecatExtKV0)
esc.segR("extKS",  ecatExtKS);  #print("extKS=", ecatExtKS)
esc.segR("extKS0", ecatExtKS0); #print("extKS0=",ecatExtKS0)

esc.segR("extSPD", ecatExtSPD); #print("extSPD=",ecatExtSPD)
esc.segR("extSPD0",ecatExtSP0); #print("extSP0=",ecatExtSP0)
esc.segR("extBRK", ecatExtBRK); #print("extBRK=",ecatExtBRK)
esc.segR("extMXC", ecatExtMXC); #print("extMXC=",ecatExtMXC)
esc.segR("extHLD", ecatExtHLD); #print("extHLD=",ecatExtHLD)
