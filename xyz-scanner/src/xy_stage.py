import sys
import argparse

# Target Test
from stm32h7_swd_target import *

# Tools control
from cnc_grbl import *
from emfiblaster import *

# NewAE GPL License files. 
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
from PIL import Image

# Global Settables - TODO: Move this and calibration data etc to config file. 
debug_xyz_stage_flag = False
safe_debug = True
create_bitmap_flag = False


# Fake scan array for testing the display of results - bmp, graph, etc. 
debug_scan_results_array = np.array([
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 2, 2, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 2, 2, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 2, 2, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]
])


def plotScanResults(result_array):
    plt.imshow(result_array, cmap='viridis') #investigate np.meshgrid
    # plt.matshow(result_array)
    plt.colorbar(label='Value')
    plt.title('2D Scan Results')
    plt.show()

def testMeshGrid(result_array):
    # Create sample x, y, and 2D array data
    x = np.linespace(0, 20, 20)
    y = np.linespace(0, 20, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) + np.cos(Y)

    # Create a color plot using pcolormesh
    plt.pcolormesh(X, Y, Z, cmap='RdBu')
    plt.colorbar(label='Value')
    plt.title('2D Array Visualization with pcolormesh')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.show()
    
# Main 
if __name__ == '__main__':

    print("Python version:")
    print(sys.version)

    # flags
    use_raw_method = True
    do_plot = True

    plotScanResults(debug_scan_results_array)
    sys.exit()

    # Scan layout TODO: Delete me.
    # x_step = 2.0      # Step size, in mm
    # y_step = 2.0      # Step size, in mm
    # x_steps = 21      # Number of steps to take 20
    # y_steps = 19      # Number of steps to take 40
    # x_max = x_step * x_steps    # Size of the grid we're measuring
    # y_max = y_step * y_steps    # Note that we'll never reach x = x_max

    # Command line argument parsing
    parser = argparse.ArgumentParser("XY Stage with specific targets")
    parser.add_argument('-p', '--emp',        type=str, required=True, help='emp pulse serial port address')
    parser.add_argument('-t', '--target',     type=str, required=True, help='emp pulse serial port address')
    parser.add_argument('-c', '--controller', type=str, required=True, help='xyz stage controller serial port address')
    args = parser.parse_args()    

    print(args.emp) 

    print("Choose a target: ")
    print("   (1) EMFI Target or NewAE Ballistic Gel silicon die recon scan bitmap)")
    print("   (2) STM32H7 Target (SWD Mode Debugger)")
    print("   (3) Arduino ATMEGA 2650 Target (SAM-ICE JTAG)")
    print("   (4) Xilinx Zynq XC7 Series (XSDB/Vivado)")
    print("   (5) Xilinx Zynq Ultrascale+ (XSDB/Vivado)")
    print("   (6) Unnamed ARM64 Tablet Bootloader (Saleae Logic 2 Python Automation API)")
    print("   (999) Single Shot Probe tester into EMFI Target SRAM Board to measure view spread")
    target_type = input()

    if (target_type != 999):
        print()
        # TODO: Move everything to float eventually. It just complicates things for the moment.... 
        value = input("Enter x-axis chip dimension(mm): ")
        x_width_mm = int(value)
        value = input("Enter y-axis chip dimension(mm): ")
        y_width_mm = int(value)
        value = input("Enter x-step resolution (mm): ")
        x_stepsize_mm = int(value)
        value = input("Enter y-step resolution (mm): ")
        y_stepsize_mm = int(value)

    print()
    print("Enter EMP Pulse Voltage")
    print("   (1) 350 Volts")
    print("   (2) 550 Volts")
    print("   (3) 600 Volts")
    print("   (4) 672 Volts")      
    print("   (5) 750 Volts")
    print("   (6) 950 Volts")
    value = input()
    voltage = int(value)

    input("\n *** Hit enter to start test and arm EMFI Blaster ***\n")

    # CNC Controller 
    cnc_controller = CNC_Grbl()
    cnc_controller.start(args.controller)
    # cnc_controller.setRelative()
    if debug_xyz_stage_flag == False:
        if target_type:      
            # Startup and initialize the EMP Target
            target = Stm32h7_Target_Tests()
            target.setup()

        # EMFI Blaster
        emp_pulse = EmfiBlaster()

        retValue = emp_pulse.connect(args.emp)
        if retValue != True:
            cnc_controller.disconnect()
            print("EMFI Pulse Device failed to open")
            sys.exit()

        # Everthing is setup and aiming at the target. 
        # **** Danger: Arming High Voltage ****
        if safe_debug:
            emp_pulse.disarm() # just in case this was left in ARMING position on a different run
            print("*** Safe Mode - No Arming of EMFI Blaster ***")
        else:
            print("*** Danger: Arming EMP Blaster ***")
            emp_pulse.arm() # TODO: add a power setting parameter
            time.sleep(3)  # Give time to charge up capacitors

    firstTimeReading = True

    # Create a 2D array of chip scan results.
    result_row = 0
    result_col = 0
    scan_results_array = np.ones((x_width_mm // x_stepsize_mm, y_width_mm // y_stepsize_mm))
    
    # Scan the chip
    positiveMovment = True
    for y_counts in range(y_width_mm // y_stepsize_mm):
        for x_counts in range(x_width_mm // x_stepsize_mm):

            # if not just testing xy-stage - initialize target, fire an EMP pulse, measure, repeat without
            # the user getting shocked by the EMP Blaster.
            if debug_xyz_stage_flag == False:
                # Step 1: Re-set the EMFI Target SRAM to random data.
                # if use_raw_method:
                #     emfi_target.raw_test_setup()
                # else:
                #     emfi_target.seed_test_setup()
                if target.reload_target():
                    target.load_target()

                # Step 2: Fire EMP Pulse
                if safe_debug != True:
                    emp_pulse.shoot() # TODO: add a power setting parameter

                # Step 3: Check for EMFI bit flips and/or fatal errors. 
                point_scan_result = target.examine_target()

                # Step 4: Check if a USB failure due to CPU/SWD crash from EMP pulse
                if (point_scan_result == target.EXAMINE_RET_CODE.USB_ERROR):
                    # cycle reset button on SWD interface.
                    None # TODO: restart target or something here. 

                # Step 5: Populate SRAM Matrix with errors (or no errors).
                scan_results_array[result_row][result_col] = point_scan_result
                result_row += 1
                result_col += 1

                # TODO: Reset statistics (or may be keep a rolling tally?)
                target.reset_sram_error_count()
                target.reset_register_error_count()
                target.reset_fatal_error_count()

            # Move EMP Blaster to next blast and examine position    
            if positiveMovment == True:
                cnc_controller.move(x_stepsize_mm, 0, 0)
            else:
                cnc_controller.move(-1*x_stepsize_mm, 0, 0)
            time.sleep(0.25)

        cnc_controller.move(0, y_stepsize_mm, 0)

        ### time.sleep(5)
        # Completed single x-direction scan. now to move 
        # opposite direction for next x-direction scan.
        positiveMovment = not positiveMovment

        # Save scan_array data. but also save metadata, stepsize, voltage, date, time, etc
 ###   TODO: pickle.dump(scan_results_array, open("filename", "wb"))
    
    # This is a SRAM Chip memory recon-only method at the moment
    if create_bitmap_flag == True:
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
    
    if debug_xyz_stage_flag == False:
        emp_pulse.disarm()
