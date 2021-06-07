
import win32com.client       #**Text-To-Speech(TTS)
import numpy as np
import time,copy,os,math,threading
#from   types import *        #**格式定義
import urllib                #**HTTP連線
import http.client as httplib
import serial                #**連線工具
import mathRobot as mm       #**座標計算
import AxRobotData

class ESC:                   #***** pmcBoard連線宣告
    def __init__(self,port="",simu=True):
        self.t0=time.time()-1          #**設置更新時間
        self._pipe=None; self.ip=None; self.com=None
        if simu:         self.pipeOpen()
        if len(port)>5:  self.ip=port;   port=""
        if len(port)>3:  self.com=serial.Serial(port,115200,timeout=1)
        self.mmReset();                #**機械手座標預設
        self._axis  =0
        self._scmd  =""
        self._header=bytearray(32)
        self._buffer=bytearray(116)
        self._map   =[0]*100
        self._status = None
        self._err = []
        self._joint=["joint",0.,0.,0.,0.,0.,0.,0.]
        self._track=["joint",0.,0.,0.,0.,0.,0.,0.]
        self._robot=["base", 0.,0.,0.,0.,0.,0.,0.]
        self._vel=["",0,0,0,0,0,0,0]
        self._acc=["",0,0,0,0,0,0,0]
        self._trq=["",0,0,0,0,0,0,0]
        self._mxC=["",0,0,0,0,0,0,0]
        self._spd=["",0,0,0,0,0,0,0]
        self._amp=["",0,0,0,0,0,0,0]
        self._out=["",0,0,0,0,0,0,0]
        self._mxM=["",0,0,0,0,0,0,0]
        self._mxG=["",0,0,0,0,0,0,0]
        self._nAxis  =7
        self._ratio=0
        self._table=0
        self._count=0
        self._running=0
        self._update=0
        self._remote=False
        self._lockComm=threading.Lock();
        self._lockPipe=threading.Lock();
        self._spdMM=100; self._spdDEG=100; self._spdFree=100
        self._dstMM=100; self._dstDEG=100; self._dstFree=100
        self.CommColiChk = 0
        self.CommColiErr = 0
        self.CommTimeOut = 0
        self.SegLostErr = 0
        self.FoeTimeOut = 0
        self.mm = mm
        self._lockPtAcc=threading.Lock();
        # self._speak=win32com.client.Dispatch("SAPI.SpVoice")
        self.mapVar={        #***** map[]位址對照表
            'segBLKe':  1,'segDEC':  1,'segK'  :  2,'segMS' :  3,'segSTS':  4,'segMOD':  5,'segCMD':  6,'segI'  :  7,'segN'  :  8,'netSTS':  9,
            'cmdBLKe': 10,'cmdPOS': 10,'cmdVEL': 11,'cmdACC': 12,'cmdTRQ': 13,'cmdMXD': 14,'cmdANG': 15,'cmdSPD': 16,'cmdAMP': 17,'cmdOUT':  18,
            'mxcBLK' : 90,'cmdMXC': 90,'cmdMXM': 91,'cmdMXG': 92,
            'cmdBLK' :100,'cmdERR':100,'cmdTG' :101,'cmdTI' :102,'cmdTF' :103,'cmdDT' :104,'cmdSIM':105,'cmdRST':106,'cmdOLD':107,'cmdOFF': 108,
            'sdoBLK' :110,'sdoRx0':110,'sdoRxN':111,'sdoTx0':112,'sdoTxN':113,'pdoRx0':114,'pdoRxN':115,'pdoTx0':116,'pdoTxN':117,
            'drvBLK' :120,'drvORG':120,'drvINV':121,'drvMxH':122,'drvMxL':123,'drvKpN':124,'drvKpD':125,'drvKvN':126,'drvKvD':127,'drvKsN': 128,'drvKsD':129,
            'drvBLKe':130,'drvPOS':130,'drvSPD':131,'drvTRQ' :132,'drvOLD' :133,'drvHLD' :134,'drvERR':135,
            'extBLK' :140,'extKG' :140,'extKM' :141,'extKA' :142,'extKV' :143,'extKV0':144,'extKS' :145,'extKS0':146,'extSPD':147,'extSPD0':148,'extBRK':149,
            'extBLKe':150,'extMXC':150,'extHLD':151,'oldVEL':152,'oldOUT':153,'oldV0' :154,'oldP1' :155,'oldP2' :156,'oldP3' :157,'oldM1'  :158,'oldM2' :159,
            'segBLK' :160,'segPOS':160,'segSPD':161,'segACC':162,'segF0' :163,'segP0' :164,'segS0' :165,'segS1' :166,'segHLD':167,
            'escBLK' :170,'escCMD':170,'escPOS':171,'escVEL':172,'escTRQ':173,'escMXC':174,'escANG':175,'escSPD':176,'escAMP':177,'escOUT' :178,'escSTS':179,
            'simBLK' :180,'simTRQ':180,'simSPD':181,'simANG':182,'simKP' :183,'simKV' :184,'simKG' :185,'simKM' :186,'simKA' :187,'simKS'  :188,'simKS0':189,'simANG0':190,
            'almBLK' :900,'almENB':900,'almMSK':901,'almANG1':902,'almANG2':903,'almSPD0':904,'almMS' :905,'almMOD':906,                      'almBRK':909,
            'tstBLK' :920,'testD0':920,'testD1':921,'testD2' :922,'testD3' :923,'testD4' :924,'testD5':925,'testD6':926,'testD7':927,'testD8':928,'testD9':929,
            'clkBLK':1000,'sysCLK':1000,'sys20K':1001,'sysLOP':1002,'sysKHZ':1003,'sysON' :1004,'sysOFF' :1005,                                       'powerON':1009,
            'ledBLK':1010,'ledR'  :1010,'ledG'  :1011,'ledY'  :1012,'ledB'  :1013,'ledMS' :1014,'ledBITS':1015,'pKey':1016,'pMask':1017,'pInput':1018,'pOutput':1019,
            'sysBLK':1020,'sysVERS':1020,'sysDATE':1021,'romVERS':1022,'romDATE':1023,'pdoCMD' :1024,'pdoNUM' :1025,'sdoSTS' :1026,'sdoERR' :1027,'netCMD' :1028,'extENB' :1029,
            'dasBLK' :1100,'dasN'   :1100,'dasCMD' :1101,'dasMS'  :1102,'dasDT'  :1103,'dasMAX' :1104,'dasSIZ' :1105,
            'dasBLKe':1110,'dasCH'  :1110,'dasV1'  :1111,'dasV2'  :1112,'dasV3'  :1113,'dasV4'  :1114,'dasV5'  :1115,'dasV6'  :1116,'dasV7'  :1117,'dasV8'  :1118,'dasV9'  :1119,
            'maxBLK' :1150,'nAxis'  :1150,'maxSPD' :1151,
            'mmBLK'  :1160, 'mmNum' :1160, 'mmSpd' :1161, 'mmAcc' :1162,'mmDec'  :1163,'spdM'   :1164,               't0M'    :1166,'t1M'    :1167,'t2M'    :1168,'t9M'    :1169,
            'dbgBLK' :1400,'coeERR' :1400,'ldpERR' :1401,'foeERR' :1402,
            }
        self.sdoVar={        #***** sdo[]位址對照表
            'sdoBLK' :0,  'sdo1000':10, 'sdo6502':29, 'sdo1018':30, 'vendor' :31, 'product':32, 'version':33,  'series':34,
            'dasBLK' :200,'dasN'   :200,'dasCMD' :201,'dasMS'  :202,'dasDT'  :203,'dasMAX' :204,'dasSIZ' :205,
            'dasBLKe':210,'dasCH'  :210,'dasV1'  :211,'dasV2'  :212,'dasV3'  :213,'dasV4'  :214,'dasV5'  :215,'dasV6'  :216,'dasV7'  :217,'dasV8'  :218,'dasV9'  :219,
            'pdoBLK' :220,'pdoCMD' :220,'pdoSTS' :221,'pdoPOS' :222,'pdoVEL' :223,'pdoTRQ' :224,'pdoMXC' :225,'pdoANG' :226,'pdoSPD' :227,'pdoAMP' :228,'pdoOUT' :229,
            'cmdBLK' :240,'cmdCMD' :240,'cmdPOS' :241,'cmdVEL' :242,'cmdACC' :243,'cmdTRQ' :244,'cmdMXC' :245,'cmdSIM' :246,                            'cmdON'  :249,
            'segBLK' :260,'segCMD' :260,'segPOS' :261,'segVEL' :262,'segMAX' :263,'segACC' :264,'segDEC' :265,'segSTS' :266,
            'segBLKe':270,'segALM' :270,'segERR' :271,'segMXC' :272,'segMS'  :273,
            'extBLK' :280,'extTRQ' :280,'extOUT' :281,'extTG'  :282,'extTI'  :283,'extTF'  :284,'extMXC' :285,'extMXG' :286,'extMXM' :287,'extMAX' :288,'extPPR' :289,
            'extBLKe':290,'extKG'  :290,'extKA'  :291,'extKV'  :292,'extKV0' :293,'extKS'  :294,'extKS0' :295,'extDT'  :296,'extMS'  :297,
            'posBLK' :300,'posCMD' :300,'posERR' :301,'posSUM' :302,'posOUT' :303,'posMXE' :304,'posMXI' :305,'posMXO' :306,'posKP'  :307,'posKI'  :308,'posDIV' :309,
            'spdBLK' :320,'spdCMD' :320,'spdERR' :321,'spdSUM' :322,'spdOUT' :323,'spdMXE' :324,'spdMXI' :325,'spdMXO' :326,'spdKP'  :327,'spdKI'  :328,'spdFLT' :329,
            'ampBLK' :340,'ampCMD' :340,'ampSD'  :341,'ampSQ'  :342,'ampLMT' :343,'ampMXE' :344,'ampMXI' :345,'ampMXO' :346,'ampKP'  :347,'ampKI'  :348,'ampFLT' :349,
            'esmBLK' :380,'esmEVT' :380,'esmREQ' :381,'esmSTS' :382,'esmERR' :383,'esmSDO' :384,'esmFOE' :385,'esmCOE' :386,'esmRXP' :387,'esmTXP' :388,'esmDOG' :389,
            'esmBLKe':390,'rxSDO0' :390,'rxSDON' :391,'txSDO0' :392,'txSDON' :393,'rxPDO0' :394,'rxPDON' :395,'txPDO0' :396,'txPDON' :397,
            'iopBLK' :400,'iopANG' :400,'iopSPD' :401,'iopID'  :402,'iopIQ'  :403,'iopVD'  :404,'iopVQ'  :405,'iopPWR' :406,'iopTMP' :407,'iopI2T' :408,'iopALM' :409,
            'iopBLKe':410,'iopREL' :410,'iopIDX' :411,'iopABS' :412,'iopMOD' :413,'iopPWM' :414,'iopRST' :415,
            'pwmBLK' :420,'pwmU'   :420,'pwmV'   :421,'pwmW'   :422,'pwmDEG' :423,'pwmCMD' :424,'pwmMS'  :425,'pwmANG' :426,'pwmENB' :427,'pwmBRK' :428,
            'pwmBLKe':430,'pwmMAX' :430,'pwmINV' :431,'pwmRST' :432,'pwmFLT' :433,
            'uvwBLK' :440,'uvwDEG' :440,'uvwSIN' :441,'uvwCOS' :442,'uvwRDY' :443,'uvwKI'  :444,'uvwKO'  :445,'uvwDEG0':446,
            'adcBLK' :460,'adcU'   :460,'adcV'   :461,'adcW'   :462,'adcP'   :463,'adcT'   :464,                                          'adcK'   :468,'adcSTD' :469,
            'adcBLKe':470,'adcIU'  :470,'adcIV'  :471,'adcIW'  :472,'adcSUM' :473,'adcDLY' :474,'adcFLT' :475,
            'angBLK' :480,'angABS0':480,'angIDX0':481,'angREL0':482,'angABS' :483,'angREL' :484,'angPOLE':485,'angGEAR':486,'angINV' :487,'angKN'  :488,'angKD'  :489,
            'abzBLK' :500,'abzENB' :500,'abzFLT' :501,'abzINV' :502,'abzOUT' :503,              'abzINP' :505,
            'halBLK' :520,'halENB' :520,'halINP' :521,'halSEQ' :522,'halANG' :523,'halSPD' :524,'halPRD' :525,'halP'   :526,'halN'   :527,'halCAP' :528,'halRST' :529,
            'bisBLK' :540,'bisENB' :540,'bisBITS':541,'bisMASK':542,'bisMULT':543,'bisBUF0':544,'bisBUF' :545,'bisACK' :546,'bisCRC' :547,'bisERR' :548,
            'dbgBLK' :990,'coeERR' :990,'pdiLOK' :991,'pdiERR' :992,'ldpERR' :993,'foeERR' :994,        
            'clkBLK':1000,'sysCLK':1000,'sys20K':1001,'sysLOP':1002,'sysKHZ':1003,'sysON' :1004,'sysOFF' :1005,                                        'powerON':1009,
            'ledBLK':1010,'ledR'  :1010,'ledO'  :1011,'ledY'  :1012,'ledG'  :1013,'ledMS' :1014,'ledBITS':1015,
            'sysBLK':1020,'sysVERS':1020,'sysDATE':1021,'romVERS':1022,'romDATE':1023,
            }                #***** 預設系統參數及檔案

    def http(self,cmd):      #***** 送出cmd並取得echo
        conn=httplib.HTTPConnection(self.ip,8080)
        conn.request("GET", "/ipCommandPLC.html?"+urllib.parse.urlencode({'cmd':cmd}))
        resp=conn.getresponse()
        echo=str(resp.read(),"utf-8")
        conn.close()
        return(echo)

    def say(self,s):         #***** 文字轉語音輸出
        self._speak.Speak(s)
    def setAxis(self,d):     #***** 設置軸號
        self._axis=d
    def getAxis(self,s):     #***** 置換軸號
        s=s.replace("@",str(self._axis))
        return(s)

    def putS(self,cmd='',n=0):
        if len(cmd)<=0: self._scmd=""; return None
        cmd=self.getEqu(cmd)
        if n<=0: s='put("'+cmd+'");'
        else:    s='put("'+cmd+'",'+str(n)+');'
        self._scmd+=s

    def getS(self,cmd='',n=0):
        if len(cmd)<=0:
            s=self._scmd+'\r'; self._scmd=""
            n=self.com.write(s.encode())
            for i in range(1000):
                time.sleep(0.001)
                if self.com.in_waiting>0: break
            s=self.com.read(self.com.in_waiting).decode()
            ss=s.strip().split('\r\n'); n=len(ss)
            if n>2: return(ss[n-2])
            return("")
        cmd=self.getEqu(cmd)
        if n<=0: s='get("'+cmd+'");'
        else:    s='get("'+cmd+'",'+str(n)+');'
        self._scmd+=s

    def plcCommand(self,cmd):
        if not self.ip is None:
            s=self.http(cmd)
            return(s)
        if not self.com is None:
            # Added for diagnostic
            if self.CommColiChk != 0:
                self.CommColiErr += 1
            self.CommColiChk += 1
            with self._lockComm:
                s=self.com.read(self.com.in_waiting)
                n=self.com.write(cmd.encode())
                for i in range(1000):
                    time.sleep(0.001)
                    if self.com.in_waiting>0:
                        break
                if i >= 999:
                    self.CommTimeOut+=1
                s=self.com.read(self.com.in_waiting).decode()
            self.CommColiChk -= 1
            return(s)
        print(s); return("")

    def put(self,cmd,n=0):   #***** 送出put指令
        cmd=self.getEqu(cmd)
        if n<=0: s='put("'+cmd+'")\r'
        else:    s='put("'+cmd+'",'+str(n)+')\r'
        s=self.plcCommand(s)
        ss=s.strip().split('\r\n'); n=len(ss)
        if n>2: return(ss[n-2])
        return("")

    def get(self,cmd,n=0):   #***** 送出get指令並取得echo
        cmd=self.getEqu(cmd)
        if n<=0: s='get("'+cmd+'")\r'
        else:    s='get("'+cmd+'",'+str(n)+')\r'
        s=self.plcCommand(s);  #print("s=",s)
        ss=s.strip().split('\r\n'); n=len(ss)
        if n>2: return(ss[n-2])
        return("")

    def dasStart(self,ms):   #***** 設置ms並啟動DAS
        s=self.put("dasN=0,1,"+str(ms))
    def dasStop(self):       #***** 關閉DAS並取得記錄個數
        s=self.put("dasCMD=0")
        s=self.get("dasN").strip()
        return(int(s))
    def dasGet(self,ch,n):   #***** 取得DAS頻道#n
        ss=""; num=50#BUG_FIX: fixed das data lose issue
        for i in range(0,n,num):
            s=self.get("m0.das."+str(i)+"."+str(ch)+".L",num)
            ss=ss+s
        d=np.fromstring(ss,dtype=int,sep=' ')
        if len(d)>n: d=d[0:n]
        return(d)

    def toArray(self,s):      #***** 將字串轉換成數列
        s=s[1:len(s)-1]
        d=np.fromstring(s,dtype=int,sep=' ')
        return(d)

    def getAddr(self,s):     #***** 取得變數位址(字串)
        ss=s.strip().split('.');  n=len(ss)
        if n==0 or n>3:           return(s)
        if n==1:             #**var
            d=self.mapVar.get(ss[0].strip())
            if not d:             return(s)
            chn=0
        if n==2:             #**m1.var
            if not len(ss[0])==2: return(s)
            if not ss[0][0]=='m': return(s)
            d=self.mapVar.get(ss[1].strip())
            if d is None:         return(s)
            chn=int(ss[0][1])
        if n==3:             #**m1.map.var
            if not len(ss[0])==2: return(s)
            if not ss[0][0]=='m': return(s)
            if not ss[1]=='map' : return(s)
            d=self.mapVar.get(ss[2].strip())
            if d is None:         return(s)
            chn=int(ss[0][1])
        if chn>0 and chn<8:
            if d>=10  and d<20  : d=d+(chn-1)*10
            if d==91            : d=d+(chn-1)
            if d>=100 and d<200 : d=d+(chn-1)*100
        s=str(d);                 return(s)

    def getMap(self,s):      #***** 取得變數定義
        ss=s.strip().split('.');     n=len(ss)
        if n==0 or n>3:           return(s)
        if n==1:             #**var
            d=self.mapVar.get(ss[0].strip())
            if not d:             return(s)
            ss[0]="m0"
        if n==2:             #**m1.var
            if not len(ss[0])==2: return(s)
            if not ss[0][0]=='m': return(s)
            d=self.mapVar.get(ss[1].strip())
            if d is None:         return(s)
        if n==3:             #**m1.map.var
            if not len(ss[0])==2: return(s)
            if not ss[0][0]=='m': return(s)
            if   ss[1]=='map' :
                d=self.mapVar.get(ss[2].strip())
                if d is None:     return(s)
            elif ss[1]=='sdo':
                d=self.sdoVar.get(ss[2].strip())
                if d is None:     return(s)
                s=ss[0]+'.sdo.'+str(d)+'.L'; return(s)
            else:                 return(s)
        s=ss[0]+'.map.'+str(d)+'.L';         return(s)

    def getEqu(self,s):
        if not s or len(s)<=0: return("")
        s=self.getAxis(s)    #**置換軸號
        ss=s.split('=')
        s =self.getMap(ss[0])
        if len(ss)<2:          return(s)
        ss=ss[1].split(',');   n=len(ss)
        for i in range(n):
            if i>0: s=s+','
            else:   s=s+'='
            s=s+self.getAddr(ss[i])
        return(s)

    def getR(self,v,n=0):    #***** 取得變數值
        s=self.get(v,n); d=np.fromstring(s,dtype=int,sep=' ')
        if len(d)==1:    d=int(d[0])
        return(d)

    def putR(self,v,d):      #***** 設置變數值
        if isinstance(d,int):
            cmd=v+"="+str(d); self.put(cmd)
        if isinstance(d,list):
            n=len(d)
            if (n<1): return None
            cmd=v+"="+str(d[0])
            for i in range(1,n):
                cmd=cmd+","+str(d[i])
            self.put(cmd)

