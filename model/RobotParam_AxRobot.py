
#**********************************************************
# RobotParam_AxRobot.py
#**********************************************************

#URDF模型  [  x,   y,  z,   Rx,  Ry,  Rz,Dist,Mass,  mx,my,mz]
modelURDF=[[  0.,  0.,220., 0.,  0.,  1., 0.5, 6.3,  0.,0.,0.],
           [  0.,  0.,155., 0.,  1.,  0., 0.5, 8.4,  0.,0.,0.],
           [  0.,  0.,288., 0.,  0.,  1., 0.5, 6.7,  0.,0.,0.],
           [  0.,  0.,137., 0.,  1.,  0., 0.5, 5.3,  0.,0.,0.],
           [  0.,  0.,245., 0.,  0.,  1., 0.5, 3.4,  0.,0.,0.],
           [  0.,  0.,180., 0.,  1.,  0., 0.5, 3.0,  0.,0.,0.],
           [  0.,  0., 80., 0.,  0.,  1., 0.5, 2.3,  0.,0.,0.]]
modelAxis=7                                          #**設置機械手軸數
nAxis=modelAxis

#馬達參數   [ticks   max  min deg/s dir]
modelMotor=[[360000, 180,-180, 180, 1],
            [360000, 110,-110, 180, 1],
            [360000, 180,-180, 180, 1],
            [360000, 110,-110, 180, 1],
            [360000, 180,-180, 180, 1],
            [360000, 110,-110, 180, 1],
            [360000, 180,-180, 180, 1],
            [360000, 360,-360, 180, 1]]
                                        
modelGainG= [0.04,0.04,0.10,0.1,1.,1.,0.] #**設置重力增益
modelGainM= [0.05, 0.05, 0.3, 0.3,4.,5.,0.] #**設置慣量增益
modelBiasM= [0.,  0.,  0., 0.,0.,  0.,0.] #**設置慣量零點

modelZero = ["joint",0,0,0,0,0,0,0]
modelBase = ["world",0,0,0,0,0,0,0]
modelWork = ["world",0,0,0,0,0,0,0]
modelTool = ["robot",0,0,0,0,0,0,0]