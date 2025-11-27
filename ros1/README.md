# netzsch_instrument_ros1
## Configuration
- Server PC (Windows)
  - Measurement software (GUI)
- Client PC (Ubuntu)
  - Manage auto_exp
     
## Install
Server PC
```
# install labauto
[wsl]
cd \\wsl.localhost\Ubuntu\home\utokyo-user\catkin_ws\src\labauto
python3 -m pip install -e .
```

Install tesseract OCR on Windows
- Download installer (exe)
  - https://github.com/UB-Mannheim/tesseract/wiki
  - Specify installed application path(exe) in the program
- Install python rapper
  ```
  [powershell]
  python3 -m pip install pytesseract
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
