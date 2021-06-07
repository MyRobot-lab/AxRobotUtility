
import time

print("***** simTest0()");
                             #**預設機械手定義和網路裝置
esc.modelURDF (modelURDF,modelAxis)    #**設置URDF模型
esc.modelToolM([1,0,0,0,0])            #**設置base和tool
esc.modelMotor(modelMotor)             #**設置馬達參數
esc.modelGainG(modelGainG)             #**設置gainG[]
esc.modelGainM(modelGainM)             #**設置gainM[]
esc.modelBiasM(modelBiasM)             #**設置biasM[]
esc.putR("extENB",1);                  #**extENB=1,   啟動矩陣運算
                             #**重設開機參數
s=esc.put("m0.map.pdoCMD=0");          #**關閉通訊
s=esc.put("m0.map.netCMD=0");          #**關閉伺服和模擬
s=esc.put("m0.map.almENB=0");          #**關閉警報
s=esc.put("m0.map.almMSK=0xff");       #**設置警報軸
                             #**輸出保護(命令=回授:限制出力為零)
esc.segR("drvSPD",["",0,0,0,0,0,0,0])
                             #**電子齒輪/開機角度/轉動極性
esc.segR("drvKpN",["",1,1,1,1,1,1,1])
esc.segR("drvKpD",["",1,1,1,1,1,1,1])
esc.segR("drvKvN",["",1,1,1,1,1,1,1])
esc.segR("drvKvD",["",1,1,1,1,1,1,1])
esc.segR("drvKsN",["",1,1,1,1,1,1,1])
esc.segR("drvKsD",["",1,1,1,1,1,1,1])
esc.segR("drvINV",["",0,0,0,0,0,0,0])
esc.segR("drvPOS",ecatDrvPOS)
                             #**設置模擬參數
esc.segR("simKP", ecatSimKP);
esc.segR("simKV", ecatSimKV);
esc.segR("simKG", ecatSimKG);
esc.segR("simKM", ecatSimKM);
esc.segR("simKA", ecatSimKA);
esc.segR("simKS", ecatSimKS);
esc.segR("simKS0",ecatSimKS0);
                             #*清除助力參數
esc.segR("extKG",["",0,0,0,0,0,0,0]);
esc.segR("extKM",["",0,0,0,0,0,0,0]);
esc.segR("extKA",["",0,0,0,0,0,0,0]);
esc.segR("extKV",["",0,0,0,0,0,0,0]);
esc.segR("extKV0",["",0,0,0,0,0,0,0]);
esc.segR("extKS", ["",0,0,0,0,0,0,0]);
esc.segR("extKS0",["",0,0,0,0,0,0,0]);
                             #**啟動模擬環境
ecatCmdSIM=["",1,1,1,1,1,1,1];         #**各軸模擬啟動
esc.segR("cmdSIM",ecatCmdSIM);
esc.segR("drvOLD",["",0,0,0,0,0,0,0])  #**設置助力模式
esc.segR("drvSPD",["",10000,10000,10000,10000,10000,10000,10000])
esc.modelURDF(modelURDF,modelAxis)     #**設置機械手模型
s=esc.put("m0.map.netCMD=0x0f");       #**開啟伺服模式
s=esc.put("m0.map.cmdMXC=1000");       #**取消助力控制

esc.segR("cmdPOS",["",0,0,0,0,0,0,0])
esc.segR("simANG",["",0,0,0,0,0,0,0])
esc.segR("simSPD",["",0,0,0,0,0,0,0])
s=esc.put("m0.map.segI=0,0");
s=esc.put("m0.map.segK=0,0");
