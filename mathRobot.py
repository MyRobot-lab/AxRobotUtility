# -*- coding: UTF-8 -*-
# 必須在檔案開始時增加上述標頭,才能使用中文註釋

import time, copy, math        #**數學運算
from  OCC.gp import *        #**矩陣運算

# Diagnostic
PtCnvChk = 0
PtCnvErr = 0
PtCnvColiErr = 0

pi180=math.pi; pi360=pi180*2; pi120=pi360/3;
pi90 =pi180/2; pi60=pi180/3;  pi45=pi180/4; pi30=pi180/6;
#**********************************************************
# 機械手模型設置
#
#URDF模型  [  x,   y,   z,   Rx,  Ry,  Rz]
modelURDF=[[  0.,  0.,230.,  0.,  0.,  1.],
           [ 25.,  0.,144.,  0.,  1.,  0.],
           [  0.,  0.,340.,  0.,  1.,  0.],
           [-40.,  0.,140.,  0.,  0.,  1.],
           [  0.,  0.,205.,  0.,  1.,  0.],
           [  0.,  0., 74.,  0.,  0.,  1.]]
nAxis =7           #**機械手總軸數
arm7=0; arm7H=pi90; arm7L=-pi90;
arm6=0; arm6H=pi90; arm6L=-pi90;
def putArm7(d):              #**設置七軸手肘模式
    global arm7,arm7H,arm7L; d=-d;
    if d> 90: d= 90;
    if d<-90: d=-90;
    arm7=d; arm7H=math.radians(d)+pi90; arm7L=math.radians(d)-pi90;
def putArm6(d):              #**設置六軸手腕模式
    global arm6,arm6H,arm6L; d=-d;
    if d> 90: d= 90;
    if d<-90: d=-90;
    arm6=d; arm6H=math.radians(d)+pi90; arm6L=math.radians(d)-pi90;

#**********************************************************
# 單點數據庫: 距離=mm, 角度=deg
#
points=dict()                          #**儲存所有單點
_joint=["joint",0.,0.,0.,0.,0.,0.,0.]  #**目前的關節座標
_robot=["base", 0.,0.,0.,0.,0.,0.,0.]  #**目前的直角座標
_none =["",     0.,0.,0.,0.,0.,0.,0.]  #**錯誤時的回覆值

def pJoint():         #***** 取得目前位置(關節座標系) *****
    return(copy.deepcopy(_joint))
def pRobot():         #***** 取得目前位置(直角座標系) *****
    return(copy.deepcopy(_robot))
def pPoint(s):            #***** 取得指定點(安全使用) *****
    return(copy.deepcopy(point(s)))
def point(s):             #***** 取得指定點(內部使用) *****
    if s=="joint":  return(_joint)
    if s=="robot":  return(_robot)
    if s in points: return(points[s])
    return(_none)
def pExist(s):                #***** 檢查單點是否存在 *****
    if not s or len(s)==0: return(False)
    if s=="joint":         return(True)
    if s=="robot":         return(True)
    if s=="world":         return(True)
    return(s in points)
                                  #***** 列印所有單點 *****
def pList():   return(str(points.keys()))
def pClear(s=""):                     #***** 清除單點 *****
    if     len(s)==0: points.clear()
    elif s in points: del points[s]
def pGrab(s,z):                     #***** 變更基準點 *****
    if not pExist(s):    return None
    if not pExist(z):    return None
    pSet(s,pGet(s,z))
#def pSet(s,p): points[s]=p            #***** 設置單點 *****
def pSet(s,p): points[s]=copy.deepcopy(p)            #***** 設置單點 *****
def pTo(p,z):                         #***** 轉換單點 *****
    global PtCnvChk, PtCnvColiErr, PtCnvErr
    if PtCnvChk != 0:
        PtCnvColiErr += 1
    PtCnvChk += 1

    pSet("###CONV",p)
    pTmp = pGet("###CONV",z)

    if pTmp == None:
        PtCnvErr += 1
    PtCnvChk -= 1
    return pTmp