#**********************************************************
# SDO指令部分:
#    d   =esc.mapSDO("var")      : 取得SDO位址
#   [d..]=esc.getSDO("var",n)    : 讀取SDO變數
#         esc.putSDO("var",[d..]): 設置SDO變數
#
    def chnSDO(self,s):      #***** 取得SDO頻道
        ss=s.strip().split('.');  n=len(ss)
        if n<2 or n>2:        return("m@")
        if not len(ss[0])==2: return("m@")
        if not ss[0][0]=='m': return("m@")
        return(ss[0])

    def mapSDO(self,s):      #***** 取得SDO位址
        ss=s.strip().split('.');  n=len(ss)
        if n==0 or n>2:           return(0)
        if n==1:             #**var
            d=self.sdoVar.get(ss[0].strip())
            if not d:             return(0)
        if n==2:             #**m1.var
            if not len(ss[0])==2: return(0)
            if not ss[0][0]=='m': return(0)
            d=self.sdoVar.get(ss[1].strip())
            if d is None:         return(0)
        return(d)

    def getSDO(self,v,n=0):  #***** 取得SDO變數
        addr=self.mapSDO(v);
        if addr<=0: return(0)
        if n<1: n=1
        d=[0]*n
        for i in range(n):
            s=self.chnSDO(v)+".sdo."+str(addr+i)+".L"
            s=self.get(s); time.sleep(0.01)
            d[i]=int(s)
        if n>1: return(d)
        return(d[0])

    def putSDO(self,v,d):    #***** 設置SDO變數
        if isinstance(d,int):
            n=1; d=[d]
        if isinstance(d,list):
            n=len(d)
            if (n<1): return None
        addr=self.mapSDO(v)
        if addr<=0:   return None
        for i in range(n):
            s=self.chnSDO(v)+".sdo."+str(addr+i)+".L="+str(d[i])
            self.put(s); time.sleep(0.01)

