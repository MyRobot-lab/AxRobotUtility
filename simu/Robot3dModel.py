
import sys, math, time, random, threading, logging

# from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse,BRepAlgoAPI_Cut,BRepAlgoAPI_Common
# from OCC.BRepGProp import brepgprop_LinearProperties
from OCC.BRepPrimAPI import BRepPrimAPI_MakeSphere
# from OCC import VERSION
# from OCC.GProp import GProp_GProps
from OCC.TopLoc import TopLoc_Location
from OCC.Quantity           import Quantity_Color#, Quantity_TOC_RGB
from OCC.gp import gp_Trsf, gp_Vec, gp, gp_Ax2, gp_Pnt
from OCC.Display.backend import load_backend, get_qt_modules

from PyQt5.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot
import simu.pipeRobot as pp       #**遠端通訊
import simu.mathRobot as mm       #**數學計算

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

used_backend = load_backend('qt-pyqt5')
if 'qt' in used_backend:
    from OCC.Display.qtDisplay import qtViewer3d
    QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()

stp_dir = 'simu/stp/ASIX/AxRobot_Zero'

#URDF模型  [  x,    y,  z,    Rx,  Ry,  Rz]
modelURDF=[[  0.,   0.,220., 0.,  0.,  1.],
           [  0.,   0.,155., 0.,  1.,  0.],
           [  0.,   0.,288., 0.,  0.,  1.],
           [  0.,   0.,137., 0.,  1.,  0.],
           [  0.,   0.,245., 0.,  0.,  1.],
           [  0.,   0.,180., 0.,  1.,  0.],
           [  0.,   0., 80., 0.,  0.,  1.],
           [  0.,   0., 10., 0.,  0.,  0.]]
mm.nAxis=7
mm.modelURDF=modelURDF
mm.putArm7(90)

degM=10.; mmM=10.                           #**手動移動量=10度
pnt0=gp.Origin()                            #**原點=(0,0,0)
dirX=gp.DX();  dirY=gp.DY(); dirZ=gp.DZ()   #**指向的X軸/Y軸/Z軸
axsX=gp.OX();  axsY=gp.OY(); axsZ=gp.OZ()   #**坐標系的X軸/Y軸/Z軸
pi180=math.pi; pi90=pi180/2; pi360=pi180*2  #**常用角度的radian值

_dots=list(); nDot=128       #**目標點和軌跡線的處理

