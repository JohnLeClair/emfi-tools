# Copyright (c) 2025    Condor Embedded Technology, LLC
# All rights reserved.
#
# Author: John LeClair
# Email:  jleclair@condorembeddedtech.com
#
# filename: xy_stage.py
# This file is part of the EMFI-Target project which is based at least in part
# by NewAE Ballistic Gel project hardware and software. 
#
#    This project is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This project is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this project.  If not, see <http://www.gnu.org/licenses/>.
#=============================================================================


import serial
import time

""" This class defines the communication to EMFI Blaster """
class EmfiBlaster:

    class EMFI_VOLTAGE_SETTING:
        EMFI_350_VOLTS = 1
        EMFI_540_VOLTS = 2
        EMFI_600_VOLTS = 3
        EMFI_672_VOLTS = 4
        EMFI_740_VOLTS = 5

    command_arm_off = [1, 0]
    command_arm_on = [1, 1]
    command_shoot = [4, 0, 50]
    

    def __init__(self):
        self.serial_port = None
        self.voltage_index = None

    def __del__(self):
        if self.serial_port.is_open:
            self.serial_port.close()

    def connect(self, serial_port_name):
        try:
            self.serial_port = serial.Serial(serial_port_name, baudrate = 9600)

        except serial.SerialException as e:
            self.SerialPort = None
            return False
        
        return True
    
    def disconnect(self):
        if self.serial_port.is_open:
            self.serial_port.close()

    def arm(self, voltage_index):
        self.serial_port.write(bytes(self.command_arm_on))
        self.voltage = voltage_index

        # A match statement here would be nice, but... not all my machines can be updated to python >= 3.10
        # Probably shoudld use a list but... this is easier to type. or calculate voltages on the fly.
        if voltage_index == self.EMFI_VOLTAGE_SETTING.EMFI_350_VOLTS:   # Narrow, weakish magnetic field.
            # command id, MSB period, LSB period, MSB width, LSB width
            command_pwm = [3, 5, 0, 0, 21]
        elif voltage_index == self.EMFI_VOLTAGE_SETTING.EMFI_540_VOLTS:
            command_pwm = [3, 6, 64, 0, 24]
        elif voltage_index == self.EMFI_VOLTAGE_SETTING.EMFI_600_VOLTS:
            command_pwm = [3, 7, 0, 0, 24]
        elif voltage_index == self.EMFI_VOLTAGE_SETTING.EMFI_672_VOLTS:
            command_pwm = [3, 7, 0, 0, 30]
        elif voltage_index == self.EMFI_VOLTAGE_SETTING.EMFI_740_VOLTS:
            command_pwm = [3, 7, 0, 0, 40]
        # Arg ... missing 800 - 1000 voltage range. Qhere did they go ?
        # Probably a good thing, I do not need to get zapped again. Once was enough.
        # TODO: 
        else:
            # Shouldnt be here - we check the bounds somewhere else right ?
            # We will do something ridiculously stupid and not complain, just 
            # set to a low power setting. Really bad decision I could return an error or throw exception. Nah.
            # Make it a TODO: We all know TODOs rarely get fixed though. 
            command_pwm = [3, 5, 0, 0, 21]

        # send the pwm (high voltage generation) command
        self.serial_port.write(bytes(command_pwm))                                             

    def disarm(self):
        self.serial_port.write(bytes(self.command_arm_off))
    
    def shoot(self):
        self.serial_port.write(bytes(self.command_shoot))
