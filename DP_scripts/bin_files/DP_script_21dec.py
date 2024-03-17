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



class RobotMain(object):
    """Robot Main Class"""
    def __init__(self, robot, **kwargs):
        self.alive = True
        self._arm = robot
        self._tcp_speed = 100
        self._tcp_acc = 2000
        self._angle_speed = 20
        self._angle_acc = 500
        self._vars = {}
        self._funcs = {}
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
    def arm(self):
        return self._arm

    @property
    def VARS(self):
        return self._vars

    @property
    def FUNCS(self):
        return self._funcs

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
            self._tcp_acc = 200
            self._tcp_speed = 20
            for i in range(int(2)):
                if not self.is_alive:
                    break
                code = self._arm.set_servo_angle(angle=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_position(*[87.0, 200.0, 154.2, 180.0, 0.0, 0.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_position(*[-80.0, 200.0, 60.0, 180.0, 0.0, 0.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_position(*[-80.0, 200.0, 60.0, 180.0, 0.0, -43.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-12.9, 162.8, 60.0, 180.0, 0.0, -45.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-80.0, 320.0, 60.0, 180.0, 0.0, -54.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[15.2, 238.2, 60.0, 180.0, 0.0, -61.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[7.5, 320.0, 60.0, 180.0, 0.0, -67.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[150.0, 320.0, 60.0, 180.0, 0.0, -89.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[240.0, 320.0, 60.0, 180.0, 0.0, -107.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[320.0, 270.0, 60.0, 180.0, 0.0, -123.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[375.0, 200.0, 60.0, 180.0, 0.0, -140.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[395.0, 92.0, 60.0, 180.0, 0.0, -162.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[405.0, 0.0, 60.0, 180.0, 0.0, 177.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[395.0, -90.0, 60.0, 180.0, 0.0, 156.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[375.0, -180.0, 60.0, 180.0, 0.0, 138.9], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[320.0, -245.0, 60.0, 180.0, 0.0, 120.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[240.0, -280.0, 60.0, 180.0, 0.0, 105.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[150.0, -280.0, 60.0, 180.0, 0.0, 87.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[30.0, -280.0, 60.0, 180.0, 0.0, 65.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-60.0, -220.0, 60.0, 180.0, 0.0, 44.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-16.5, -182.1, 60.0, 180.0, 0.0, 44.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-40.0, -159.6, 60.0, 180.0, 0.0, 39.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-28.9, -137.4, 60.0, 180.0, 0.0, 34.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(3)

                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-28.9, -181.2, 192.7, 180.0, 0.0, 34.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-40.5, -198.6, 190.0, 174.6, 24.2, 46.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-6.5, -166.5, 179.3, 178.6, 27.9, 44.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[55.0, -243.9, 200.2, 170.6, 27.4, 66.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[205.1, -219.5, 195.3, 176.5, 31.2, 98.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[299.3, -175.3, 228.4, 170.9, 36.8, 127.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[343.6, -117.0, 228.4, 178.2, 37.9, 137.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[363.4, -46.2, 232.4, -178.0, 40.2, 156.9], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[366.3, 20.9, 232.4, -177.9, 40.2, 175.9], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[366.3, 124.6, 232.4, -155.8, 38.1, -160.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[290.3, 191.1, 232.4, -169.5, 40.2, -133.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[237.0, 258.2, 232.4, -165.6, 36.8, -113.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[142.2, 291.0, 229.3, -163.4, 31.5, -90.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[68.7, 282.1, 229.3, -163.4, 31.5, -78.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-35.7, 261.4, 229.3, -163.4, 31.5, -60.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-65.6, 208.0, 229.3, -163.4, 31.5, -48.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(1)
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_pause_time(4)
                if not self._check_code(code, 'set_pause_time'):
                    return
                code = self._arm.set_position(*[-5.4, 219.2, 226.6, -151.1, 19.7, -41.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_position(*[69.8, 206.6, 221.9, -148.5, -0.4, -38.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_position(*[132.1, 168.5, 216.2, -159.1, -16.3, -33.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
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
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    else:
        try:
            from configparser import ConfigParser

            parser = ConfigParser()
            parser.read('../example/wrapper/robot.conf')
            ip = parser.get('xArm', 'ip')
        except:
            ip = input('Please input the xArm ip address:')
            if not ip:
                print('input error, exit')
                sys.exit(1)
    arm = XArmAPI(ip)
    robot_main = RobotMain(arm)
    robot_main.run()