def pGet(s,z=""):                     #***** 取得單點 *****
    if not pExist(s):    return None   #**單點未定義
    p=pPoint(s)
    
    if len(z)==0:        return(p)     #**直接回覆
    if z=="joint":           #**直角座標轉換成關節座標
        if p[0]==z:      return(p);    #**直接回覆
        ss=pTree(s,"world")
        if not ss:       return None   #**錯誤結束
        n=len(ss); mx=mxTree(ss,n)     #**合成M34矩陣
        mx.Multiply   (mxTool("tool").Inverted()) #**扣除刀具部分
        mx.PreMultiply(mxBase("base").Inverted()) #**扣除基座部分
        return(toJointP(mxToP(mx)))    #**回覆關節座標
    if p[0]=="joint":        #**關節座標轉換成直角座標
        mx=mxFromP(toRobotP(p))             #**轉成直角座標
        mx.PreMultiply(mxBase("base"))      #**加上基座部分
        mx.Multiply   (mxTool("tool"))      #**加上刀具部分
        mx.PreMultiply(mxBase(z).Inverted())#**扣除基準部分
        p=mxToP(mx); p[0]=z; return(p)      #**回覆直角座標
    ss=pTree(s,z)
    if not ss:           return None   #**錯誤結束
    n=len(ss); mx=mxTree(ss,n)         #**合成M34矩陣
    s=ss[n-1]; p=pPoint(s)
    if p[0]!=z:                        #**扣除基準部分
        ss=pTree(z,"world")
        if not ss:       return None   #**錯誤結束
        n=len(ss)
        mx.PreMultiply(mxTree(ss,n).Inverted())
    p=mxToP(mx); p[0]=z; return(p)     #**更換基準後回覆

def pTree(s,z=""):             #***** 搜尋所有基準點 *****
    if not pExist(s):     return None  #**未定義
    ss=[s]; p=point(s)
    for i in range(10):
        if not p:         return None  #**結束(錯誤)
        if p[0]== z:      return(ss)   #**結束(找到基準點)
        if p[0]=="joint": return None  #**結束(錯誤)
        if p[0]=="world": return(ss)   #**結束(找到world)
        s=p[0]; ss.append(s); p=point(s)
    return(ss)
def mxTree(ss,n):                #***** 合成M34[]矩陣 *****
    for i in range(n):                 #**正向運算
        s=ss[n-i-1]
        if s=="robot": mxx=mxForward(_joint,0,nAxis);
        else:          mxx=mxFromP(pPoint(s));
        if i==0: mx=mxx
        else:    mx.Multiply(mxx)
    return(mx)
def mxTool(s):                  #***** M34[]=刀具部分 *****
    ss=pTree(s,"robot"); n=len(ss)
    return(mxTree(ss,n))
def mxBase(s):                 #****** M34[]=基座部分 *****
    ss=pTree(s,"world"); n=len(ss)
    return(mxTree(ss,n))

#**********************************************************
# 軌跡設置部分: 軌跡線是一連串的單點所組成的序列
#
tracks=list();
def pTrack(p=None):               #***** pTrack()指令 *****
    if isinstance(p,int):    #**讀取tracks[n]
        n=p;
        if n<0:              #**清除tracks[]
            tracks.clear(); return None
        if n<len(tracks):   return(tracks[n])
        else:               return(_none) 
    if isinstance(p,str):    #**設置tracks[]
        ss=p.strip().split(" ")
        if len(ss)<=1: ss=p.strip().split(",")
        n=len(ss)
        for i in range(n):
            s=ss[i].strip()
            p=pGet(s,"joint")
            if len(p[0])>0: pAppend(p)
        return None
    if isinstance(p,list):   #**設置tracks[]
        p=pTo(p,"joint")
        if len(p[0])>0:     pAppend(p)
        return None
    return(len(tracks))
def pAppend(p):                   #***** pTrack[]單筆 *****
    tracks.append(p)

#**********************************************************
# 矩陣運算部分
#   mx=mxFromZYZ(): 從(degH,degV,degS)換算M34[]
#   mx=mxFromP(p) : 從(x,y,z,Rx,Ry,Rz)換算M34[]
#    p=mxToP(mx)  : 從M34[]換算(x,y,z,Rx,Ry,Rz)
#
def mxFromPOS(x,y,z):              #***** mx=M(x,y,z) *****
    mx=gp_Trsf(); mx.SetValues(1.,0.,0.,x,
                               0.,1.,0.,y,
                               0.,0.,1.,z);
    return(mx)

