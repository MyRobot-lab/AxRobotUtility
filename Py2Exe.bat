call %PROGRAMDATA%\Anaconda3\Scripts\activate.bat %USERPROFILE%\.conda\envs\py36occ173_RoboticArm
%~d0
cd %~dp0\
::chcp 65001
rd /s/q ..\Binary_x64
md ..\Binary_x64
cd ..\Binary_x64
pyinstaller -F ..\AxRobotUtility\AxRobotUtility.py --hidden-import PyQt5.sip --noconsole

:: Copy resource
xcopy ..\AxRobotUtility\img .\dist\img /i/e/d/y
xcopy ..\AxRobotUtility\model .\dist\model /i/e/d/y
xcopy ..\AxRobotUtility\param .\dist\param /i/e/d/y
xcopy ..\AxRobotUtility\program .\dist\program /i/e/d/y
xcopy ..\AxRobotUtility\script .\dist\script /i/e/d/y
xcopy ..\AxRobotUtility\simu\stp .\dist\simu\stp /i/e/d/y