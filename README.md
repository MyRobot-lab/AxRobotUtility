# AxRobotUtility
The GUI control tool for AxRobot system

# AxRobot System Main Components


# Features
- StartUp
- Parameter Viewer
- Jog Control
- Point Editor
- Script Editor
- Motion Tuner
- Upgrade

# Dependencies
- PyQt5
- pythonocc-core 0.17.3
- pywin32
- numpy
- matplotlib
- pyserial
- ipython
- pyinstaller

# Folder Structure

    |-img                # Store icons and images for UI design.
    |-model              # Store motion parameters and robot parameters.
    |-param              # Store servo drive parameters.
    |-program            # Store python files for system connection, servo on/off, motion control and tuning.
    |-script             # Store "motion script file(.ms)", it can be loaded into "Script Editor".
    |-simu               # Contain python files for 3D robot model generation.
    |-ui                 # Store Qt Designer UI files and converted python files.
    |-AxRobotData.py     # AxRobot data module.
    |-AxRobotUtility.py  # AxRobot main module.
    |-def.appcfg         # Default configuration file of AxRobot Utility.
    |-escMotion.py       # Motion control toplayer module.
    |-frmAbout.py        # The handled module of "About" dialog on UI.
    |-frmInformation.py  # The handled module of "Information" page on UI, but now is not used.
    |-frmJogControl.py   # The handled module of "Jog Control" page on UI.
    |-frmMotionTuner.py  # The handled module of "Motion Tuner" page on UI.
    |-frmParamViewer.py  # The handled module of "Parameter Viewer" page on UI.
    |-frmPointEditor.py  # The handled module of "Point Editor" page on UI.
    |-frmScriptEditor.py # The handled module of "Script Editor" page on UI.
    |-frmStartUp.py      # The handled module of "StartUp" page on UI.
    |-frmUpgrade.py      # The handled module of "Upgrade" page on UI.
    |-mathRobot.py       # Motion control mathematics module.
    |-Monitor.py         # Real time status and 3d robot poseture updating.
    |-MotionFunction.py  # Is the threading module and handling events of each function page on UI.
    |-powerON.py         # Handling system startup flow, but not used now.
    |-Py2Exe.bat         # The batch file used to converte to execution file.
    |-PyConsole.bat      # The batch file used to create a command line console.
    |-Run.bat            # The batch file used to bring up AxRobot utility.
    |-Ui2Py.bat          # The batch file used to converte ".ui" files to be ".py" file in "ui" folder.

# Prerequisites
- Windows 7/10 64bits OS installed PC
- AxRobot Controller Module

# Development Environment Setup
1. Download and install Anaconda3 with Python3.7 at link https://www.anaconda.com/distribution/.
2. Add channels to .condarc file, normally it can be found at path below.
   - Windows：C:\users\username\.condarc
   - Linux：/home/username/.condarc
   
   Open .condarc file and modify the content as below.
   
        channels:
          - tpaviot
          - oce
          - 3dhubs
          - dlr-sc
          - conda-forge
          - pythonocc
          - defaults

3. There are two ways to create python environment, it is recommended to use first way to avoid package incompatibility issues.

   - Import env.yml file to create new python environment.


   or

   - Use Anaconda Navigator to create a new virtual environment for Python3.6, then install related packages manually with conda, please following the ordering as below.

          conda install -c conda-forge -c dlr-sc -c pythonocc -c oce pythonocc-core==0.17.3
          conda install pywin32
          conda install numpy
          conda install matplotlib
          conda install pyserial
          conda install -c conda-forge pyside2
          conda install ipython
          conda install -c anaconda opencv
          conda install -c anaconda cherrypy
          conda install -c conda-forge pyinstaller
   