def mxFromZYZ(H,V,S,deg=1):        #***** mx=M(H,V,S) *****
    if deg>0:
        H=math.radians(H); V=math.radians(V); S=math.radians(S);
    ca=math.cos(H); sa=math.sin(H)
    cb=math.cos(V); sb=math.sin(V)
    cc=math.cos(S); sc=math.sin(S)
    m11=ca*cb*cc-sa*sc; m12=-ca*cb*sc-sa*cc; m13=ca*sb;
    m21=sa*cb*cc+ca*sc; m22=-sa*cb*sc+ca*cc; m23=sa*sb;
    m31=  -sb*cc;       m32=    sb*sc;       m33=   cb;
    mx=gp_Trsf(); mx.SetValues(m11,m12,m13,0.,
                               m21,m22,m23,0.,
                               m31,m32,m33,0.);
    return(mx)
                   #***** 從(x,y,z,Rx,Ry,Rz)換算M34[] *****
def mxXYZABC(x,y,z,Rx,Ry,Rz,deg=1):
    if deg>0:                          #**degree to radian
        Rx=math.radians(Rx); Ry=math.radians(Ry); Rz=math.radians(Rz);
    a=Rz; ca=math.cos(a); sa=math.sin(a)
    b=Ry; cb=math.cos(b); sb=math.sin(b)
    c=Rx; cc=math.cos(c); sc=math.sin(c)
    m11=ca*cb; m12=ca*sb*sc-sa*cc; m13=ca*sb*cc+sa*sc; m14=x
    m21=sa*cb; m22=sa*sb*sc+ca*cc; m23=sa*sb*cc-ca*sc; m24=y
    m31=  -sb; m32=   cb*sc;       m33=   cb*cc;       m34=z
    mx=gp_Trsf(); mx.SetValues(m11,m12,m13,m14,
                               m21,m22,m23,m24,
                               m31,m32,m33,m34);
    return(mx)

def mxFromP(p,deg=1): #*** 從(x,y,z,Rx,Ry,Rz)換算M34[] ****
    return(mxXYZABC(p[1],p[2],p[3],p[4],p[5],p[6],deg))

def mxToP(mx):     #***** 從M34[]換算(x,y,z,Rx,Ry,Rz) *****
    p=["",0.,0.,0.,0.,0.,0.,0.]
    x = mx.Value(1,4); y =mx.Value(2,4); z=mx.Value(3,4)
    sa= mx.Value(2,1); ca=mx.Value(1,1);      a=math.atan2(sa,ca)
    sb=-mx.Value(3,1);  d=1-sb*sb
    if d<0.00001: d=0.
    cb=math.sqrt(d);                          b=math.atan2(sb,cb)
    sc= mx.Value(3,2); cc=mx.Value(3,3);      c=math.atan2(sc,cc)
    if cb<0.0001:            #**b=+/-90度時,(a,c)=多重解
        a=0.; sc= mx.Value(1,2)/sb; cc=mx.Value(1,3)/sb; c=math.atan2(sc,cc)
    elif c>pi90 or c<-pi90:  #**c限制在(+/-90度)範圍
        a=math.atan2(-sa,-ca); b=math.atan2(sb,-cb); c=math.atan2(-sc,-cc);
    if b<-pi120: b+=pi360;   #**b限制在(-120度~+240度)
    p[1]=x; p[4]=math.degrees(c)
    p[2]=y; p[5]=math.degrees(b)
    p[3]=z; p[6]=math.degrees(a)
    return(p)

def mxToXYZ(mx):            #***** 從M34[]換算(x,y,z) *****
    x=mx.Value(1,4); y=mx.Value(2,4); z=mx.Value(3,4)
    return(x,y,z)

