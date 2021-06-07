# -*- coding: UTF-8 -*-
# 必須在檔案開始時增加上述標頭,才能使用中文註釋

import win32file,win32pipe,threading
import sys,math,time,copy,random
from   OCC.gp import *       #**向量計算
import simu.mathRobot as mm       #**座標計算

nRandom=0;        nMode7=0;         nReal=0;
nArm1=1; nArm2=1; nArm3=1; nArm4=1; nArm5=1; nArm6=1; nArm7=1
nBase=1; #nGrip=1; nCam0=1; nImgF=1; nImgR=1
# nTabA=1; nTabB=1; nTabC=1
# nObjA=1; nObjB=1; nObjC=1; nObjD=1; nObjE=1; nUpdate=0

mxArm1=gp_Trsf(); mxArm2=gp_Trsf(); mxArm3=gp_Trsf()
mxArm4=gp_Trsf(); mxArm5=gp_Trsf(); mxArm6=gp_Trsf(); mxArm7=gp_Trsf()
# mxImgF=gp_Trsf(); mxImgR=gp_Trsf()
# mxTabA=gp_Trsf(); mxTabB=gp_Trsf(); mxTabC=gp_Trsf();
# mxObjA=gp_Trsf(); mxObjB=gp_Trsf(); mxObjC=gp_Trsf(); mxObjD=gp_Trsf(); mxObjE=gp_Trsf()

pi180=math.pi; pi90=pi180/2; pi360=pi180*2

#**********************************************************
# 機械手狀況顯示
#
# sTitle="PythonRobot"
# sText1="100"
# sText2="100\n200"
# sText3="100\n200\n300"
# sText4="100\n200\n300\n400"
_map  =[0]*100

# def sFloat(s,d):                       #**浮點轉字串
#     ss='{}={:9.3f}'.format(s,d)
#     return(ss)
# def sJoint(p):                         #**機械手關節座標
#     n=mm.nAxis;        s="";
#     for i in range(n): s=s+sFloat('J'+str(i+1),p[i+1])+"\n"
#     return(s.strip())
# def sMode(d):                          #**操作模式
#     text=["OFF","拖動","教導","自動","手動"]
#     if d<0: d=0
#     if d>4: d=4
#     return("MOD="+str(d)+"["+text[d]+"] ")
# def sAlarm(d):                         #**警報狀態
#     text=["正常","恢復","重啟","撞擊","剎車","","","","","警報"]
#     if d<0: d=0
#     if d>9: d=9
#     return("STS="+str(d)+"["+text[d]+"] ")
# def sStatus():                         #**顯示機械手狀態
#     s=   sMode      (_map[5])+"\n"
#     s=s+ sAlarm     (_map[4])+"\n"
#     s=s+"DEC="  +str(_map[1])+"\n"
#     s=s+"segI=" +str(_map[7])+"\n"
#     s=s+"segN=" +str(_map[8])+"\n"
#     s=s+"segK=" +str(_map[2])+"\n"
#     s=s+"ratio="+str(_map[0])
#     return(s)
# def sGravity():
#     n=mm.nAxis; s=""
#     for i in range(n):
#         d=(_map[91+i]>>16)&0xffff;
#         if d>=0x8000:  d-=0x10000;
#         s=s+"G"+str(i+1)+"="+str(d)+"\n"
#     return(s)
# def sInertia():
#     n=mm.nAxis; s=""
#     for i in range(n):
#         d=(_map[91+i])&0xffff;
#         if d>=0x8000:  d-=0x10000;
#         s=s+"M"+str(i+1)+"="+str(d)+"\n"
#     return(s)
# def sTCP(JntPos):
#     curtcp=mm.pTo(JntPos,'work')
#     s=""
#     s=s+sFloat('X',curtcp[1])+"\n"
#     s=s+sFloat('Y',curtcp[2])+"\n"
#     s=s+sFloat('Z',curtcp[3])+"\n"
#     s=s+sFloat('RX',curtcp[4])+"\n"
#     s=s+sFloat('RY',curtcp[5])+"\n"
#     s=s+sFloat('RZ',curtcp[6])+"\n"
#     return(s.strip())
# def sMapping(c,k):
#     n=mm.nAxis; s=""
#     for i in range(1,n+1):
#         d=_map[10*i+k];
#         s=s+c+str(i)+"="+str(d)+"\n"
#     return(s)
def doMessage():                       #**更新機械手數據
    # global sTitle,sText1,sText2,sText3,sText4
    global pipeEnd,_map
    if pipeEnd==1:    _map[0]=-1;
    if pipeEnd==0 and _map[0]>=0:
        for i in range(1,8):
            mm._track[i]=_map[10*i+0]/1000.
            mm._joint[i]=_map[10*i+5]/1000.
    # if nReal==0:
    #     sText1=copy.deepcopy(sStatus())
    #     sText2=copy.deepcopy("角度命令\n"+sMapping("POS",0))
    #     sText3=copy.deepcopy("重力計算\n"+sGravity())
    #     sText4=copy.deepcopy("慣量計算\n"+sInertia())
    # if nReal==1:
    #     sText1=copy.deepcopy(sStatus())
    #     sText2=copy.deepcopy("位置命令\n"+sJoint(mm._track))
    #     sText3=copy.deepcopy("位置回授\n"+sJoint(mm._joint))
    #     sText4=copy.deepcopy("直角坐標\n"+sTCP(mm._joint))
    # if nReal==2:
    #     sText1=copy.deepcopy("速度命令\n"+sMapping("VEL",1))
    #     sText2=copy.deepcopy("加速命令\n"+sMapping("ACC",2))
    #     sText3=copy.deepcopy("扭力命令\n"+sMapping("TRQ",3))
    #     sText4=copy.deepcopy("限制開關\n"+sMapping("MXC",4))
    # if nReal==3:
    #     sText1=copy.deepcopy("角度回授\n"+sMapping("ANG",5))
    #     sText2=copy.deepcopy("速度回授\n"+sMapping("SPD",6))
    #     sText3=copy.deepcopy("電流回授\n"+sMapping("AMP",7))
    #     sText4=copy.deepcopy("控制輸出\n"+sMapping("OUT",8))

