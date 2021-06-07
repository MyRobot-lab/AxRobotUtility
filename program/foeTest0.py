
import time

s=esc.put ("m0.map.pdoCMD=0");             time.sleep(0.2) #**關閉通訊
s=esc.put ("m0.map.pdoNUM=0")
s=esc.put ("m0.map.netCMD=0");                             #**關閉伺服和模擬
s=esc.put ("m0.map.almENB=0");                             #**關閉警報
s=esc.put ("m0.map.netSTS=0");             time.sleep(0.2)

                   #**驅動器連線確認
s=esc.get("m0.esc.0xffff.9.B"); n=int(s); print("驅動器="+str(n));
                   #**設置Init模式並清除參數
if n != 0:
    s=esc.put("m0.esc.0x120.W=1"); time.sleep(0.01)
    s=esc.put("m0.esc.0x101.B=0")
    s=esc.put("m0.esc.0x600.L=0",64)
    s=esc.put("m0.esc.0x800.L=0",32)
    s=esc.put("m0.esc.0x200.W=4")
    s=esc.put("m0.esc.0x300.W=0",4)
    s=esc.put("m0.esc.0x910.L=0",8)
    s=esc.put("m0.esc.0x981.B=0")
    s=esc.put("m0.esc.0x103.B=0")

                   #**設置驅動器的絕對位址
if n>=1: s=esc.put("m1.esc.0x10.W=0x1001"); s=esc.put("m1.esc.0x500.B=0x01")
if n>=2: s=esc.put("m2.esc.0x10.W=0x1002"); s=esc.put("m2.esc.0x500.B=0x01")
if n>=3: s=esc.put("m3.esc.0x10.W=0x1003"); s=esc.put("m3.esc.0x500.B=0x01")
if n>=4: s=esc.put("m4.esc.0x10.W=0x1004"); s=esc.put("m4.esc.0x500.B=0x01")
if n>=5: s=esc.put("m5.esc.0x10.W=0x1005"); s=esc.put("m5.esc.0x500.B=0x01")
if n>=6: s=esc.put("m6.esc.0x10.W=0x1006"); s=esc.put("m6.esc.0x500.B=0x01")
if n>=7: s=esc.put("m7.esc.0x10.W=0x1007"); s=esc.put("m7.esc.0x500.B=0x01")
if n>=8: s=esc.put("m8.esc.0x10.W=0x1008"); s=esc.put("m8.esc.0x500.B=0x01")
if n>=9: s=esc.put("m9.esc.0x10.W=0x1009"); s=esc.put("m9.esc.0x500.B=0x01")

for i in range(n):
    esc.setAxis(i+1)         #**預設軸號
                             #**進入BootStrap模式
    s=esc.put("m@.esc.0x800.W=0x1000,0x0080,0x0026,0x0001")
    s=esc.put("m@.esc.0x808.W=0x1080,0x0080,0x0022,0x0001"); time.sleep(0.1)
    s=esc.put("m@.esc.0x120.W=0x03");                        time.sleep(0.1)
                             #**設置SDO參數
    esc.put("m@.map.sdoRx0=0x1000")
    esc.put("m@.map.sdoRxN=0x80")
    esc.put("m@.map.sdoTx0=0x1080")
    esc.put("m@.map.sdoTxN=0x80")
    s=esc.get("m@.esc.0x130.W"); print("esc.130=",s)