def mxZYZ(mx,p):            #***** 從M34[]換算(z,y,z) *****
    sa= mx.Value(2,3); ca= mx.Value(1,3);     a=math.atan2(sa,ca)
    cb= mx.Value(3,3);  d=1-cb*cb
    if d<0.00001: d=0.
    sb= math.sqrt(d);                         b=math.acos (   cb)
    sc= mx.Value(3,2); cc=-mx.Value(3,1);     c=math.atan2(sc,cc)
    if sb<0.0001:            #b=0度時,    (a,c)=多重解
        a=0.; sc=-mx.Value(1,2)/cb; cc=mx.Value(1,1)/cb; c=math.atan2(sc,cc)
    if a>arm6H or a<arm6L:   #**當a過頭時,限制a在(H,L)之間
        if a<0 : a+=pi180;   #**a轉180度
        else:    a-=pi180;
        b=-b;                #**b正負翻轉
        if c<0:  c+=pi180;   #**c轉180度
        else:    c-=pi180;
    p[2]=math.degrees(a); p[1]=math.degrees(b); p[0]=math.degrees(c)

def mxARM(p,n):            #***** 從URDF模型換算M34[] *****
    ang=p[n]; m=modelURDF[n-1]
    x=m[0]; y=m[1]; z=m[2]; Rx=m[3]; Ry=m[4]; Rz=m[5]
    if Rx>0.5: Rx=ang
    if Ry>0.5: Ry=ang
    if Rz>0.5: Rz=ang
    return(mxXYZABC(x,y,z,Rx,Ry,Rz))

def mxMOV(mx,p):       #***** 移動端點坐標系的(x,y,z) *****
    x=p[0]; y=p[1]; z=p[2];
    for i in range(1,4):
        p[i-1]=mx.Value(i,1)*x+mx.Value(i,2)*y+mx.Value(i,3)*z+mx.Value(i,4)
    return(p)

#**********************************************************
# 三角函數計算
#   dst2(),dst3(): 計算直線距離
#   ang3()       : 已知三角邊長,計算夾角
#   sid3()       : 已知兩邊和夾角,求取對邊邊長
#   triangle()   : 確認三角形是存在的
#
def dst2(x,y):    return(math.sqrt(x*x+y*y))
def dst3(x,y,z):  return(math.sqrt(x*x+y*y+z*z))
def ang3(a,b,c):  return(math.acos((a*a+b*b-c*c)/(a*b*2)))
def sid3(a,b,th): return(math.sqrt(a*a+b*b-a*b*math.cos(th)))
def triangle(a,b,c):
    a=math.fabs(a); b=math.fabs(b); c=math.fabs(c)
    if (a+b)<=c: return(False)
    if (b+c)<=a: return(False)
    if (c+a)<=b: return(False)
    return(True)

#**********************************************************
# 正向運動(Forward)和逆向運動(Inverse)計算
#   p=toRobotP(p): 正向運動計算,從joint座標換算robot座標
#   p=toJointP(p): 逆向運動計算,從robot座標換算joint座標
#
def iDeg(th): return(int(math.degrees(th)))
def printM(mx):
    pass
    # print("***** mx[]=")
    # print(mx.Value(1,1),mx.Value(1,2),mx.Value(1,3),mx.Value(1,4))
    # print(mx.Value(2,1),mx.Value(2,2),mx.Value(2,3),mx.Value(2,4))
    # print(mx.Value(3,1),mx.Value(3,2),mx.Value(3,3),mx.Value(3,4))

def mxForward(p,i,n):      #***** 正向運動計算(i~n軸) *****
    for j in range(i,n):
        if j==i: mx=         mxARM(p,j+1)
        else:    mx.Multiply(mxARM(p,j+1))
    return(mx)
                        #***** 求取六軸機械手的前三軸 *****
