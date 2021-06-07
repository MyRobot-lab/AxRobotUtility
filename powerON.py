
import escMotion                       #**導入工具庫
esc=escMotion.ESC("COM5",True)              #**連線USB和3D模擬器
exec(open("escTest0.py","rb").read())       #**啟動EtherCAT連線,  之後就可設置esc參數
exec(open("sdoTest0.py","rb").read())  #**啟動SDO環境(sts=2),之後就可設置sdo參數
exec(open("pdoTest0.py","rb").read())  #**啟動PDO環境(sts=8),之後就是realtime通訊
exec(open("drvTest0.py","rb").read())  #**啟動伺服驅動,進入(CSP)控制模式
exec(open("movTest0.py","rb").read())      #**建構URDF模型,之後可執行運動控制

