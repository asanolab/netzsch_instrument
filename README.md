# netzsch_ros

## install
install labauto on WSL
```
cd \\wsl.localhost\Ubuntu\home\utokyo-user\catkin_ws\src\labauto
python3 -m pip install -e .
```

client PC (Ubuntuなど)
```
roslaunch rosbridge_server rosbridge_websocket.launch  # roslibでの通信に必要
```

gui PC (windows)
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