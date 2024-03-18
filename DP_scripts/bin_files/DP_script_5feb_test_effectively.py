#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2022, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
# Notice
#   1. Changes to this file on Studio will not be preserved
#   2. The next conversion will overwrite the file with the same name
#
# xArm-Python-SDK: https://github.com/xArm-Developer/xArm-Python-SDK
#   1. git clone git@github.com:xArm-Developer/xArm-Python-SDK.git
#   2. cd xArm-Python-SDK
#   3. python setup.py install
"""
import winsound
import sys
import math
import time
import queue
import datetime
import random
import traceback
import threading
from xarm import version
from xarm.wrapper import XArmAPI
from pics_camera import initialize_camera, close_camera, capture_and_save_image
from meshing_script import meshing_proces


class RobotMain(object):
    """Robot Main Class"""
    def __init__(self, robot, **kwargs):
        self.alive = True
        self._arm = robot
        self._tcp_speed = 100
        self._tcp_acc = 2000
        self._angle_speed = 20
        self._angle_acc = 500
        self._variables = {}
        self._robot_init()

    # Robot init
    def _robot_init(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)
        self._arm.register_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.register_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'register_count_changed_callback'):
            self._arm.register_count_changed_callback(self._count_changed_callback)

    # Register error/warn changed callback
    def _error_warn_changed_callback(self, data):
        if data and data['error_code'] != 0:
            self.alive = False
            self.pprint('err={}, quit'.format(data['error_code']))
            self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)

    # Register state changed callback
    def _state_changed_callback(self, data):
        if data and data['state'] == 4:
            self.alive = False
            self.pprint('state=4, quit')
            self._arm.release_state_changed_callback(self._state_changed_callback)

    # Register count changed callback
    def _count_changed_callback(self, data):
        if self.is_alive:
            self.pprint('counter val: {}'.format(data['count']))

    def _check_code(self, code, label):
        if not self.is_alive or code != 0:
            self.alive = False
            ret1 = self._arm.get_state()
            ret2 = self._arm.get_err_warn_code()
            self.pprint('{}, code={}, connected={}, state={}, error={}, ret1={}. ret2={}'.format(label, code, self._arm.connected, self._arm.state, self._arm.error_code, ret1, ret2))
        return self.is_alive

    @staticmethod
    def pprint(*args, **kwargs):
        try:
            stack_tuple = traceback.extract_stack(limit=2)[0]
            print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
        except:
            print(*args, **kwargs)

    @property
    def is_alive(self):
        if self.alive and self._arm.connected and self._arm.error_code == 0:
            if self._arm.state == 5:
                cnt = 0
                while self._arm.state == 5 and cnt < 5:
                    cnt += 1
                    time.sleep(0.1)
            return self._arm.state < 4
        else:
            return False

    # Robot Main Run
    def run(self):
        h_cam, mem_ptr, mem_id = initialize_camera()
        try:
            # self._tcp_acc = 500
            # self._tcp_speed = 100
            self._tcp_acc = 20
            self._tcp_speed = 10
            for i in range(int(1)):
                if not self.is_alive:
                    break
                # Define a list of target positions
                target_positions = [
                    # first circle positions
                    [87.0, 0.0, 166.5, 180.0, 0.0, 0.0],
                    [116.2, 0.0, 166.5, 180.0, 0.0, 0.0],
                    [124.7, 54.4, 166.5, 180.0, 0.0, -20.1],
                    [124.7, 83.5, 166.5, 180.0, 0.0, -31.2],
                    [124.7, 115.6, 166.5, 180.0, 0.0, -40.7],
                    [124.7, 137.4, 175, 180.0, 0.0, -47.7],
                    [98.4, 128.7, 175, 180.0, 0.0, -40.1],
                    [65.3, 202.4, 175, 180.0, 0.0, -48.4],
                    [92.3, 220.8, 175, 180.0, 0.0, -54.7],
                    [129.5, 227.0, 175, 180.0, 0.0, -62.0],
                    [163.5, 253.3, 175, 180.0, 0.0, -71.3],
                    [217.4, 255.9, 175, 180.0, 0.0, -82.4],
                    [268.6, 266.7, 175, 180.0, 0.0, -94.2],
                    [339.2, 245.9, 175, 180.0, 0.0, -111.0],
                    [363.9, 245.9, 175, 180.0, 0.0, -115.7],
                    [375.8, 189.8, 175, 180.0, 0.0, -127.6],
                    [406.6, 169.1, 175, 180.0, 0.0, -135.6],
                    [426.7, 108.8, 175.5, 180.0, 0.0, -150.6],
                    [426.7, 91.4, 175.5, 180.0, 0.0, -157.9],
                    [433.7, 54.7, 175.9, 180.0, 0.0, -169.5],
                    [433.7, 39.0, 175.9, 180.0, 0.0, -173.5],
                    [433.7, 8.5, 175.9, 180.0, 0.0, 176.1],
                    [422.0, -23.8, 175.9, 180.0, 0.0, 162.8],
                    [422.0, -61.2, 175.9, 180.0, 0.0, 151.0],
                    [418.8, -80.7, 175.9, 180.0, 0.0, 144.1],
                    [418.8, -120.7, 175.9, 180.0, 0.0, 137.1],
                    [380.9, -162.2, 175.9, 180.0, 0.0, 120.8],
                    [347.9, -202.2, 175.9, 180.0, 0.0, 108.8],
                    [310.0, -250.6, 175.9, 180.0, 0.0, 98.0],
                    [276.5, -305.6, 175.9, 180.0, 0.0, 88.7],
                    [220.0, -292.0, 175.9, 180.0, 0.0, 78.0],
                    [158.4, -284.5, 175.9, 180.0, 0.0, 65.2],
                    [125.0, -265.9, 175.9, 180.0, 0.0, 58.3],
                    [83.0, -245.9, 175.9, 180.0, 0.0, 50.3],
                    [34.0, -200.0, 175.9, 180.0, 0.0, 40.0],
                    [12.8, -158.6, 180.9, 180.0, 0.0, 29.9],
                    [82.0, -82.0, 180.9, 180.0, 0.0, 24.0],

                    # second circle positions
                    [39.9, -121.4, 200.9, 180.0, 0.0, 26.0],
                    [83.0, -245.9, 200.9, 180.0, 0.0, 50.3],
                    [158.4, -284.5, 200.9, 180.0, 0.0, 65.2],
                    [276.5, -305.6, 200.9, 180.0, 0.0, 88.7],
                    [347.9, -202.2, 200.9, 180.0, 0.0, 108.8],
                    [418.8, -120.7, 200.9, 180.0, 0.0, 137.1],
                    [422.0, -61.2, 200.9, 180.0, 0.0, 151.0],
                    [433.7, 8.5, 200.9, 180.0, 0.0, 176.1],
                    [426.7, 108.8, 200.5, 180.0, 0.0, -150.6],
                    [406.6, 169.1, 200.5, 180.0, 0.0, -135.6],
                    [363.9, 245.9, 200.5, 180.0, 0.0, -115.7],
                    [268.6, 266.7, 200.5, 180.0, 0.0, -94.2],
                    [163.5, 253.3, 200.5, 180.0, 0.0, -71.3],
                    [65.3, 202.4, 200.5, 180.0, 0.0, -48.4],
                    [98.4, 128.7, 200.5, 180.0, 0.0, -40.1],
                    [124.7, 137.4, 200.5, 180.0, 0.0, -47.7],
                    [116.2, 0.0, 200.5, 180.0, 0.0, 0.0],
                    [87.0, 0.0, 200.5, 180.0, 0.0, 0.0],
                    [116.2, 0.0, 200.5, 180.0, 0.0, 0.0],
                ]

                higher_target_positions = [
                    [0.0, -16.3, 7.8, 0.0, 40.5, 0.0],
                    [0.0, -6.4, 15.4, 0.0, 38.2, 0.0],
                    [35.9, -8.0, 38.3, 34.4, 62.1, 62.2],
                    [38.9, 2.8, 53.1, 44.0, 54.0, 74.1],
                    [32.3, 17.0, 71.4, 36.5, 18.2, 111.6],
                    [23.6, 32.2, 92.2, 6.8, 20.0, 153.6],
                    [6.2, 23.0, 83.9, -7.1, 7.9, 184.9],
                    [-19.5, 32.6, 92.0, 51.4, 20.6, 145.5],
                    [-33.1, 41.0, 94.8, 29.0, 22.6, 181.9],
                    [-41.4, 29.3, 78.0, 10.8, 19.6, 211.1],
                    [-59.5, 14.4, 55.9, 28.3, 13.6, 197.4],
                    [-96.3, 7.0, 48.1, 38.0, 16.8, 183.0],
                    [-72.6, -28.7, 18.4, -18.0, 16.5, 259.8],
                    # end of third circle - higher positions
                    [-96.3, 7.0, 48.1, 38.0, 16.8, 183.0],
                    [-59.5, 14.4, 56.9, 28.3, 11.6, 199.4],
                    [-59.5, 14.4, 55.9, 28.3, 13.6, 197.4],
                    [-41.4, 29.3, 78.0, 10.8, 19.6, 211.1],
                    [-33.1, 41.0, 94.8, 29.0, 22.6, 181.9],
                    [-19.5, 39.3, 92.0, 51.4, 20.6, 149.5],
                    [6.2, 33.9, 83.9, -7.1, 7.9, 184.9],
                    [23.6, 39.4, 92.2, 6.8, 20.0, 153.6],
                    [32.3, 25.2, 71.4, 36.5, 18.2, 111.6],
                    [38.9, 11.1, 53.1, 44.0, 54.0, 74.1],
                    [35.9, 0.4, 38.3, 34.4, 62.1, 56.2],
                    [0.0, -6.4, 15.4, 0.0, 38.2, 0.0],

                    #repeat for another pictures

                    [0.0, -16.3, 7.8, 0.0, 40.5, 0.0],
                    [0.0, -6.4, 15.4, 0.0, 38.2, 0.0],
                    [35.9, -8.0, 38.3, 34.4, 62.1, 62.2],
                    [38.9, 2.8, 53.1, 44.0, 54.0, 74.1],
                    [32.3, 17.0, 71.4, 36.5, 18.2, 111.6],
                    [23.6, 32.2, 92.2, 6.8, 20.0, 153.6],
                    [6.2, 23.0, 83.9, -7.1, 7.9, 184.9],
                    [-19.5, 32.6, 92.0, 51.4, 20.6, 145.5],
                    [-33.1, 41.0, 94.8, 29.0, 22.6, 181.9],
                    [-41.4, 29.3, 78.0, 10.8, 19.6, 211.1],
                    [-59.5, 14.4, 55.9, 28.3, 13.6, 197.4],
                    [-96.3, 7.0, 48.1, 38.0, 16.8, 183.0],
                    [-72.6, -28.7, 18.4, -18.0, 16.5, 259.8],
                    # end of fifth circle - higher positions
                    [-96.3, 7.0, 48.1, 38.0, 16.8, 183.0],
                    [-59.5, 14.4, 56.9, 28.3, 11.6, 199.4],
                    [-59.5, 14.4, 55.9, 28.3, 13.6, 197.4],
                    [-41.4, 29.3, 78.0, 10.8, 19.6, 211.1],
                    [-33.1, 41.0, 94.8, 29.0, 22.6, 181.9],
                    [-19.5, 39.3, 92.0, 51.4, 20.6, 149.5],
                    [6.2, 33.9, 83.9, -7.1, 7.9, 184.9],
                    [23.6, 39.4, 92.2, 6.8, 20.0, 153.6],
                    [32.3, 25.2, 71.4, 36.5, 18.2, 111.6],
                    [38.9, 11.1, 53.1, 44.0, 54.0, 74.1],
                    [35.9, 0.4, 38.3, 34.4, 62.1, 56.2],
                    [0.0, -6.4, 15.4, 0.0, 38.2, 0.0],

                ]

                # start on null position
                code = self._arm.set_servo_angle(angle=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return

                # Loop through the target positions and set them using the arm
                for position in target_positions:
                    code = self._arm.set_position(*position, speed=self._tcp_speed,
                                                  mvacc=self._tcp_acc, radius=0.0, wait=True)
                    if not self._check_code(code, 'set_position'):
                        return

                    #timer for stabilizating camera
                    code = self._arm.set_pause_time(2)
                    if not self._check_code(code, 'set_pause_time'):
                        return
                    #function to create and save image
                    capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                    code = self._arm.set_pause_time(1)
                    if not self._check_code(code, 'set_pause_time'):
                        return

                # Loop through the target angles for the higher circle and set them using the arm
                for angle in higher_target_positions:
                    code = self._arm.set_servo_angle(angle=angle, speed=self._angle_speed,
                                                     mvacc=self._angle_acc, wait=True, radius=0.0)
                    if not self._check_code(code, 'set_servo_angle'):
                        return

                    # timer for stabilizating camera
                    code = self._arm.set_pause_time(5)
                    if not self._check_code(code, 'set_pause_time'):
                        return
                    # function to create and save image
                    capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                    code = self._arm.set_pause_time(5)
                    if not self._check_code(code, 'set_pause_time'):
                        return

                # end of shooting positions
                code = self._arm.set_servo_angle(angle=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return

        except Exception as e:
            self.pprint('MainException: {}'.format(e))
        self.alive = False

        # camera close
        close_camera(h_cam, mem_ptr, mem_id)

        self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.release_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'release_count_changed_callback'):
            self._arm.release_count_changed_callback(self._count_changed_callback)


if __name__ == '__main__':
    RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
    arm = XArmAPI('192.168.1.152', baud_checkset=False)
    robot_main = RobotMain(arm)
    robot_main.run()
    meshing_proces()








#
# if __name__ == '__main__':
#     RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
#     if len(sys.argv) >= 2:
#         ip = sys.argv[1]
#     else:
#         try:
#             from configparser import ConfigParser
#
#             parser = ConfigParser()
#             parser.read('../example/wrapper/robot.conf')
#             ip = parser.get('xArm', 'ip')
#         except:
#             ip = input('Please input the xArm ip address:')
#             if not ip:
#                 print('input error, exit')
#                 sys.exit(1)
#     arm = XArmAPI(ip)
#     robot_main = RobotMain(arm)
#     robot_main.run()




