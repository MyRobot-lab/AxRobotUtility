
import time                                      #**導入Library
from AxRobotData import *
                   #**   j1   j2   j3   j4   j5   j6   j7        設置測試點
esc.pSet('p1',['joint',   0,   0,   0,   0,   0,   0,   0])   #**p1=零點
esc.pSet('p2',['joint',   0,   0,   0,   0,   0,   0,   0])   #**p2=起點
esc.pSet('p3',['joint',   0,  degEnd,   0,   0,   0,   0,   0])   #**p3=終點
jS='2'; jN=2; print("joint=",jN)                 #**設置軸號
glo2={"jN":jN}
exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"kgTest0.py","rb").read())        #**參數預設
exec(open(dctAPP_CFIG["Ext_PY_PATH"]+"kgTestX.py","rb").read(), glo2)        #**測試執行
