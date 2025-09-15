import serial
import time

class EmfiBlaster(object):
    """This class defines the communication to EMFI Blaster"""
    command_arm_off = [1, 0]
    command_arm_on = [1, 1]

    def __init__(self):
        self.SerialPort = None

    def connect(self):
        self.SerialPort = serial.Serial("/dev/ttyUSB1", baudrate = 9600)

    def arm(self):
  
        self.SerialPort.write(bytes(self.command_arm_on))

        # command id, MSB period, LSB period, MSB width, LSB width
        # Very Narrow Beam
        command_pwm = [3, 5, 0, 0, 21]

        # command_pwm = [3, 5, 0, 0, 24]

        # 540 volts.
        # command_pwm = [3, 6, 64, 0, 24]

        # 585 volts
        # command_pwm = [3, 6, 255, 0, 24]

        # 600 volts
        #command_pwm = [3, 7, 0, 0, 24]

        # 532 volts
        # command_pwm = [3, 8, 0, 0, 24]

        # 672 volts 
        # command_pwm = [3, 7, 0, 0, 30]

        # 740 volts
        # command_pwm = [3, 7, 0, 0, 40]

        self.SerialPort.write(bytes(command_pwm))

        time.sleep(3)
    
    def disarm(self):
        self.SerialPort.write(bytes(self.command_arm_off))
