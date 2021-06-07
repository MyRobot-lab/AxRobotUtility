import mathRobot as mm       #**座標計算

print("***** movTest0()")

#**********************************************************
# 機械手的參數設置
#**********************************************************
mm.pSet("base",modelBase)
mm.pSet("work",modelWork)
mm.pSet("tool",modelTool)
        

esc.modelURDF(modelURDF,modelAxis)
esc.modelToolM([1,0,0,0,0])            #**設置base和tool
esc.modelMotor(modelMotor)             #**設置馬達參數
esc.modelGainG(modelGainG)             #**設置gainG[]
esc.modelGainM(modelGainM)             #**設置gainM[]
esc.modelBiasM(modelBiasM)             #**設置biasM[]
esc.modelArm7(Joint3AngLimit)

esc.putR("extENB",1);                  #**extENB=1,啟動矩陣運算

#esc.putR("netCMD",0x0f);               #**netCMD=0x0f,設置伺服作動
esc.putR("cmdMXC",1000);               #**cmdMXC=1000,取消助力控制
esc.putR("almMSK",0x3f);               #**almMSK=0x3f
esc.putR("almENB",0);                  #**almENB=0,   取消警報處理
esc.putR("segMOD",3);                  #**segMOD=3,   模式=[自動]
esc.putR("segSTS",0);                  #**segSTS=0,   狀態=[正常]
#esc.segR("simTRQ",["",0,0,0,0,0,0,0])

print("nAxis=",esc.getR("m0.map.nAxis"))

print("***** EtherCAT連線完畢,可以執行機械手控制");
