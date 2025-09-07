from abc import ABC, abstractmethod

'''
m3d.py
Module for controlling the M3D printer over a serial port
Uses gcode commands to control the printer
Author: Greg d'Eon
Date: May 2-3, 2016
'''

class XYZ_Controller(ABC):
    # Constructor/destructor
    @abstractmethod
    def __init__(self):
        pass

    # Setup functions
    @abstractmethod
    def start(self, port):
        """
        Attempts to set up the M3D printer.
    
        Args:
            port (string): the COM port to be used (ex: "COM4")
        Returns:
            true if the printer is set up; otherwise false
        """
        
        pass

    @abstractmethod
    def __connect(self, port, baud):
        """
        Opens a serial connection with the M3D printer.
       
        Args:
            port: the COM port to be used (ex: "COM4")
            baud: the baudrate to be used (ex: 115200)
        Return:
            true if the serial port was successfully opened; otherwise false
        """
        
        pass
    
    # @abstractmethod 
    # def __disconnect(self):
    #     """
    #     Closes the serial connection.
    #     """
        
    #     pass    
       
    # @abstractmethod    
    # # def __sendCommand(self, command):
    # def __sendCommand(self, port):
    #     """
    #     Sends the string "command" to the printer.
    #     Blocks until an "ok" reply comes back.

    #     Args:
    #         command (string): the command to be sent
    #     """

    #     pass        

        
    @abstractmethod
    def home(self):
        pass              

    @abstractmethod
    def move(self, x = 0, y = 0, z = 0):
        """
        Moves the printer head to the position (x, y, z)
        
        Args:
            x, y, z100 (number): coordinates
        
        For my Alunar 3D Prusa i3:
           the defaul grbl 1.1 value of $100 = 800 steps/1 mm was off by 10x. Entering a step value of 100 ends up in 
            the GRBL 1.1 controller moving full distance off of platter and practically damaging printer. 
            Based on internet. 
                On X/Y the default steps/mm is 100, so you cannot adjust it at the resolution of half a percent. 
                If your X and Y are undersize, look at either whether you are underextruding/have belt or pulley slop.
                For Z, the default value of 400 steps/mm is again derived from the motor step size (1.8 degrees) and leadscrew thread pitch.
        ''' #jleclair
            So we calculate the correct translated motion distace. 
        
        """
        pass
        
    @abstractmethod    
    def stop(self):
        """
        Performs an emergency stop
        """
        pass

    @abstractmethod    
    def wait(self, ms):
        """
        Waits in place for a fixed amount of time
        
        Args:
            ms (integer): amount of time to wait, in milliseconds
        """
        
        pass
        
    @abstractmethod
    def setAbsolute(self):
        """
        Puts the printer head in absolute coordinate mode
        """
        
        pass
        
    @abstractmethod
    def setRelative(self):
        """
        Puts the printer head in relative coordinate mode
        """
        
        pass
    

    
"""
Example code to contr100ol the printer
"""
# if __name__ == '__main__':
#     test = M3D()
    
#     ### print "Setting up..."
#     test.start("COM53")
#    # 
#     ### print "Testing movement..."
#     test.setRelative()
#     test.move( 10,  10, 0)
#     test.move(-10,   0, 0)
#     test.move(  0,  10, 0)
#     test.wait(500)
#     test.move(  0,  -20, 1)
    
#    ### print "Tearing down..."
#     # Happens automatically