#**********************************************************
# FoE指令部分:
#   esc.foeWrite("fname","m0") : 寫入檔案至指定驅動器
#   esc.foeRead ("fname")      : 讀取檔案
#
# #0: Signature [4B]: 固定=“ASIX”,不得變更.
# #4: FileType  [2B]: 0=程式檔,1=參數檔
# #6: Compress  [2B]:
# #8: FileAddr  [4B]: 固定=32
# #12:FileLeng  [4B]: 單位=byte       (包括32B標頭)
# #16:Reserved  [2B]:
# #18:Flags     [2B]: 0=已確認通過(不用再檢查)
# #20:Checksum32[4B]: 檢查碼(檢查範圍不包括32B標頭)
# #24:Reserved  [8B]:
#
    def putB(self,addr,d):   #**put(Byte)
        self._header[addr&0x1f]=d
    def putW(self,addr,d):   #**put(Word)
        self.putB(addr,   d    &0xff)
        self.putB(addr+1,(d>>8)&0xff)
    def putL(self,addr,d):   #**put(Long)
        self.putW(addr,   d     &0xffff)
        self.putW(addr+2,(d>>16)&0xffff)
    def putHL(self,addr,d):  #**put(H-M-M-L)
        self.putB(addr,  (d>>24)&0xff)
        self.putB(addr+1,(d>>16)&0xff)
        self.putB(addr+2,(d>>8) &0xff)
        self.putB(addr+3, d     &0xff)
                             #***** 計算checksum
    def checksum32(self,sum,d):
        length=len(d)
        for i in range(0,length,4):
            dat = (int(d[i])       &0x000000ff)
            dat|=((int(d[i+1])<<8) &0x0000ff00)
            dat|=((int(d[i+2])<<16)&0x00ff0000)
            dat|=((int(d[i+3])<<24)&0xff000000)
            sum=(sum+dat)&0xffffffff
            if sum<dat: sum=(sum+1)&0xffffffff
        return(sum)
                             #***** 送出put/get指令
    def foeSegment(self,idx,cmd):
        if idx<0: print("cmd=",cmd)
        s=self.com.read(self.com.in_waiting)
        n=self.com.write(cmd.encode())
        for i in range(1000):
            time.sleep(0.001)
            if self.com.in_waiting>0:
                break
        if i >= 999:
            self.FoeTimeOut+=1
            print(cmd.encode())
        s=self.com.read(self.com.in_waiting).decode()
        if idx<0: print("echo=",s)
        ss=s.strip().split('\r\n'); n=len(ss)
        if n>2: s=ss[n-2]
        else:   s=""
        ss=s.strip().split(' '); n=len(ss)
        if n<=1 and len(ss[0])<=0: d=bytearray(0)
        else:
            d=bytearray(n)
            for i in range(n): d[i]=int(ss[i])
        if idx==0: return(d)
        addr=(idx*116)&0x0fff                    #**搭配FlashROM的燒錄時間
        if cmd.find("m0.")<0: tErase=0.5;  tProg=0.03
        else:                 tErase=0.16; tProg=0.012
        if addr>0 and addr<=116: time.sleep(tErase); print("segment #"+str(idx))
        else:                    time.sleep(tProg);

        return(d)
                             #***** 產生put("m0.foe..")字串
    def foePutCmd(self,chn,idx,n,buf,k):
        s='put("'+chn+'.foe.'+str(idx)+'.B='
        for i in range(n):
            if i<(n-1): s=s+str(int(buf[i+k])&0xff)+','
            else:       s=s+str(int(buf[i+k])&0xff)+'")\r'
        return(s)
                             #***** 產生get("m0.foe..")字串
    def foeGetCmd(self,idx,sub=0):
        if idx>0: s='get("m0.foe.'  +str(idx)+'.B")\r'
        else:     s='get("m0.foe.0.'+str(sub)+'.B")\r'
        return(s)
                             #***** foeWrite()指令
    def foeWrite(self,fname,chn="m0", SetUpgradingProgress=None):
        if not fname or len(fname)<=0: return
        if not chn   or len(chn)!=2:   return
        if chn[0]!='m':                return
        if chn[1]<'0' or chn[1]>'9':   return
        f=open(fname,"rb"); dat=f.read(); f.close()
        n=(len(dat)+32)&0xfff; k=n&3;
        if   n>0 and n<256:    k=256-n; #**防止erase後立刻prog
        elif k>0:              k=4-k;   #**維持4B格式
        if k>0: dat+=bytes(k)           #**充填0
        for i in range(32):          self.putB (i,0)
        self._header[0:4]="ASIX".encode();
        if fname.find(".bin")<0:     self.putW (4,1)
        offset=32;                   self.putHL(8, offset)
        chksum=0;   length=len(dat); self.putHL(12,length+32)
        chksum=self.checksum32(chksum,dat)
        chksum=(~chksum)&0xffffffff; self.putL (20,chksum)
        print("fname=" +fname+", servo="+chn)
        print("length="+hex(length)+", chksum="+hex(chksum),hex((~chksum)&0xffffffff))
                             #**segment=0: filename
        s=fname;         ss=s.split('/')
        s=ss[len(ss)-1]; ss=s.split('\\')
        s=ss[len(ss)-1]; ss=s.split('.')
        s=ss[0];         n=len(s)
        self._buffer[0:n]=s.encode()
        s=self.foePutCmd(chn,0,n,self._buffer,0);
        self.foeSegment(0,s)
        if SetUpgradingProgress != None:
            SetUpgradingProgress(10)
                             #**segment=1: header+dat[]
        for i in range(32):     self._buffer[i]   =self._header[i]
        for i in range(116-32): self._buffer[i+32]=dat[i]
        s=self.foePutCmd(chn,1,116,self._buffer,0);   k=1
        self.foeSegment(1,s)
        if SetUpgradingProgress != None:
            SetUpgradingProgress(20)
                             #**segment>1: dat[]-only
        for i in range(116-32,length,116):
            if (k%20)==0: print("segment #"+str(k))
            n=length-i; k+=1
            if n>116: n=116
            s=self.foePutCmd(chn,k,n,dat,i)
            self.foeSegment(k,s)
            if SetUpgradingProgress != None:
                SetUpgradingProgress(20+(80*i/length))

        if SetUpgradingProgress != None:
            SetUpgradingProgress(100)

    def foeRead(self,fname): #***** foeRead()指令
        if not fname or len(fname)<=0: return
        if fname.find(".bin")<0: sub=1
        else:                    sub=0
        s=self.foeGetCmd(0,sub); d=self.foeSegment(0,s)
        print(s)
        s=self.foeGetCmd(1);     d=self.foeSegment(0,s)
        print(s)
        length=(int(d[12])<<24)|(int(d[13])<<16)|(int(d[14])<<8)|int(d[15]);
        length=(length&0xffffffff)-32;
        chksum=(int(d[23])<<24)|(int(d[22])<<16)|(int(d[21])<<8)|int(d[20]);
        chksum=(~chksum)&0xffffffff;
        print("fname=" +fname)
        print("length="+hex(length)+",chksum="+hex(chksum))
        if sub<1 and length>0x5FFE0: return
        if sub>0 and length>0x0FFE0: return
        f=open(fname,'w+b');         sum=0;
        if sub==0:       f.write(d[:32])         #**32B標頭
        k=2; d=d[32:];   f.write(d); sum=self.checksum32(sum,d)
        for i in range(116-32,length,116):
            if (k%100)==0: print("segment #"+str(k))
            s=self.foeGetCmd(k); k+=1; d=self.foeSegment(0,s)
            if len(d)>0: f.write(d); sum=self.checksum32(sum,d)
            else:        break
        f.close();
        if sum==chksum: print("checksum OK!")
        else:           print("checksum NG!")

