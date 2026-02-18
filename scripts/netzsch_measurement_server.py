#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import roslibpy
import sys
import time
import yaml
from netzsch_instrument.gui_control_netzsch_measurement import GUIControl_NETZSCH_Measurement

tma_gui_controller = GUIControl_NETZSCH_Measurement()

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
        client_ip = conf['ros_client']['ip']
        client_port = conf['ros_client']['port']
except Exception as e:
    print(f"fail to load YAML file: {e}")
    sys.exit(1)


def handle_netzsch_measurement(request, response):
    print(f"[roslibpy] Received measurement request: {request}")

    # start software
    print('[roslibpy] starting software')
    response['message'] = 'starting software'
    try:
        tma_gui_controller.start_software()
    except Exception as e:
        print(e)
        response['success'] = False
        return False

    # set method
    print('[roslibpy] setting method')
    response['message'] = 'setting method'
    try:
        tma_gui_controller.set_method(
            method_file_name = method['file_name']
        )
    except Exception as e:
        print(e)
        response['success'] = False
        return False

    # input method
    print('[roslibpy] inputting parameters')
    response['message'] = 'inputting parameters'
    try:
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
    except Exception as e:
        print(e)
        response['success'] = False
        return False

    # measure sample
    print('[roslibpy] measuring sample')
    response['message'] = 'measuring sample'
    try:
        tma_gui_controller.measure()
    except Exception as e:
        print(e)
        response['success'] = False
        return False

    # close software
    print('[roslibpy] closing software')
    response['message'] = 'closing software'
    try:
        tma_gui_controller.close_software()
    except Exception as e:
        print(e)
        response['success'] = False
        return False

    # return
    response['success'] = True
    response['message'] = 'measurement succeeded'
    print("[roslibpy] measurement succeeded")
    print("[roslibpy] waiting for next service call")

    return True  # must return True to roslibpy when success


# ros
ros = roslibpy.Ros(host=client_ip, port=client_port)
ros.run()

# Service server
service = roslibpy.Service(ros, '/netzsch_measurement_server', 'netzsch_instrument/NETZSCH_Measurement')
service.advertise(handle_netzsch_measurement)

print("[roslibpy] Service '/netzsch_measurement_server' advertised. Waiting for requests...")


try:
    while ros.is_connected:
        time.sleep(0.1)  # continue to connect
except KeyboardInterrupt:
    print('[roslibpy] Interrupted, shutting down service...')
finally:
    service.unadvertise()
    ros.terminate()
    print('[roslibpy] Disconnected from ROS.')
