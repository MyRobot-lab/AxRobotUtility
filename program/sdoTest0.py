import time
print("***** sdoTest0()");

print("Devices=",ecatDevices);         #**網路連線順序
print("DeviceN=",ecatDeviceN);         #**網路裝置總數
print("ServoN =",ecatServoN);          #**伺服驅動總數
#ecatDevices=[1,2,3,4,5,6,7,8,9]
#注意: SDO編號和ESC編號不同
#      ESC編號是以連線順序為準,依連線順序為#1~#9
#      SDO編號是以設置編號為準,0x1001=#1,..,0x1009=#9
#      所有裝置都必須進入SDO模式,可用SDO讀寫.但只有(#1~#8)需要進入PDO模式.      

                   #**設置Init模式並清除參數
s=esc.put("m0.esc.0x120.W=1"); time.sleep(0.01)
s=esc.put("m0.esc.0x101.B=0")
s=esc.put("m0.esc.0x600.L=0",64)
s=esc.put("m0.esc.0x800.L=0",32)
s=esc.put("m0.esc.0x200.W=4")
s=esc.put("m0.esc.0x300.W=0",4)
s=esc.put("m0.esc.0x910.L=0",8)
s=esc.put("m0.esc.0x981.B=0")
s=esc.put("m0.esc.0x103.B=0")

n=ecatDeviceN      #**取得連線裝置的總數
for i in range(n): #**設置驅動器的絕對位址
    esc.setAxis(i+1);
    s=esc.putR("m@.esc.0x10.W",ecatDevices[i]+0x1000);
    s=esc.putR("m@.esc.0x500.B",0x01)

Rx0=hex(ecatSdoRx0);         #**SDO的讀寫區域
RxN=hex(ecatSdoRxN); print("sdoRx0="+Rx0,"sdoRxN="+RxN)
Tx0=hex(ecatSdoTx0);
TxN=hex(ecatSdoTxN); print("sdoTx0="+Tx0,"sdoTxN="+TxN)
                  
for i in range(n): #**設置SDO環境
    dev=ecatDevices[i]; seq=i+1;
    esc.setAxis(seq)         #**進入Init模式
    s=esc.put("m@.esc.0x120.W=0x01");                        time.sleep(0.01)
                             #**進入pre-OP模式
    s=esc.put("m@.esc.0x800.W="+Rx0+","+RxN+",0x0026,0x0001")
    s=esc.put("m@.esc.0x808.W="+Tx0+","+TxN+",0x0022,0x0001"); time.sleep(0.01)
    s=esc.put("m@.esc.0x120.W=0x02");                        time.sleep(0.01)
    esc.setAxis(dev)         #**設置SDO參數
    esc.put("m@.map.sdoRx0="+Rx0)
    esc.put("m@.map.sdoRxN="+RxN)
    esc.put("m@.map.sdoTx0="+Tx0)
    esc.put("m@.map.sdoTxN="+TxN)

s=esc.put("m0.map.netSTS=2");
for i in range(n):           #**讀取SDO參數
    dev=ecatDevices[i]; seq=i+1
    esc.setAxis(dev); d1=esc.get("m@.sdo.0x1000.0.LX")
    print("Axis=",seq,d1)

for i in range(n): #**準備PDO表格
    dev=ecatDevices[i]
    if dev<1 or dev>8: continue
    esc.setAxis(dev)         #**預設軸號
                             #**設置RxPDO表格
    esc.put("m@.sdo.0x1C12.0.WX=0");          time.sleep(0.01)
    esc.put("m@.sdo.0x1600.0.WX=0");          time.sleep(0.01)
    esc.put("m@.sdo.0x1600.1.LX=0x60400010"); time.sleep(0.01)
    esc.put("m@.sdo.0x1600.2.LX=0x607A0020"); time.sleep(0.01)
    esc.put("m@.sdo.0x1600.3.LX=0x60B20010"); time.sleep(0.01)
    esc.put("m@.sdo.0x1600.4.LX=0x60B10020"); time.sleep(0.01)
    esc.put("m@.sdo.0x1600.5.LX=0x60B30010"); time.sleep(0.01)
    esc.put("m@.sdo.0x1600.0.WX=5");          time.sleep(0.01)
    esc.put("m@.sdo.0x1C12.0.WX=1");          time.sleep(0.01)
                             #**設置TxPDO表格
    esc.put("m@.sdo.0x1C13.0.WX=0");          time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.0.WX=0");          time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.1.LX=0x60410010"); time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.2.LX=0x60640020"); time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.3.LX=0x606C0020"); time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.4.LX=0x60770010"); time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.5.LX=0x60890010"); time.sleep(0.01)
    esc.put("m@.sdo.0x1A00.0.WX=5");          time.sleep(0.01)
    esc.put("m@.sdo.0x1C13.0.WX=1");          time.sleep(0.01)