#**********************************************************
# 機械手3D模擬器
#
    def pipeOpen(self):           #***** 開啟pipe連線 *****
        if     self._pipe: return None
        self._pipe=open('\\\\.\\pipe\\robotpipe','a+b')
    def pipeClose(self):          #***** 關閉pipe連線 *****
        if not self._pipe: return None
        self._pipe.close()
        self._pipe=None
    def pipe(self,cmd):     #***** 下達指令並接收回覆 *****
        if not self._pipe: return None
        with self._lockPipe:           #**PIPE指令
            self._pipe.write(bytes(cmd,encoding="utf8"))
            self._pipe.flush()
            for i in range(100):
                time.sleep(0.1); n=self._pipe.seek(0,2)
                if n>0: break
            if n<=0: return("")
            time.sleep(0.1);     n=self._pipe.seek(0,2)
            echo=str(self._pipe.read(n),encoding="utf-8")
            self._pipe.seek(0,0)
        return(echo.strip())
    def pipeMov(self,p=None):   #***** 機械手角度設置 *****
        if not p:         return None
        if isinstance(p,str):          #**p=字串
            ss=p.strip().split(" ")
            if len(ss)<=1: ss=p.strip().split(",")
            n=len(ss)
            for i in range(n):
                s=ss[i].strip()
                p=self.pGet(s,"joint");
                if len(p[0])>0:  p[0]=""; s=self.pipe(".move "+self.sDot(p))
                time.sleep(0.5)
            return None
        if isinstance(p,list):         #**p=數列
            p=self.pDot(p)
            p=mm.pTo(p,"joint"); p[0]=""
            s=self.pipe(".move "+self.sDot(p))
    def sDot(self,p):              #**** 取得p[8]字串 *****
        p=self.pDot(p)
        s='{} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}'.format(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7])
        return(s)
    def pDot(self,p):                 #***** 充填p[8] *****
        n=len(p)
        for i in range(n,8): p.append(0.)
        return(p)          #**** 設置標誌點(或軌跡線) *****
    def pipeDot(self,p=None):
        if not p:                      #**清除dots[]
            s=self.pipe(".dot"); return None
        if isinstance(p,str):          #**設置dots[]
            ss=p.strip().split(" ")
            if len(ss)<=1: ss=p.strip().split(",")
            n=len(ss)
            for i in range(n):
                s=ss[i].strip()
                p=pGet(s,"base")
                if len(p[0])>0: s=self.pipe(".dot "+self.sDot(p))
            return None
        if isinstance(p,list):   #**設置dots[]
            p=mm.pTo(self.pDot(p),"base")
            s=self.pipe(".dot "+self.sDot(p))
    def pipeShow(self,s,d):       #***** 部件顯示設置 *****
        s='.show {} {}'.format(d,s)
        s=self.pipe(s)
    def pipeGrab(self,s,d):       #***** 夾爪控制設置 *****
        s='.grab {} {}'.format(d,s)
        s=self.pipe(s)
    def pipeList(self):           #***** 列出所有單點 *****
        s='.point list'
        s=self.pipe(s);         print(s)
    def pipeSet(self,s,p):             #***** 設置單點 *****
        p=self.pDot(p)
        s='.point set {} {} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}'.format(s,p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7])
        s=self.pipe(s)
                        #***** 取得單點(包括座標轉換) *****
    def pipeS(self,s,n=0):
        ss=s.strip().split(';')
        for s in ss:
            d=s.strip().split(' ')
            if len(d)>=n: return(s)
        return("")
    def pipeGet(self,s="",z=""):
        if len(s)<=0: self.pipeList(); return None
        s='.point get {} {}'.format(s,z)
        s=self.pipe(s.strip())
        if not s: return None
        ss=s.strip().split(' '); n=len(ss)
        if n<8:   return None
        p=[ss[0],0.,0.,0.,0.,0.,0.,0.]
        for i in range(1,8): p[i]=float(ss[i])*0.001
        return(p)
    def pipeText(self,k=0,s=""):  #***** 設置文字視窗 *****
        ss='.text '+str(k)+" "+s;
        s=self.pipe(ss)