#*********************************************************************************************************************************************************
# 機械手臂模型
#
#
#*********************************************************************************************************************************************************
class Robot3dModel (QObject):
    sigMainWinEventHandler = pyqtSignal(dict)

    def __init__(self):
        super(Robot3dModel, self).__init__()
        self.canva = qtViewer3d()
        self.canva.resize(400, 700)
        pp.reset()

    @pyqtSlot(dict)
    def sltEventHandler(self, dctEvents):
        # General Event Handler
        for k, v in dctEvents.items():
            # Filter out debug log
            log.debug("RxEvent:%s, %s\r\n", k, str(v))

            if k == "Create3dModle":
                self.armDisplay()
            elif k == "Update3dModle":
                self.segUpdate()

    def arm_init(self):             #**
        app = QtWidgets.QApplication(sys.argv)
        self.canva.InitDriver()
        self.canva.qApp = app
        self.canva._display.set_bg_gradient_color(206, 215, 222, 128, 128, 128)
        self.canva._display.display_trihedron()
        self.canva._display.DisableAntiAliasing()
        self.canva._display.SetModeShaded()

    # finished = pyqtSignal()
    # @pyqtSlot()
    # def timerStop(self):             #**
    #     self.update_timer.stop()
    #     self.finished.emit()

    @pyqtSlot()
    def armDisplay(self):
    #     threading.Thread(daemon=True,target=self.armplay).start()
    # def armplay(self):
        color = Quantity_Color()
        Quantity_Color.Argb2color(0x006e0d0a,color)
        self.base=  self.baseMaker(); self.base=self.canva._display.DisplayColoredShape(self.base,color,update=True)
        Quantity_Color.Argb2color(0x006e460a,color)
        self.arm1=  self.arm1Maker(); self.arm1=self.canva._display.DisplayColoredShape(self.arm1,color,update=True)
        Quantity_Color.Argb2color(0x006e600a,color)
        self.arm2=  self.arm2Maker(); self.arm2=self.canva._display.DisplayColoredShape(self.arm2,color,update=True)
        Quantity_Color.Argb2color(0x00496e0a,color)
        self.arm3=  self.arm3Maker(); self.arm3=self.canva._display.DisplayColoredShape(self.arm3,color,update=True)
        Quantity_Color.Argb2color(0x000a6b5b,color)
        self.arm4=  self.arm4Maker(); self.arm4=self.canva._display.DisplayColoredShape(self.arm4,color,update=True)
        Quantity_Color.Argb2color(0x000a416b,color)
        self.arm5=  self.arm5Maker(); self.arm5=self.canva._display.DisplayColoredShape(self.arm5,color,update=True)
        Quantity_Color.Argb2color(0x003a0a6b,color)
        self.arm6=  self.arm6Maker(); self.arm6=self.canva._display.DisplayColoredShape(self.arm6,color,update=True)
        Quantity_Color.Argb2color(0x00690956,color)
        self.arm7=  self.arm7Maker(); self.arm7=self.canva._display.DisplayColoredShape(self.arm7,color,update=True)
        # self.grip=  self.gripMaker(); self.grip=self.canva._display.DisplayShape(self.grip,update=True)
        # self.cam0=self.cameraMaker(); self.cam0=self.canva._display.DisplayShape(self.cam0,update=True)
        # self.imgF=  self.imgMaker(1); self.imgF=self.canva._display.DisplayShape(self.imgF,update=True)
        # self.imgR=  self.imgMaker(2); self.imgR=self.canva._display.DisplayShape(self.imgR,update=True)
        # self.tabA= self.tableMaker();self.tabA=self.canva._display.DisplayColoredShape(self.tabA,'WHITE' ,update=True)
        # self.tabB= self.tableMaker();self.tabB=self.canva._display.DisplayColoredShape(self.tabB,'WHITE' ,update=True)
        # self.tabC= self.tableMaker();self.tabC=self.canva._display.DisplayColoredShape(self.tabC,'WHITE' ,update=True)
        # self.objA=  self.objMaker(1);self.objA=self.canva._display.DisplayColoredShape(self.objA,'RED'   ,update=True)
        # self.objB=  self.objMaker(2);self.objB=self.canva._display.DisplayColoredShape(self.objB,'BLUE'  ,update=True)
        # self.objC=  self.objMaker(3);self.objC=self.canva._display.DisplayColoredShape(self.objC,'YELLOW',update=True)
        # self.objD=  self.objMaker(4);self.objD=self.canva._display.DisplayColoredShape(self.objD,'GREEN' ,update=True)
        # self.objE=  self.objMaker(5);self.objE=self.canva._display.DisplayColoredShape(self.objE,'BLACK' ,update=True)
        # pp.nself.imgF=0; self.canva._display.Context.SetDisplayMode(self.imgF.GetHandle(),pp.nImgF)
        # pp.nself.imgR=0; self.canva._display.Context.SetDisplayMode(self.imgR.GetHandle(),pp.nImgR)
        # pp.nGrip=3; self.canva._display.Context.SetDisplayMode(self.grip.GetHandle(),pp.nGrip)
        # pp.nCam0=3; self.canva._display.Context.SetDisplayMode(self.cam0.GetHandle(),pp.nCam0)
        # pp.nImgF=3; self.canva._display.Context.SetDisplayMode(self.imgF.GetHandle(),pp.nImgF)
        # pp.nImgR=3; self.canva._display.Context.SetDisplayMode(self.imgR.GetHandle(),pp.nImgR)

        self.dotMaker();                  #**建構指示點
        pp.pipeEnd=0
    # def StartUpdate(self):
        self.segUpdate()
        # self.update_timer=QTimer()        #**建構Timer
        # self.update_timer.timeout.connect(self.segUpdate)
        # self.finished.emit()
        #self.update_timer.timeout.connect(self.updateStatus)
        #self.update_timer.start(200)
        #self.pipe_ON()
        # self.finished.emit()

        # self.canva._display.View_Left()
        self.canva._display.FitAll()

    def segUpdate(self,event=None):   #**畫面中的機械手各軸更新
        self.canva._display.OnResize()
        pp.update()
        # update(); 
        # txtUpdate()
        self.canva._display.Context.SetLocation(self.arm1.GetHandle(),TopLoc_Location(pp.mxArm1))
        self.canva._display.Context.SetLocation(self.arm2.GetHandle(),TopLoc_Location(pp.mxArm2))
        self.canva._display.Context.SetLocation(self.arm3.GetHandle(),TopLoc_Location(pp.mxArm3))
        self.canva._display.Context.SetLocation(self.arm4.GetHandle(),TopLoc_Location(pp.mxArm4))
        self.canva._display.Context.SetLocation(self.arm5.GetHandle(),TopLoc_Location(pp.mxArm5))
        self.canva._display.Context.SetLocation(self.arm6.GetHandle(),TopLoc_Location(pp.mxArm6))
        self.canva._display.Context.SetLocation(self.arm7.GetHandle(),TopLoc_Location(pp.mxArm7))
        # self.canva._display.Context.SetLocation(self.grip.GetHandle(),TopLoc_Location(pp.mxgrip))
        # self.canva._display.Context.SetLocation(self.cam0.GetHandle(),TopLoc_Location(pp.mxcam0))
        # self.canva._display.Context.SetLocation(self.imgF.GetHandle(),TopLoc_Location(pp.mximgF))
        # self.canva._display.Context.SetLocation(self.imgR.GetHandle(),TopLoc_Location(pp.mximgR))
        # self.canva._display.Context.SetLocation(self.tabA.GetHandle(),TopLoc_Location(pp.mxTabA))
        # self.canva._display.Context.SetLocation(self.tabB.GetHandle(),TopLoc_Location(pp.mxTabB))
        # self.canva._display.Context.SetLocation(self.tabC.GetHandle(),TopLoc_Location(pp.mxTabC))
        # self.canva._display.Context.SetLocation(self.objA.GetHandle(),TopLoc_Location(pp.mxObjA))
        # self.canva._display.Context.SetLocation(self.objB.GetHandle(),TopLoc_Location(pp.mxObjB))
        # self.canva._display.Context.SetLocation(self.objC.GetHandle(),TopLoc_Location(pp.mxObjC))
        # self.canva._display.Context.SetLocation(self.objD.GetHandle(),TopLoc_Location(pp.mxObjD))
        # self.canva._display.Context.SetLocation(self.objE.GetHandle(),TopLoc_Location(pp.mxObjE))
        self.canva._display.Context.UpdateCurrentViewer()

    def stepFile(self,fname):
        from OCC.STEPControl import STEPControl_Reader
        p=STEPControl_Reader()
        p.ReadFile(fname)
        p.TransferRoot()
        blk=p.OneShape()
        return(blk)

    def baseMaker(self):             #**建構base
        blk=self.stepFile(stp_dir+'/Base.stp');
        x=0.; y=0.; z=0.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm1Maker(self):             #**建構arm1
        blk=self.stepFile(stp_dir+'/J1.stp');
        x=0.; y=0.; z=-220.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm2Maker(self):             #**建構arm2
        blk=self.stepFile(stp_dir+'/J2.stp');
        x=0.; y=0.; z=-375.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm3Maker(self):             #**建構arm3
        blk=self.stepFile(stp_dir+'/J3.stp');
        x=0.; y=0.; z=-663.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm4Maker(self):             #**建構arm4
        blk=self.stepFile(stp_dir+'/J4.stp');
        x=0.; y=0.; z=-800.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm5Maker(self):             #**建構arm5
        blk=self.stepFile(stp_dir+'/J5.stp');
        x=0.; y=0.; z=-1045.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm6Maker(self):             #**建構arm6
        blk=self.stepFile(stp_dir+'/J6.stp');
        x=0.; y=0.; z=-1225.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    def arm7Maker(self):             #**建構arm7
        blk=self.stepFile(stp_dir+'/J7.stp');
        x=0.; y=0.; z=-1305.
        mx=gp_Trsf(); mx.SetTranslation(gp_Vec(x,y,z))
        blk.Move(TopLoc_Location(mx))
        return(blk)

    # def cameraMaker(self):           #**建構camera
    #     blk=self.stepFile(stp_dir+'/Camera.stp');
    #     mx1=gp_Trsf(); mx1.SetRotation(axsX,pi90);
    #     mx2=gp_Trsf(); mx2.SetRotation(axsZ,pi180); x=0.; y=0.; z=10.
    #     mx3=gp_Trsf(); mx3.SetTranslation(gp_Vec(x,y,z))
    #     mx=mx3; mx.Multiply(mx2); mx.Multiply(mx1);
    #     blk.Move(TopLoc_Location(mx))
    #     return(blk)

    # def imgMaker(self,n):           #**建構image
    #     if n==1:
    #         blk=BRepPrimAPI_MakeWedge(gp_Ax2(gp_Pnt(220,-50, 70),dirZ,dirY),240,300,160,120,80,120,80).Shape()
    #     else:
    #         blk=BRepPrimAPI_MakeWedge(gp_Ax2(gp_Pnt(390,-50,-210),dirZ,dirY),240,300,160,120,80,120,80).Shape()
    #         mx =gp_Trsf();  mx.SetRotation(axsY,pi180);
    #         blk.Move(TopLoc_Location(mx))
    #     return(blk)
    # def gripMaker(self):            #**建構gripper
    #     mx=BRepPrimAPI_MakeBox(gp_Pnt(30,-20,0),10,40,100).Shape()
    #     return(mx)
    # def tableMaker(self):            #**建構table
    #     mx=BRepPrimAPI_MakeBox(gp_Pnt(-150,-200,-10),300,400,10).Shape()
    #     return(mx)
    # def objMaker(self,n):           #**建構object
    #     if   n==1: mx=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,-20),dirZ,dirX),20,40).Shape()
    #     elif n==2: mx=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,-20),dirZ,dirX),20,80).Shape()
    #     elif n==3: mx=BRepPrimAPI_MakeBox     (gp_Pnt(-20,-20,-20),40,40,40).Shape()
    #     elif n==4: mx=BRepPrimAPI_MakeBox     (gp_Pnt(-10,-30,-20),20,60,40).Shape()
    #     else:      mx=BRepPrimAPI_MakeSphere  (gp_Pnt(  0,  0,  0),20).Shape()
    #     return(mx)


    def dotMaker(self):              #**建構dots[]
        for i in range(nDot):
            mx =BRepPrimAPI_MakeSphere(gp_Pnt(0,0,0),6).Shape()
            _dots.append(self.canva._display.DisplayColoredShape(mx,'BLACK',update=True))
