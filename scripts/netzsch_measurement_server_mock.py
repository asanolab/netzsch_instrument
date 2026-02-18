#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import roslibpy
import rospy
import time
from std_msgs.msg import Bool

measure_finished = False
LOG_INTERVAL = 60.0


def measure_finished_cb(msg):
    global measure_finished
    rospy.loginfo(f"/measure_finished received: {msg.data}")
    measure_finished = msg.data


def handle_netzsch_measurement_mock(request, response):
    global measure_finished
    measure_finished = False

    print(f"[roslibpy] Received measurement request: {request}")

    start_time = time.time()
    last_log_time = start_time
    response['message'] = 'during measurement'

    # wait for measure
    while not measure_finished:
        now = time.time()
        # print every 1min
        if now - last_log_time >= LOG_INTERVAL:
            rospy.loginfo("[mock] waiting for /measure_finished ...")
            last_log_time = now

        time.sleep(0.1)

    # return
    response['success'] = True
    response['message'] = 'measurement succeeded'
    print("[roslibpy] measurement succeeded")
    print("[roslibpy] waiting for next service call")

    return True  # must return True to roslibpy when success


# ros
ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()

# subscriber
rospy.init_node("netzsch_measurement_server_mock")
rospy.Subscriber("/measure_finished", Bool, measure_finished_cb)

# Service server
service = roslibpy.Service(ros, '/netzsch_measurement_server_mock', 'netzsch_instrument/NETZSCH_Measurement')
service.advertise(handle_netzsch_measurement_mock)

print("[roslibpy] Service '/netzsch_measurement_server_mock' advertised. Waiting for requests...")


try:
    while ros.is_connected:
        time.sleep(0.1)  # continue to connect
except KeyboardInterrupt:
    print('[roslibpy] Interrupted, shutting down service...')
finally:
    service.unadvertise()
    ros.terminate()
    print('[roslibpy] Disconnected from ROS.')