#**********************************************************
# 矩陣運算測試
#
    def putM(self,cmd,p):
        s="m0.mat."+str(cmd)+".L"
        n=len(p)
        if n<1:  return None
        for i in range(n):
            if i>0: s=s+","+str(int(p[i]*1000.))
            else:   s=s+"="+str(int(p[i]*1000.))
        self.put(s)

    def getM(self,cmd,p=None):
        s="m0.mat."+str(cmd)+".L"
        if p: n=len(p)
        else: n=0
        for i in range(n):
            if i>0: s=s+","+str(int(p[i]*1000.))
            else:   s=s+"="+str(int(p[i]*1000.))
        s=self.get(s); d=np.fromstring(s,dtype=int,sep=' ')
        if len(d)<8:   d.resize(1,8); d=d.flatten()
        return(d)

    def modelURDF(self,mx,axis=7):               #**設置urdf[]
        mm.modelURDF=mx
        mm.nAxis=axis;        self.putR("nAxis",axis)
        for i in range(axis): self.putM(11+i,mx[i])
    def modelArm7(self,arm7=0,arm6=0):           #**設置七軸的手肘模式
        AxRobotData.log.debug("Setup joint3 angle limitation=%ddeg for Arm7, %ddeg for Arm6", arm7, arm6)
        mm.putArm7(arm7); mm.putArm6(arm6);      #**以及六軸的手腕模式
    def modelLimit(self,p): self.putM(36,p)      #**設置limit[]
    def modelGainG(self,p): self.putM(37,p)      #**設置gainG[]
    def modelGainM(self,p): self.putM(38,p)      #**設置gainM[]
    def modelBiasM(self,p): self.putM(39,p)      #**設置biasM[]
                           
    def modelMotor(self,p): #***** 設置馬達的工作範圍 *****
        return None
                          #***** 設置tool[]的質心位置 *****
    def modelToolM(self,p=None):
        d=[0.]*12;     n=len(p)
        for i in range(n): d[i+6]=p[i]
        p=self.pGet("tool","robot")
        for i in range(6): d[i]=p[i+1]
        """
        self.putM(11+mm.nAxis,d)
        p=self.pGet("base","world")
        d=[0.]*12;
        for i in range(6): d[i]=p[i+1]
        self.putM(10,d)
        """
        self.putM(18,d)      #**設置tool[]
        d=[0.]*12; p=self.pGet("base","world")
        for i in range(6): d[i]=p[i+1]
        self.putM(10,d)      #**設置base[]
        d=[0.]*12; p=self.pGet("work","world")
        for i in range(6): d[i]=p[i+1]
        self.putM(19,d)      #**設置work[]