# def dotUpdate():             #**顯示dots[]
#     n=mm.pDot()
#     for i in range(nDot):
#         obj=_dots[i].GetHandle();
#         if i<n:
#             display.Context.SetDisplayMode(obj,1)
#             display.Context.SetLocation(obj,TopLoc_Location(mm.mxFromP(mm.pDot(i))))
#         else:
#             display.Context.SetDisplayMode(obj,3)
# sTitle=""; sText1=""; sText2=""; sText3=""; sText4="";
# def txtUpdate():             #**文字視窗更新
#     global sTitle,sText1,sText2,sText3,sText4
#     if sTitle!=pp.sTitle: sTitle=pp.sTitle; _uiView.setWindowTitle(pp.sTitle)
#     if sText1!=pp.sText1: sText1=pp.sText1; _uiText1.setText(pp.sText1)
#     if sText2!=pp.sText2: sText2=pp.sText2; _uiText2.setText(pp.sText2)
#     if sText3!=pp.sText3: sText3=pp.sText3; _uiText3.setText(pp.sText3)
#     if sText4!=pp.sText4: sText4=pp.sText4; _uiText4.setText(pp.sText4)

    # def pipe_ON(self,event=None):
    #     pp.pipe=pp.pipeServer(); pp.pipe.start()
    # def pipe_OFF(self,event=None):
    #     pp.pipeEnd=1
    # def exit(self,event=None):
    #     pp.pipeEnd=1; pp.pipe.join(); sys.exit()

