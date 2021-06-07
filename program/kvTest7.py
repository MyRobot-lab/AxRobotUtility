
import time
from AxRobotData import *
                   #**   j1   j2   j3   j4   j5   j6   j7        設置測試點
esc.pSet('p1',['joint',   0,   0,   0,   0,   0,   0,   0])   #**p1=零點
esc.pSet('p2',['joint',   0,   0,   0,   0,   0,   0,  degEnd])   #**p2=起點
esc.pSet('p3',['joint',   0,   0,   0,   0,   0,   0, -degEnd])   #**p3=終點
jS='7'; jN=7; print("joint=",jN)                 #**設置軸號
glo2={"jN":jN}
exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"kvTest0.py","rb").read())        #**參數預設
exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"kvTestX.py","rb").read(),glo2)        #**測試執行