#**********************************************************
# 機械手座標換算
#
    def mmReset(self):          #***** 機械手座標預設 *****
        mm.pClear();
        mm.pSet("base",["world",  0.,0., 0.,0.,0.,0.,0.])
        # mm.pSet("tabA",["world",400.,0.,500.,0.,0.,0.,0.])
        # mm.pSet("tabB",["world",400.,0.,500.,0.,0.,0.,0.])
        # mm.pSet("tabC",["world",400.,0.,500.,0.,0.,0.,0.])
        mm.pSet("work",["base" ,  0.,0.,  0.,0.,0.,0.,0.])
        # mm.pSet("camF",["robot",  0.,0.,  0.,0.,0.,0.,0.])
        # mm.pSet("camR",["robot",  0.,0.,  0.,0.,0.,0.,0.])
#        mm.pSet("grp0",["robot", 35.,0., 80.,0.,0.,0.,0.])
        # mm.pSet("grp0",["robot",  0.,0.,  0.,0.,0.,0.,0.])
        # mm.pSet("grp1",["robot",  0.,0.,  0.,0.,0.,0.,0.])
        # mm.pSet("grp2",["robot",  0.,0.,  0.,0.,0.,0.,0.])
        mm.pSet("tool",["robot",   0.,0.,  0.,0.,0.,0.,0.])
        # mm.pSet("objA",["work", 100., 150.,20.,0.,0.,0.,0.])
        # mm.pSet("objB",["work",-100.,-150.,20.,0.,0.,0.,0.])
        # mm.pSet("objC",["work",-100., 150.,20.,0.,0.,0.,0.])
        # mm.pSet("objD",["work", 100.,-150.,20.,0.,0.,0.,0.])
        # mm.pSet("objE",["work",   0.,   0.,20.,0.,0.,0.,0.])

    def moveTo(self,s,spd=0,acc=0):
        ss=s.strip().split(','); n=len(ss)
        if n<=1 and len(ss[0])<=0:     return None
        if n==1:
            ss=s.strip().split(' '); n=len(ss)
        for i in range(n):
            if not ss[i] in mm.points: return None
        for i in range(n):
            p=mm.pGet(ss[i],"joint")
