# netzsch_instrument
Software for controlling NETZSCH instrument using ROS framework

## Configuration
- Server PC (Windows)
  - Measurement software (GUI)
- Client PC (Ubuntu)
  - Manage auto_exp

## Install
### Server PC
**Install python modules**
```
[powershell]
python3 -m pip install pyautogui
cd labautopy
python3 -m pip install -e .
```

**netzsch_instrumentへのpythonパスの追加**  
- 設定ファイルの確認(.bashrcに相当)
  ```
  echo $PROFILE
  -> C:\Users\user\Documents\PowerShell\Microsoft.PowerShell_profile.ps1
  ```
- ファイルなければ作る
  ```
  New-Item -ItemType File -Path $PROFILE -Force
  ```
- 中にパスを書く
  ```
  $env:PYTHONPATH = "\\wsl.localhost\Ubuntu\home\user\catkin_ws\netzsch_instrument\src;" + $env:PYTHONPATH
  的な感じ
  ```
- powershellを再起動する


**Install tesseract OCR on Windows**
- Download installer (exe)
  - https://github.com/UB-Mannheim/tesseract/wiki
  - Specify installed application path(exe) in the program
- Install python rapper
  ```
  [powershell]
  python3 -m pip install pytesseract
  ```

## Build
```
catkin bt
```

## Usage
client PC
```
roslaunch rosbridge_server rosbridge_websocket.launch  # roslibでの通信に必要
```

server PC
```
[terminal1] wsl
roscore

[terminal2] powershell
cd \\wsl.localhost\Ubuntu
cd 'path_to_pkg'\netzsch_ros\scripts_powershell
python3 .\netzsch_measurement_server.py ..\config\netzsch_measurement_config.yaml


# ターミナルで直接 ```.\netzsch_measurement_server_thread.py```とすると,pythonが別端末で立ち上がりエラー確認できない
```


外部PC か wslで
```
rosservice call /netzsch_measurement_server "sample_id: 0 sample_thickness: 0.3"
```
