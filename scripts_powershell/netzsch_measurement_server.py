#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import roslibpy
import sys
import time
import yaml
from gui_control_netzsch_measurement import GUIControl_NETZSCH_Measurement

tma_gui_controller = GUIControl_NETZSCH_Measurement()
client_ip = '192.168.0.21'  # manager desktop PC

# load exp config
if len(sys.argv) < 2:
    print("Usage: python3 ./netzsch_measurement_server.py <yaml file path>")
    sys.exit(1)

yaml_path = sys.argv[1]

# load yaml
try:
    with open(yaml_path, 'r') as f:
        conf = yaml.safe_load(f)
        method = conf['method']
        method_p = conf['method']['param']
except Exception as e:
    print(f"fail to load YAML file: {e}")
    sys.exit(1)


def handle_netzsch_measurement(request, response):
    print(f"Received measurhement request: {request}")

    # measurement
    if request['sample_id'] == 0:
        print('starting software')
        tma_gui_controller.start_software()
        response['message'] = 'starting software'
    else:
        print('skip starting software')

    print('setting method')
    tma_gui_controller.set_method(
        method_file_name = method['file_name']
    )
    response['message'] = 'setting method'

    print('inputting parameters')
    tma_gui_controller.input_parameters(
        lab              = method_p['lab'],
        project          = method_p['project'],
        measurer         = method_p['measurer'],
        sample_id        = request['sample_id'],
        sample_name      = method_p['sample_name'],
        sample_length    = method_p['sample_length'],
        sample_width     = method_p['sample_width'],
        sample_thickness = request['sample_thickness'],
        sample_material  = method_p['sample_material'],
        result_file_name = method_p['result_file_name']
    )
    response['message'] = 'inputting parameters'

    print('measuring sample')
    tma_gui_controller.measure()
    response['message'] = 'measuring sample'

    print('closing software')
    tma_gui_controller.close_software()
    response['message'] = 'closing software'

    time.sleep(1.0)

    response['success'] = True
    response['message'] = 'measurement succeeded'
    print("Measurement succeeded")
    return True

# ros
ros = roslibpy.Ros(host=client_ip, port=9090)
ros.run()

# Service server
service = roslibpy.Service(ros, '/netzsch_measurement_server', 'auto_tma/NETZSCH_Measurement')
service.advertise(handle_netzsch_measurement)

print("Service '/netzsch_measurement_server' advertised. Waiting for requests...")


try:
    while ros.is_connected:
        time.sleep(0.1)  # continue to connect
except KeyboardInterrupt:
    print('Interrupted, shutting down servece...')
finally:
    service.unadvertise()
    ros.terminate()
    print('Disconnected from ROS.')