#            print("I="+str(i+1),p)
            self.segD(i+1,p)
        self.seg0(n,spd,acc)
                                  #***** 列出所有單點 *****
    def pList(self):       return(mm.pList())
    def pClear(self, s=""):      mm.pClear(s)  #***** 清除單點 *****
                                      #***** 設置單點 *****
    def pSet(self,s,p):
        with self._lockPtAcc:
            mm.pSet(s,p)
                        #***** 取得單點(包括座標轉換) *****
    def pGet(self,s,z=""):
        with self._lockPtAcc:
            tmp = mm.pGet(s,z)
        for i in range(1,len(tmp)):
            tmp[i] = round(tmp[i],3)
        return(tmp)
    def pXYZ(self,p,x,y,z):        #***** 置換(x,y,z) *****
        p[1]=x; p[2]=y; p[3]=z
    def pX(self,p,x):   p[1]=x
    def pY(self,p,y):   p[2]=y
    def pZ(self,p,z):   p[3]=z
                    #***** 由夾爪角度來設置(Rx,Ry,Rz) *****
    def pTool(self,p,degT,degH=0.,degV=0.,devS=0.,axis='z'):
        return(mm.pTool(p,degT,degH,degV,devS,axis));

                          #***** 設置運動表格(軌跡線) *****
    def pMove(self,p=None): return(mm.pTrack(p))
                       #***** 移至指定目標,並等待結束 *****
    def pMoveTo(self,p,spd=100,acc=1000,timeout=100.):
        if p: mm.pTrack(-1); mm.pTrack(p)
        n=mm.pTrack(); segs=22;
        if n<=0: return None
        for i in range(0,n,segs): self.segN(i+1,segs);
        self.seg0(n,spd,acc); self.wait() #Aways waiting til ratio reach to 100%.
                                      #***** 直線移動 *****
    def pMoveLn(self,p,spd=100,acc=1000,timeout=100.):
        p =self.pTo(p,"work");                    self.update();
        p0=self.pTo(self._track,"work"); d=[0]*8; self.pMove(-1);
        for k in range(1,7): d[k]=p[k]-p0[k]
        dst=math.sqrt(d[1]*d[1]+d[2]*d[2]+d[3]*d[3])
        deg=math.sqrt(d[4]*d[4]+d[5]*d[5]+d[6]*d[6])
        n1=int(dst/5+1); n2=int(deg/5+1); n=max(n1,n2,2);
        for i in range(1,n+1):
            for k in range(1,7): p[k]=p0[k]+d[k]*i/n;
            self.pMove(p);
        self.pMoveTo(None,spd,acc,timeout)
                        #***** 座標轉換(至關節座標系) *****
    def pTo(self,p,z="joint"):
        with self._lockPtAcc:
            tmp = mm.pTo(p,z)
        return tmp
    def GetPointDataBase(self): return(mm.points)
    def SetPointDataBase(self, dctPoints): mm.points.clear(); mm.points=dctPoints
    def pExist(self, s=""): return(mm.pExist(s))