#**********************************************************
# 控制參數設置
#
def sPoint(p):            #***** 單點轉字串(預設名稱) *****
    if not p:  return("NG")
    s=p[0]
    for i in range(1,8):
        d=p[i]
        if p[i]<0: s=s+" "+str(int(p[i]*1000-0.5)) 
        else:      s=s+" "+str(int(p[i]*1000+0.5))
    return(s)

def reset():                      #***** 開機設置部分 *****
    mm.pClear()
    mm.pSet("base",["world",  0.,0.,0.,0.,0.,0.,0.])
    mm.pSet("work",["base" ,  0.,0.,0.,0.,0.,0.,0.])
    mm.pSet("tool",["robot",  0.,0.,0.,0.,0.,0.,0.])
#     mm.pSet("tabA",["world",400.,0.,500.,0.,0.,0.,0.])
#     mm.pSet("tabB",["world",400.,0.,500.,0.,0.,0.,0.])
#     mm.pSet("tabC",["world",400.,0.,500.,0.,0.,0.,0.])
#     mm.pSet("work",["tabA" ,  0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("imgF",["robot",  0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("imgR",["robot",  0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("grp0",["robot", 35.,0., 80.,0.,0.,0.,0.])
#     mm.pSet("grp0",["robot",  0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("grp1",["robot",  0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("grp2",["robot",  0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("tool",["grp0",   0.,0.,  0.,0.,0.,0.,0.])
#     mm.pSet("objA",["work", 100., 150.,20.,0.,0.,0.,0.])
#     mm.pSet("objB",["work",-100.,-150.,20.,0.,0.,0.,0.])
#     mm.pSet("objC",["work",-100., 150.,20.,0.,0.,0.,0.])
#     mm.pSet("objD",["work", 100.,-150.,20.,0.,0.,0.,0.])
#     mm.pSet("objE",["work",   0.,   0.,20.,0.,0.,0.,0.])
    mm.pDot(-1)

