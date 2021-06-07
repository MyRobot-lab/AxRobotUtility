
import time
                             #**剎車脫離(POS正負移動)
esc.segR("drvSPD",["",1000,250,250,250,250,250,250])
x=esc.segR("cmdPOS"); dx=300; dt=1.0   #**dx=30度/減速比
d=[""]+list(x+dx); esc.segR("cmdPOS",d); time.sleep(dt)    #**先正轉
d=[""]+list(x-dx); esc.segR("cmdPOS",d); time.sleep(dt)    #**再反轉
d=[""]+list(x);    esc.segR("cmdPOS",d); time.sleep(dt)    #**再還原
esc.segR("drvSPD",["",2500,250,250,250,250,250,250])