#**********************************************************
# 運動控制部分
#
                             #***** 更新機械手狀態
    def update(self,force=False):      #false=TRUE:強制更新
        if not force:                  #每隔100ms更新機械手狀態
            if (time.time()-self.t0)<0.1: return None
        self.t0=time.time()            #設置更新時間
        s=self.get("m0.seg.0xffff.L")
        ss=s.strip().split(' '); n=len(ss)
        if n<=1 and len(ss[0])<=0: return None
        if n>100: n=100
        #self.pipeText(9,s)             #**更新3D模擬器(map[100])
        for i in range(n): self._map[i]=int(ss[i])
        self._ratio=self._map[0]       #**ratio
        self._table=self._map[8]       #**segN
        self._count=self._map[2]       #**segK
        self._status=self._map[4]      #**segSTS 
        for i in range(1,8):
            self._joint[i]=self._map[10*i+5]/1000.    #**cmdANG[]
            self._track[i]=self._map[10*i+0]/1000.    #**cmdPOS[]
            d= self._map[10*i+1]; self._vel[i]=d;
            d= self._map[10*i+2]; self._acc[i]=d;
            d= self._map[10*i+3]; self._trq[i]=d;
            d= self._map[10*i+4]; self._mxC[i]=d;
            d= self._map[10*i+6]; self._spd[i]=d;
            d= self._map[10*i+7]; self._amp[i]=d;
            d= self._map[10*i+8]; self._out[i]=d;
            d= self._map[90+i]     &0xffff;
            if d>=0x8000: d-=0x10000;
            self._mxM[i]=d;
            d=(self._map[90+i]>>16)&0xffff;
            if d>=0x8000: d-=0x10000;
            self._mxG[i]=d;

    def ratio(self):         #***** 取得單節執行率
        self.update(); return(self._ratio)
                             #***** 等待執行結束
    def wait(self,timeout=0.,ratio=100):
#        if timeout<=0.: return None
        t0=time.time(); time.sleep(0.2)
        while True:
            if timeout>0:
                if (time.time()-t0)<timeout: break
            d=self.ratio(); dt=time.time()-t0
            if dt<1.0: continue
            if d>=ratio:  break
    def segD(self,idx,p):    #***** 設置單個seg[]表格
        s="m0.seg."+str(idx)+".L=0"
        for i in range(1,8): s=s+","+str(int(p[i]*1000.))
        self.put(s)
    def segN(self,idx,segs): #***** 設置連續seg[]表格
        s="m0.seg."+str(idx)+".L=0";
        n=mm.pTrack()-idx+1;
        if n>segs: n=segs;
        for j in range(n):
            if j>0: s=s+",0";
            p=mm.pTrack(idx+j-1);
            for i in range(1,8): s=s+","+str(int(p[i]*1000.))
        self.put(s);
                             #***** cmd=0:單節啟動
    def seg0(self,num,spd=0,acc=0):
        s="m0.seg.0xffff.0.L=0,{},{},{}".format(num,spd,acc)
        s=self.put(s);
        if s.strip()!=str(num):
            self.SegLostErr += 1
            print("*****error: segment lost")
            print(s)
    def seg1(self,spd,p):    #***** cmd=1:手動控制(相對座標)
        s="m0.seg.0xffff.1.L="+str(spd)
        for i in range(1,8): s=s+","+str(int(p[i]*1000.))
        self.put(s)
    def seg2(self,spd,p):    #***** cmd=2:手動控制(絕對座標)
        s="m0.seg.0xffff.2.L="+str(spd)
        for i in range(1,8): s=s+","+str(int(p[i]*1000.))
        self.put(s)
    def segDEC(self,dec):    #***** cmd=8:設置減速或取消
        s="m0.seg.0xffff.8.L="+str(dec)
        self.put(s)
    def segBRK(self):        #***** cmd=9:設置剎車並結束表格
        s="m0.seg.0xffff.9.L"
        self.put(s)
    def segCMD(self,cmd,p):  #***** cmd>9:其他設置指令
        s="m0.seg.0xffff."+str(cmd)+".L=0"
        for i in range(1,8): s=s+","+str(int(p[i]*1000.))
        self.put(s)
    def segANG(self,p): self.segCMD(5,p) #**cmd=5:設置simANG[]
    def segPOS(self,p): self.segCMD(6,p) #**cmd=6:設置cmdPOS[]
    def drvPOS(self,p): self.segCMD(7,p) #**cmd=7:設置drvPOS[]
    def segR(self,s,p=None): #***** 一次讀寫多軸變數
        d=self.mapVar.get(s.strip())
        if not d :          return None
        if d<10 or d>=200 : return None
        if not p:                           #**讀取多軸變數
            s="m0.seg.0xffff."+str(d)+".L"
            return(self.getR(s))
        s="m0.seg.0xffff."+str(d)+".L=0"    #**設置多軸變數
        for i in range(1,8): s=s+","+str(int(p[i]))
        self.put(s)

#**********************************************************
# Thread處理: 定時更新機械手狀態
#
    def doUpdate(self):
        self.update()

    # def doThread(self):
    #     self._running=1; self._update=1
    #     while True:
    #         if  self._running==0: break
    #         time.sleep(0.2)
    #         if  self._update>0: self.update()
    # def threadON(self):
    #     if self._running>0: return None
    #     threading.Thread(daemon=True,target=self.doThread).start()
    # def threadOFF(self): self._running=0
    # def updateON (self): self._update =1
    # def updateOFF(self): self._update =0
