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
            self._tcp_acc = 500
            self._tcp_speed = 100
            for i in range(int(1)):
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

                #start shooting photos
                code = self._arm.set_position(*[-120.2, 236.0, 120.0, 180.0, 0.0, -43.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-183.2, 285.1, 120.0, 180.0, 0.0, -43.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-118.9, 321.7, 120.0, 180.0, 0.0, -54.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-78.6, 334.8, 120.0, 180.0, 0.0, -60.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=False)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-21.7, 341.3, 120.0, 180.0, 0.0, -66.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[36.6, 356.3, 120.0, 180.0, 0.0, -75.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[76.0, 366.3, 120.0, 180.0, 0.0, -82.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[100.9, 366.3, 120.0, 180.0, 0.0, -85.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[119.7, 366.3, 120.0, 180.0, 0.0, -88.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[157.2, 366.3, 120.0, 180.0, 0.0, -94.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[190.7, 366.3, 120.0, 180.0, 0.0, -101.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[234.0, 328.3, 120.0, 180.0, 0.0, -106.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[264.8, 306.8, 120.0, 180.0, 0.0, -114.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[279.2, 303.8, 120.0, 180.0, 0.0, -117.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[304.4, 289.9, 120.0, 180.0, 0.0, -120.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[323.5, 270.2, 120.0, 180.0, 0.0, -125.9], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[357.4, 235.9, 120.0, 180.0, 0.0, -134.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[374.8, 199.9, 120.0, 180.0, 0.0, -142.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_position(*[401.9, 134.0, 120.0, 180.0, 0.0, -156.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[419.0, 70.6, 120.0, 180.0, 0.0, -170.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[425.0, 48.3, 120.0, 180.0, 0.0, -175.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[427.0, 15.2, 120.0, 180.0, 0.0, 178.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[428.1, -23.8, 120.0, 180.0, 0.0, 169.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[423.9, -64.4, 120.0, 180.0, 0.0, 159.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[396.2, -129.6, 120.0, 180.0, 0.0, 145.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[377.3, -148.0, 120.0, 180.0, 0.0, 141.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[368.3, -179.9, 120.0, 180.0, 0.0, 134.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[357.3, -210.9, 120.0, 180.0, 0.0, 128.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[334.9, -240.9, 120.0, 180.0, 0.0, 121.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[301.4, -263.6, 120.0, 180.0, 0.0, 113.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[256.2, -286.6, 120.0, 180.0, 0.0, 107.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[199.7, -286.6, 120.0, 180.0, 0.0, 95.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[167.6, -286.6, 120.0, 180.0, 0.0, 87.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[129.0, -283.2, 120.0, 180.0, 0.0, 80.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[72.9, -286.6, 120.0, 180.0, 0.0, 69.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-13.3, -286.6, 120.0, 180.0, 0.0, 55.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-69.7, -256.7, 120.0, 180.0, 0.0, 44.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-60.3, -189.5, 120.0, 180.0, 0.0, 37.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-16.2, -137.8, 120.0, 180.0, 0.0, 35.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[26.2, -137.8, 120.0, 180.0, 0.0, 45.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[26.2, -137.8, 120.3, 180.0, 0.0, 44.2], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-25.5, -120.8, 120.6, 180.0, 0.0, 29.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-71.6, -176.9, 120.6, 180.0, 0.0, 32.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-147.5, -246.1, 120.6, 180.0, 0.0, 35.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-94.4, -246.1, 120.6, 180.0, 0.0, 37.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[10.7, -246.1, 120.6, 180.0, 0.0, 54.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[145.2, -286.6, 120.0, 180.0, 0.0, 82.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[204.4, -286.6, 120.0, 180.0, 0.0, 93.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[267.4, -270.9, 120.0, 180.0, 0.0, 107.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[324.8, -232.8, 120.0, 180.0, 0.0, 121.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[379.8, -146.1, 120.0, 180.0, 0.0, 142.0], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[396.3, -99.6, 120.0, 180.0, 0.0, 153.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[420.7, -56.9, 120.0, 180.0, 0.0, 162.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[420.7, -1.4, 120.0, 180.0, 0.0, 175.6], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[420.7, 68.3, 120.0, 180.0, 0.0, -170.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[385.5, 172.8, 120.0, 180.0, 0.0, -149.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[345.2, 249.5, 120.0, 180.0, 0.0, -133.1], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[307.8, 289.4, 120.0, 180.0, 0.0, -121.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[256.9, 322.5, 120.0, 180.0, 0.0, -112.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[208.2, 322.5, 120.0, 180.0, 0.0, -104.5], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[96.4, 322.5, 120.0, 180.0, 0.0, -84.3], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[29.8, 322.5, 120.0, 180.0, 0.0, -73.8], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-35.8, 308.7, 120.0, 180.0, 0.0, -62.9], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-112.0, 283.9, 120.0, 180.0, 0.0, -51.4], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-156.2, 246.1, 120.0, 180.0, 0.0, -43.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-115.2, 224.3, 120.0, 180.0, 0.0, -43.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_position(*[-59.9, 189.1, 120.0, 180.0, 0.0, -43.7], speed=self._tcp_speed,
                                              mvacc=self._tcp_acc, radius=0.0, wait=True)
                if not self._check_code(code, 'set_position'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[125.5, 33.0, 52.7, 0.0, 6.0, 165.2], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[80.0, 40.0, 75.0, 0.0, 15.0, 162.0], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[53.0, 65.1, 109.5, 0.0, 28.7, 163.9], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[33.3, 65.6, 110.5, 0.0, 27.0, 168.1], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[17.7, 61.9, 103.8, 0.0, 21.9, 176.9], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-2.6, 63.0, 105.7, 0.0, 23.3, 186.9], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-19.5, 71.8, 121.8, 0.0, 31.9, 196.5], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-41.6, 64.9, 109.3, 0.0, 28.0, 204.4], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-54.2, 46.4, 76.0, 0.0, 9.5, 208.8], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-95.7, 31.1, 49.5, 0.0, 2.1, 211.1], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-100.0, 29.5, 46.9, 0.0, 0.6, 210.9], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-107.5, 25.0, 39.6, 0.0, -2.1, 211.1], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-123.1, 16.5, 26.6, 0.0, -6.8, 209.7], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-123.1, -4.9, 29.1, 0.0, 4.6, 209.7], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-64.6, 5.4, 41.1, 0.0, -5.4, 210.7], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-41.9, 39.0, 86.2, 0.0, 13.5, 201.2], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[-19.3, 42.9, 92.4, 0.0, 14.9, 194.8], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[1.8, 46.0, 97.3, 0.0, 16.4, 185.0], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[23.0, 57.4, 116.3, 0.0, 28.2, 174.1], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[42.8, 49.7, 103.4, 0.0, 23.6, 167.8], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[69.2, 43.0, 92.5, 0.0, 21.7, 161.7], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[122.2, 7.1, 42.9, 0.0, 8.4, 163.5], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[103.7, 39.1, 86.3, 0.0, 24.0, 163.9], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[122.2, 7.1, 42.9, 0.0, 8.4, 163.5], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[126.0, 24.5, 64.8, 0.0, 16.9, 167.4], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[122.2, 7.1, 42.9, 0.0, 8.4, 163.5], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[110.5, -7.3, 28.5, 0.0, 0.2, 160.3], speed=self._angle_speed,
                                                 mvacc=self._angle_acc, wait=True, radius=0.0)
                if not self._check_code(code, 'set_servo_angle'):
                    return
                code = self._arm.set_pause_time(2)
                if not self._check_code(code, 'set_pause_time'):
                    return
                capture_and_save_image(h_cam, mem_ptr, 1280, 720)

                code = self._arm.set_pause_time(1)
                if not self._check_code(code, 'set_pause_time'):
                    return

                code = self._arm.set_servo_angle(angle=[55.9, 1.2, 30.1, 0.0, 10.9, 81.2], speed=self._angle_speed,
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




