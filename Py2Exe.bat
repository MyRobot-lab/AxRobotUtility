call %PROGRAMDATA%\Anaconda3\Scripts\activate.bat %USERPROFILE%\.conda\envs\py36occ173_RoboticArm
%~d0
cd %~dp0\
::chcp 65001
rd /s/q ..\Binary_x64
md ..\Binary_x64
cd ..\Binary_x64
pyinstaller -F ..\Source\AxRobotUtility.py --hidden-import PyQt5.sip --noconsole

:: Copy resource
xcopy ..\Source\img .\dist\img /i/e/d/y
xcopy ..\Source\model .\dist\model /i/e/d/y
xcopy ..\Source\param .\dist\param /i/e/d/y
xcopy ..\Source\program .\dist\program /i/e/d/y
xcopy ..\Source\script .\dist\script /i/e/d/y
xcopy ..\Source\simu\stp .\dist\simu\stp /i/e/d/y