def inverse3(mx,z6,z35,x35,d23):
    p=mxMOV(mx,[0.,0.,-z6]);           #**後退z6的距離
    x=p[0]; y=p[1]; z=p[2]             #**取得p5的座標
    j1 =math.atan2(y,x)                #**取得J1角度
    x2 =modelURDF[1][0]                #**扣除p2的影響
    x -=x2*math.cos(j1)
    y -=x2*math.sin(j1)
    z -=modelURDF[0][2]+modelURDF[1][2]
    d25=dst3(x,y,z)                    #**取得三角形的邊長
    d35=dst2(z35,x35)
    if not triangle(d23,d35,d25):
        return(999.,0.,0.,0.)          #**若三角形不成立則無解
    q25=ang3(d23,d35,d25)              #**由三角形各邊長,求解各夾角
    q35=ang3(d23,d25,d35)
    d =dst2(x,y); th=math.atan2(z,d)
    j2=pi90 -(q35+math.atan2(z,d))     #**取得J2/J3的角度
    j3=pi180-(q25+math.atan2(x35,z35)); j4=j3;
    if nAxis==6:                       #**六軸機械手部分結束
        return(math.degrees(j1),math.degrees(j2),math.degrees(j3),0.)
    if arm7==0:                        #**七軸機械手部分
        return(math.degrees(j1),math.degrees(j2),0.,math.degrees(j4))
#    print("***** j1=",iDeg(j1),"j2=",iDeg(j2),"j3=0.","j4=",iDeg(j4))
    x4=-d23*math.sin(q35); y4=0.;      #**手肘座標(x4,y4,z4)旋轉
    z4= d23*math.cos(q35);
    degH=math.atan2(y,x); d=dst2(x,y);
    degV=math.atan2(d,z); degS=math.radians(arm7);
    mx=mxFromZYZ(degH,degV,degS,0);
    mx.Multiply(mxFromPOS(x4,y4,z4)); x4,y4,z4=mxToXYZ(mx)
    j1=     math.atan2(y4,x4)          #**設置J1角度
    j2=math.atan2(dst2(x4,y4),z4);     #**設置J2角度
    mx=mxFromPOS(x,y,z);               #**設置J3角度
    mx.PreMultiply(mxFromZYZ(j1,j2,0.,0).Inverted());
    mx,my,mz=mxToXYZ(mx);       j3=math.atan2(my,mx);
#    print("      j1=",iDeg(j1),"j2=",iDeg(j2),"j3=",iDeg(j3),"j4=",iDeg(j4))
    if j3>=arm7H or j3<arm7L:          #**當J3過頭時
        if j1<0:    j1+=pi180;         #**J1轉180度
        else:       j1-=pi180;
        j2=-j2;                        #**J2正負切換
        if j3<0:    j3+=pi180;         #**J3轉180度
        else:       j3-=pi180;
#    print("      j1=",iDeg(j1),"j2=",iDeg(j2),"j3=",iDeg(j3),"j4=",iDeg(j4))
    return(math.degrees(j1),math.degrees(j2),math.degrees(j3),math.degrees(j4))

def inverse6(p):     #***** 從_robot[]換算至_joint[] *****
    mx =mxFromP(p);          #**取得機械手的轉移函數
    p  =["",0.,0.,0.,0.,0.,0.,0.]
    z6 =modelURDF[5][2]
    z35=modelURDF[3][2]+modelURDF[4][2]
    x35=modelURDF[3][0]
    d23=modelURDF[2][2]
                             #**先求取六軸中的前三軸
    j1,j2,j3,j4=inverse3(mx,z6,z35,x35,d23)
    if j1>180.: return(p)    #**若三角形不成立則無解
    p[1]=j1;    p[2]=j2;    p[3]=j3
    mx13=mxForward(p,0,3)              #取得前三軸
    mx.PreMultiply(mx13.Inverted())    #取得後三軸
    p3=[0.,0.,0.]; mxZYZ(mx,p3)
    p[4]=p3[2]; p[5]=p3[1]; p[6]=p3[0]
    return(p)

def inverse7(p):     #***** 從_robot[]換算至_joint[] *****
    mx =mxFromP(p);          #**取得機械手的轉移函數
    p  =["",0.,0.,0.,0.,0.,0.,0.]
    z6 =modelURDF[6][2]
    z35=modelURDF[4][2]+modelURDF[5][2]
    x35=modelURDF[4][0]
    d23=modelURDF[2][2]+modelURDF[3][2]
                             #**先求取七軸中的前四軸
    j1,j2,j3,j4=inverse3(mx,z6,z35,x35,d23)
    if j1>180.: return(p)    #**若三角形不成立則無解
    p[1]=j1;    p[2]=j2;    p[3]=j3; p[4]=j4
    mx14=mxForward(p,0,4)              #取得前四軸
    mx.PreMultiply(mx14.Inverted())    #取得後三軸
    p3=[0.,0.,0.]; mxZYZ(mx,p3)
    p[5]=p3[2]; p[6]=p3[1]; p[7]=p3[0]
    return(p)

