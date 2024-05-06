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

import time
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
        self._tcp_speed = 200
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

    def move_arm_and_capture_images(self, h_cam, mem_ptr, angles):
        code = self._arm.set_servo_angle(angle=angles, speed=self._angle_speed,
                                         mvacc=self._angle_acc, wait=True, radius=0.0)
        if not self._check_code(code, 'set_servo_angle'):
            return False

        for _ in range(20):
            # Timer for stabilizing camera
            time.sleep(3)
            # Function to create and save image
            capture_and_save_image(h_cam, mem_ptr, 1920, 1080)
            time.sleep(3)


        return True

    def run_sequence(self, h_cam, mem_ptr):
        sequences = [
            [23.8, 62.9, 100.9, 0.5, 38.7, 105.8],
            [4.4, 37.2, 89.8, 39.6, 57.7, 63.3],
            [-5, 34.7, 95.5, 46.5, 73.4, 58],
            [1.3, 45.1, 84.8, 34, 45.4, 58.1],
            [7.5, 52.9, 86.1, 14.4, 33.8, 77.8]
        ]

        for sequence in sequences:
            if not self.is_alive:
                break
            if not self.move_arm_and_capture_images(h_cam, mem_ptr, sequence):
                return

    # Robot Main Run
    def run(self):
        h_cam, mem_ptr, mem_id = initialize_camera()
        try:
            self._arm.reset()

            i = int(1)
            code = self._arm.set_servo_angle(angle=[58.3, 42.0, 66.6, 1.4, 25.0, 139.4], speed=self._angle_speed,
                                             mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            #turning on rolling plate
            code = self._arm.set_cgpio_digital(0, 1, delay_sec=0)
            if not self._check_code(code, 'set_cgpio_digital'):
                return

            robot_main.run_sequence(h_cam, mem_ptr)
            #turning off rolling plate
            code = self._arm.set_cgpio_digital(0, 0, delay_sec=0)
            if not self._check_code(code, 'set_cgpio_digital'):
                return
            code = self._arm.set_servo_angle(angle=[58.3, 42.0, 66.6, 1.4, 25.0, 139.4], speed=self._angle_speed,
                                             mvacc=self._angle_acc, wait=True, radius=0.0)
            if not self._check_code(code, 'set_servo_angle'):
                return
            self._arm.reset()

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