def update():                     #***** 模擬更新部分 *****
    global mxArm1,mxArm2,mxArm3,mxArm4,mxArm5,mxArm6,mxArm7
    # global mxTabA,mxTabB,mxTabC
    # global mxObjA,mxObjB,mxObjC,mxObjD,mxObjE
    doMessage()
    mxArm1=mm.mxForward(mm._joint,0,1)
    mxArm2=mm.mxForward(mm._joint,0,2)
    mxArm3=mm.mxForward(mm._joint,0,3)
    mxArm4=mm.mxForward(mm._joint,0,4)
    mxArm5=mm.mxForward(mm._joint,0,5)
    mxArm6=mm.mxForward(mm._joint,0,6)
    mxArm7=mm.mxForward(mm._joint,0,7)
    # mxImgF=mm.mxFromP(mm.pGet("imgF","base"))
    # mxImgR=mm.mxFromP(mm.pGet("imgR","base"))
    # mxTabA=mm.mxFromP(mm.pGet("tabA","base"))
    # mxTabB=mm.mxFromP(mm.pGet("tabB","base"))
    # mxTabC=mm.mxFromP(mm.pGet("tabC","base"))
    # mxObjA=mm.mxFromP(mm.pGet("objA","base"))
    # mxObjB=mm.mxFromP(mm.pGet("objB","base"))
    # mxObjC=mm.mxFromP(mm.pGet("objC","base"))
    # mxObjD=mm.mxFromP(mm.pGet("objD","base"))
    # mxObjE=mm.mxFromP(mm.pGet("objE","base"))

#**********************************************************
# 遠端連線: 利用PIPE指令連線本機中的其他Python程式
#
pipe=None; pipeEnd=1
# class pipeServer(threading.Thread):
#     def run(self):
#         global pipeEnd
#         self.pipeHandle=win32pipe.CreateNamedPipe(
#                        '\\\\.\\pipe\\robotpipe',
#                         win32pipe.PIPE_ACCESS_DUPLEX,
#                         win32pipe.PIPE_TYPE_BYTE     |
#                         win32pipe.PIPE_READMODE_BYTE |
#                         win32pipe.PIPE_WAIT, 50,4096,4096,10000,None)
#         if self.pipeHandle==win32file.INVALID_HANDLE_VALUE:
#             print('Failed to create named pipe! Exiting...')
#             sys.exit(1)
#         print("pipeCreate()")
#         win32pipe.ConnectNamedPipe(self.pipeHandle)
#         print("pipeConnect()")
#         pipeEnd=0
#         while True:          #**取得PIPE命令並回覆
#             if pipeEnd>0: break;
#             n=win32file.GetFileSize(self.pipeHandle)
#             if n<=0: continue
#             time.sleep(0.01)
#             n=win32file.GetFileSize(self.pipeHandle)
#             e,v=win32file.ReadFile(self.pipeHandle,n,None)
#             cmd=str(v,encoding="utf-8"); #print("cmd=",cmd)
#             s=doCommand(cmd);            #print("echo=",s)
#                              #**送出pipe回覆
#             err,j=win32file.WriteFile (self.pipeHandle,bytes(s,encoding="utf-8"))
#             win32file.FlushFileBuffers(self.pipeHandle)
#         win32pipe.DisconnectNamedPipe (self.pipeHandle)
#         print("SERVER: Exiting server")