def trimP(p):                  #***** 刪除過長的小數 *****
    for i in range(1,8):
        if p[i]<0.: p[i]=float(int(p[i]*1000-0.5))/1000.
        else:       p[i]=float(int(p[i]*1000+0.5))/1000.

def toRobotP(p):                 #***** 正向運動計算 *****
    mx=mxForward(p,0,nAxis)
    p=mxToP(mx);
    p[0]="base";  trimP(p); return(p)
def toJointP(p):                 #***** 逆向運動計算 *****
    if nAxis==6: p=inverse6(p)
    if nAxis==7: p=inverse7(p)
    p[0]="joint"; trimP(p); return(p)

def doForward():                 #***** 正向運動計算 *****
    p=toRobotP(_joint)
    for i in range(1,7):       _robot[i]=p[i]
def doInverse():                 #***** 逆向運動計算 *****
    p=toJointP(_robot)
    for i in range(1,nAxis+1): _joint[i]=p[i]

#**********************************************************
# 向量轉換部分:        假設 p1+p2=p3,則
#   p3=toNextP(p1,p2): 已知(p1,p2),計算p3 
#   p1=toPrevP(p3,p2): 已知(p3,p2),計算p1
#   p2=toDiffP(p3,p1): 已知(p3,p1),計算p2
#
def toNextP(p1,p2):
    m1=mxFromP(p1); m2=mxFromP(p2)
    mx=m1;          mx.Multiply(m2)
    p3=mxToP(mx); p3[0]=p1[0]; trimP(p3); return(p3)

def toPrevP(p3,p2):
    m3=mxFromP(p3); m2=mxFromP(p2)
    mx=m3;          mx.Multiply(m2.Inverted())
    p1=mxToP(mx); p1[0]=p3[0]; trimP(p1); return(p1)

def toDiffP(p3,p1):
    m3=mxFromP(p3); m1=mxFromP(p1)
    mx=m3;          mx.PreMultiply(m1.Inverted())
    p2=mxToP(mx);              trimP(p2); return(p2)
                    #***** 由夾爪角度來設置(Rx,Ry,Rz) *****
def pTool(p,degT,degH=0.,degV=0.,degS=0.,axis='z'):
    for i in range(len(p),8):p.append(0.)   #**補齊數列
    mx=mxFromP([0.,0.,0.,0., 0.,degT,0.])
    mode=int(degT)
    if   mode==0:                           #**上舉模式
        mx.Multiply(mxFromP([0.,0.,0.,0., 0.,  0., degH]))
        mx.Multiply(mxFromP([0.,0.,0.,0., 0., degV,  0.]))
    elif mode==90:                          #**水平向前
        mx.Multiply(mxFromP([0.,0.,0.,0.,-degH,0.,   0.]))
        mx.Multiply(mxFromP([0.,0.,0.,0., 0.,-degV,  0.]))
    elif mode==180:                         #**下垂模式
        mx.Multiply(mxFromP([0.,0.,0.,0., 0.,  0.,-degH]))
        mx.Multiply(mxFromP([0.,0.,0.,0., 0.,-degV,  0.]))
    elif mode==270 or mode==-90:            #**水平向後
        mx.Multiply(mxFromP([0.,0.,0.,0., degH,0.,   0.]))
        mx.Multiply(mxFromP([0.,0.,0.,0., 0.,-degV,  0.]))
    else:  return(p)
    if   axis=='x' or axis=='X':       #**軸心=X
        mx.Multiply(mxFromP([0.,0.,0.,0.,degS,0.,0.]))
    elif axis=='y' or axis=='Y':       #**軸心=Y
        mx.Multiply(mxFromP([0.,0.,0.,0.,0.,degS,0.]))
    else:                              #**軸心=Z
        mx.Multiply(mxFromP([0.,0.,0.,0.,0.,0.,degS]))
    d=mxToP(mx)
    p[4]=d[4]; p[5]=d[5]; p[6]=d[6]; return(p)
