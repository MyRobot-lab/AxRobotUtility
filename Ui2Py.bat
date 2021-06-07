call %PROGRAMDATA%\Anaconda3\Scripts\activate.bat %USERPROFILE%\.conda\envs\py36occ173_RoboticArm
%~d0
cd %~dp0\
::chcp 65001
call pyuic5 ./ui/AxRobotUtility.ui -o ./ui/AxRobotUtilityUi.py
call pyuic5 ./ui/frmStartUp.ui -o ./ui/frmStartUpUi.py
call pyuic5 ./ui/frmParamViewer.ui -o ./ui/frmParamViewerUi.py
call pyuic5 ./ui/frmJogControl.ui -o ./ui/frmJogControlUi.py
call pyuic5 ./ui/frmPointEditor.ui -o ./ui/frmPointEditorUi.py
call pyuic5 ./ui/frmScriptEditor.ui -o ./ui/frmScriptEditorUi.py
call pyuic5 ./ui/frmMotionTuner.ui -o ./ui/frmMotionTunerUi.py
call pyuic5 ./ui/frmUpgrade.ui -o ./ui/frmUpgradeUi.py
call pyuic5 ./ui/frmInformation.ui -o ./ui/frmInformationUi.py
call pyuic5 ./ui/frmAbout.ui -o ./ui/frmAboutUi.py