#**********************************************************
# 遠端指令(PIPE)包括:
#  .point list           : 列印單點清單
#  .point clear <s>      : 清除單點
#  .point set   <s> <z> <d1> <d2> .. : 設置單點
#  .point get   <s> <z>              : 讀取單點
#  .move     <j1> <j2>.. : 設置機械手的關節角
#  .put  <z> <d1> <d2>.. : 設置目標點(或軌跡線)
#  .grab on/off <s> ..   : 抓取物件或放開物件
#  .show <objA> <d>      : 指定顯示模式
#
# def doCommand(s):
#     global nGrip,nCam0,nImgF,nImgR,nBase,nReal
#     global nArm1,nArm2,nArm3,nArm4,nArm5,nArm6,nArm7
#     global nTabA,nTabB,nTabC,nUpdate
#     global nObjA,nObjB,nObjC,nObjD,nObjE,_map
#     # global sTitle,sText1,sText2,sText3,sText4
#     cmd=s.strip().split()
#     n=len(cmd)
#     if n<1:                      return("NG")
#                    #***** .move指令
#     if cmd[0]==".move":                #**[.move][d]..
#         if n<7 or n>8:           return("NG")
#         for i in range(1,n): mm._joint[i]=float(cmd[i])
#         mm.doForward();          return("OK")
#                    #***** .dot指令
#     if cmd[0]==".dot":                 #**[.dot][z][d]..
#         nUpdate=1;
#         if n<2: mm.pDot(-1);     return("OK")
#         p=[cmd[1],0.,0.,0.,0.,0.,0.,0.]
#         for i in range(2,n): p[i-1]=float(cmd[i])
#         mm.pDot(p);              return("OK")
#                    #***** .text指令
#     if cmd[0]==".text":                 #**[.text][k][s]..
#         if n<2 or n>102:         return("NG")
#         k=int(cmd[1])
#         if k==9:                          #**設置_map[]
#             for i in range(2,n): _map[i-2]=int(cmd[i])
#             return("OK")
#         s=""
#         for i in range(2,n): s=s+cmd[i]+"\n";
#         # if k==0: sTitle=copy.deepcopy(s)  #**設置sTitle
#         # if k==1: sText1=copy.deepcopy(s)  #**設置sText1
#         # if k==2: sText2=copy.deepcopy(s)  #**設置sText2
#         # if k==3: sText3=copy.deepcopy(s)  #**設置sText3
#         # if k==4: sText4=copy.deepcopy(s)  #**設置sText4
#         return("OK")
#                    #***** ,point指令
#     if cmd[0]==".point":
#         if n<2:                  return("NG")
#         if cmd[1]=="list":             #**[.point][list]
#             s=mm.pList();        return(s)
#         if cmd[1]=="clear":            #**[.point][clear][s]
#             if n<3: mm.pClear("")
#             else:
#                 for i in range(2,n):
#                     mm.pClear(cmd[i])
#             return("OK")
#         if cmd[1]=="set":              #**[.point][set][s][z][d]..
#             if n<10:             return("NG")
#             p=["",0.,0.,0.,0.,0.,0.,0.]
#             for i in range(4,n): p[i-3]=float(cmd[i])
#             s=cmd[2]; p[0]=cmd[3];
#             mm.pSet(s,p);        return("OK")
#         if cmd[1]=="get":              #**[.point][get][s][z]
#             if n<3:              return("NG")
#             if n<4: z=""
#             else:   z=cmd[3]
#             s=cmd[2]; p=mm.pGet(s,z)
#             if not p:            return("NG")
#             s=sPoint(p);         return(s)
#                    #***** .grab指令
#     if cmd[0]==".grab":
#         if n<3:                  return("NG")
#         s=cmd[1]
#         if s=="on"  or s=="1":         #**[.grab][on] [s]..
#             for i in range(2,n): mm.pGrab(cmd[i],"robot")
#         if s=="off" or s=="0":         #**[.grab][off][s]..
#             for i in range(2,n): mm.pGrab(cmd[i],"work")
#         return("OK")
#                    #***** .show指令
#     if cmd[0]==".show":                #**[.show][d][s]
#         if n<3:                  return("NG")
#         d=int(cmd[1])&0x03;  nUpdate=1
#         for i in range(2,n):
#             s=cmd[i]
#             if s=="real"  : nReal=d   #**即時連線更新
#             if s=="grip"  : nGrip=d   #**夾爪
#             if s=="camera": nCam0=d   #**相機
#             if s=="imgF"  : nImgF=d   #**影像
#             if s=="imgR"  : nImgR=d
#             if s=="robot" : nBase=nArm1=nArm2=nArm3=nArm4=nArm5=nArm6=nArm7=d
#             if s=="base"  : nBase=d   #**機械手
#             if s=="arm1"  : nArm1=d
#             if s=="arm2"  : nArm2=d
#             if s=="arm3"  : nArm3=d
#             if s=="arm4"  : nArm4=d
#             if s=="arm5"  : nArm5=d
#             if s=="arm6"  : nArm6=d
#             if s=="arm7"  : nArm7=d
#             if s=="tabA"  : nTabA=d   #**桌面A
#             if s=="tabB"  : nTabB=d   #**桌面B
#             if s=="tabC"  : nTabC=d   #**桌面C
#             if s=="objA"  : nObjA=d   #**物件A
#             if s=="objB"  : nObjB=d   #**物件B
#             if s=="objC"  : nObjC=d   #**物件C
#             if s=="objD"  : nObjD=d   #**物件D
#             if s=="objE"  : nObjE=d   #**物件E
#         return("OK")
#     return("NG")
