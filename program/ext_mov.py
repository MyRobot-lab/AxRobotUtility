
import time                                      #**導入Library
import time                                      #**導入Library
                    #** j1  j2 j3  j4 j5 j6 j7        設置測試點
esc.pSet('p1',['joint',  0, 0, 0,  0, 0,  0, 0])   #**p1=零點
esc.pSet('p2',['joint',  0, 10, 0,60, 0,   90, 0])   #**p2=起點
esc.pSet('p3',['joint',  0, 0, 0,  0, 0,  0, 0])   #**p3=終點
jS='1'; jN=1; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[2696,8])    #**設置摩擦補償
esc.putR("m@.map.extKS",[2157,6])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG", 0)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)
jS='2'; jN=2; print("joint=",jN)                 #**設置軸號
                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[2935,221])    #**設置摩擦補償
esc.putR("m@.map.extKS",[2028,169])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG", -1143)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

jS='3'; jN=3; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[2398,14])    #**設置摩擦補償
esc.putR("m@.map.extKS",[2238,11])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG",0)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

jS='4'; jN=4; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[1897,22])    #**設置摩擦補償
esc.putR("m@.map.extKS",[1518,18])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG",-745)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

jS='5'; jN=5; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[835,385])    #**設置摩擦補償
esc.putR("m@.map.extKS",[668,308])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG", 0)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

jS='6'; jN=6; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[826,488])    #**設置摩擦補償
esc.putR("m@.map.extKS",[587,316])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG",-94)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

jS='7'; jN=7; print("joint=",jN)                 #**設置軸號

                                       #**限制恢復速度
esc.segR("drvSPD",["",500,500,500,500,500,500,500])

esc.putR("m0.map.cmdMXC",300)
esc.putR("m0.map.extENB",1)            #**啟動助力計算

esc.setAxis(jN)
esc.putR("m@.map.cmdOLD",0)            #**允許助力控制
esc.putR("m@.map.extKV",[734,445])    #**設置摩擦補償
esc.putR("m@.map.extKS",[587,356])
esc.putR("m@.map.extSPD",[200,10])
esc.putR("m@.map.extKG", 0)            #**設置重力
esc.putR("m@.map.extKM",[0,0])        #**設置慣量(同軸和偏心)

                   #**設置模擬參數
esc.putR("m@.simTRQ",0)      #**simTRQ=外力干擾(單位=0.1%)
esc.putR("m@.simKP" ,250)    #**simKP =位置環路的增益
esc.putR("m@.simKV" ,10000)  #**simKV =速度環路的增益
esc.putR("m@.simKG" ,1000)   #**simKG =重力計算的增益
esc.putR("m@.simKM",200)    #**simKM=同軸慣量(單位=0.1%)
esc.putR("m@.simKA" ,50)     #**simKA =偏心慣量的增益
esc.putR("m@.simKS" ,50)     #**simKS =動摩擦值的增益
esc.putR("m@.simKS0",200)    #**simKS0=靜摩擦值(單位=0.1%)

esc.pMoveTo("p1",100,800,100000000); time.sleep(10.5) #**進入起點
esc.pMoveTo("p2",100,800,100000000); time.sleep(10.5) #**移動至終點
esc.pMoveTo("p1",100,800,100000000); time.sleep(10.5) #**移動回起點
