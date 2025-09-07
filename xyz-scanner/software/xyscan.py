'''
xyscan.py
Uses a DSA815 with a loop antenna probe attached to an M3D printer head
to scan for EM signals over the surface of the chip.

Author: Greg d'Eon
Date: May 3-4, 2016
'''

import sys

print("Python version:")
print(sys.version)

print("\nVersion info:")
print(sys.version_info)


# Controllers
from m3d import *
from emfitarget import *
from emfiblaster import *
from PIL import Image


import srammap
import naeusb as NAE

# Utilities
import math
from time import sleep

# Plotting
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import pickle

def plotHeatmap(data, x_min, x_max, y_min, y_max, filename):
    """
    Plot a heatmap.
    
    Args:
        Data: a 2D list of the data to be plotted
        x_min, y_min: the minimum coordinate of any data point
        x_max, y_max: the maximum coordinate any data point
        filename: where to save this image
    """
    
    # Generate x and y lists
    x_points = numpy.linspace(x_min, x_max, len(data[0]))
    y_points = numpy.linspace(y_min, y_max, len(data))
    
    x, y = numpy.meshgrid(x_points, y_points)

    # Plot heatmap
    fig = plt.figure()
    plt.pcolor(x, y, data, cmap=plt.cm.Blues)
    plt.axis([x_min, x_max, y_min, y_max])
    plt.colorbar()
    plt.xlabel("Frequency / Hz")
    plt.ylabel("Y coordinate / mm")
    fig.savefig(filename, bbox_inches="tight")

    
# Main script
if __name__ == '__main__':

    # flags
    use_raw_method = True
    do_plot = True

    # Scan layout
    x_step = 2.0      # Step size, in mm
    y_step = 2.0      # Step size, in mm
    x_steps = 4      # Number of steps to take 20
    y_steps = 1       # Number of steps to take 40
    
    x_max = x_step * x_steps    # Size of the grid we're measuring
    y_max = y_step * y_steps    # Note that we'll never reach x = x_max
    
     
    ## Startup and initialize the EMP Target
    # TODO: Create SRAM error matrix.
#    emfi_target = EmfiTarget()
#    emfi_target.con()

    # CNC Controller
    cnc_control = M3D()
    ### cnc_controller.start('/dev/ttyUSB0')
    # cnc_controller.setRelative()

    # EMFI Blaster
    emp_pulse = EmfiBlaster()
    emp_pulse.connect()
    emp_pulse.disarm()

    # For now start out home and move out into middle of platter. 
    ### cnc_controller.home()

    # TODO: Change me to move to bottom left of chip always mm for now.
    ### cnc_controller.move(0, 0, 25)   # lifet head
    ### cnc_controller.move(100, 300, 0)   

    # Everthing is setup and aiming at the target. 
    # **** Danger: Turning Arming High Voltage ****
    emp_pulse.arm()
    time.sleep(10)
    ### emp_pulse.disarm()

    firstTimeReading = True

    # Scan the chip
    positiveMovment = True
    for y_counts in range(y_steps):
        for x_counts in range(x_steps):

            # Step 1: Re-set the EMFI Target SRAM to random data.
            if use_raw_method:
                emfi_target.raw_test_setup()
            else:
                emfi_target.seed_test_setup()

            # Step 2: Fire EMP Pulse

            # Boom.
            emp_pulse.shoot()

            # Step 3: Check for EMFI SRAM errors
            if use_raw_method:
                 results = emfi_target.raw_test_compare()
            else:
                 results = emfi_target.seed_test_compare()

            errdatay = results['errdatay']
            errdatax = results['errdatax']
            errorlist = results['errorlist']
            
            # Since this is a pass over entire chip surface, Logical OR new data over the 
            # current list of multiple regions.
            if firstTimeReading == True:
                errorlistScanResults = errorlist
                firstTimeReading = False

            errorlistScanResults = np.bitwise_or(errorlistScanResults, errorlist)

            stopHere = 1

            # if do_plot:
            #     plt.plot(errdatax, errdatay, '.r')
            #     plt.axis([0, 8192, 0, 4096])
            #     plt.show()     
            
            # Step 4: Populate SRAM Matrix with Errors.

            # Step 5: Move EMP Blaster to next position    
            ### if positiveMovment == True:
                ### cnc_controller.move(x_step, 0, 0)
            ### else:
                ### cnc_controller.move(-1*x_step, 0, 0)
            time.sleep(1)
        ###  cnc_controller.move(0, y_step, 0)
        time.sleep(5)
        positiveMovment = not positiveMovment
    
    # 3D list for scan result data
    # scanData[x][y][f] is data at position (x, y) and frequency f
    # (ie: one output from DSA is scanData[x][y])
    #scanData = [[[0 for k in range(num_freqs+1)] 
    #            for j in range(y_steps)] 
    #            for i in range(x_steps)]
    

#    for x in range (7):
#        cnc_controller.move(-1)

    # Scan over the surface
    # for y in range (y_steps):
    #     for x in range (x_steps):
    #         # Wait for the head to stop moving
    #         time.sleep(0.1)
            
    #         # Scan with the spectrum analyzer
    #         ### scanData[x][y] = scope.measure_trace()
            
    #         # Note where we are
    #         ### print "x = {0:d}; y = {1:d}".format(x, y)
    #         time.sleep(0.1)
    
    #         # Move in x
    #         if x == x_steps-1:
    #             printer.move(x_step - x_max, 0)
    #         else:
    #             printer.move(x_step, 0)
            
                
    #     # Move in y
    #     if y == y_steps-1:
    #         printer.move(0, y_step - y_max)
    #     else:
    #         printer.move(0, y_step)
    
    # printer.stop()

 ###   pickle.dump(scanData, open("scandata.p", "wb"))
    
    # Create Bitmap
              # adjust for one bit-per-pixel gray scale value
    for i in range(len(errorlist)):
        if errorlistScanResults[i] > 0:
            errorlistScanResults[i] = 0     # black if errors.
        else:
            errorlistScanResults[i] = 255   # white if no errors.

    bmpWidth, bmpHeight = 2048, 2048
    xyArray = errorlistScanResults.reshape ((2048, 2048))
    image = Image.fromarray(xyArray, mode='L')
    image.save('my_bitmap.png')
    image.close()
    
    # Plot scan data
###    for i in range(len(scanData)):
###         plotHeatmap(scanData[i], f_low, f_hi, 0, y_max - y_step, "image{}".format(i))

    emp_pulse.disarm()
