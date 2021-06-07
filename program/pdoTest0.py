
import time
print("***** pdoTest0()");

esc.put("m0.map.pdoCMD=0")
esc.put("m0.map.pdoNUM="+str(ecatServoN))   #**設置機械手軸數
esc.put("m0.map.cmdMXC=1000")

Rx0=hex(ecatPdoRx0);         #**SDO的讀寫區域
RxN=str(ecatPdoRxN); print("pdoRx0="+Rx0,"pdoRxN="+RxN)
Tx0=hex(ecatPdoTx0);
TxN=str(ecatPdoTxN); print("pdoTx0="+Tx0,"pdoTxN="+TxN)

n=ecatServoN;     #**取得連線裝置的總數
for i in range(n): 
    dev=ecatDevices[i]; seq=i+1
    if dev<1 or dev>8: continue
    esc.setAxis(dev)         #**預設軸號
    esc.put("m@.map.pdoRx0="+Rx0+","+RxN)
    esc.put("m@.map.pdoTx0="+Tx0+","+TxN)
    esc.setAxis(seq) #新版測試(取消WatchDog)
    esc.put("m@.esc.0x810.W="+Rx0+","+RxN+",0x0024,0x0001")
    esc.put("m@.esc.0x818.W="+Tx0+","+TxN+",0x0020,0x0001")
    esc.put("m@.esc.0x420.W=0")
                   #**進入pre-OP模式
esc.put("m0.map.pdoCMD=2")

for i in range(n): #**進入save-OP模式
    dev=ecatDevices[i]; seq=i+1
    if dev<1 or dev>8: continue
    esc.setAxis(seq); esc.put("m@.esc.0x120.W=0x04");
esc.put("m0.map.pdoCMD=4"); time.sleep(0.2)

for i in range(n): #**進入OP模式
    dev=ecatDevices[i]; seq=i+1
    if dev<1 or dev>8: continue
    esc.setAxis(seq); esc.put("m@.esc.0x120.W=0x08");
esc.put("m0.map.pdoCMD=8"); time.sleep(0.2)

for i in range(n):           #**讀取SDO參數
    dev=ecatDevices[i]; seq=i+1
    if dev<1 or dev>8: continue
    esc.setAxis(seq); d1=esc.get("m@.esc.0x130.WX")
    esc.setAxis(dev); d2=esc.get("m@.sdo.0x1000.0.LX")
    print("Axis=",seq,d1,d2)
s=esc.put("m0.map.netSTS=3");
