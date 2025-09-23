# Copyright (c) 2018-2019, NewAE Technology Inc
# All rights reserved.
#
# Authors: Colin O'Flynn, Alex Dewar
#
# This file is part of the ChipSHOUTER Ballistic Gel project.
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

import sys
import argparse


# Target Test
from stm32h7_swd_target import *
from sram_as6c3216A_emfi_target import *
# from xilinx_zynq_7000_target import *
# from xilinx_ultrascalplus_target import *

# Tools control
from cnc_grbl import *
from emfiblaster import *

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
safe_debug = False
create_bitmap_flag = True

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
    plt.colorbar(label='Examine')
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
    single_shot_mode = False    # Sends a EMP pulse only once. ie: no cnc controller needed.
    point_scan_result = None    # Results of a single EMP Pulse on a Target. 

    # TODO: Remove this test.
    # plotScanResults(debug_scan_results_array)
    # sys.exit()

    # Command line argument parsing
    parser = argparse.ArgumentParser("XY Stage with specific targets")
    parser.add_argument('-p', '--emp',        type=str, required=True, help='emp pulse serial port address')
    parser.add_argument('-t', '--target',     type=str, help='emp pulse serial port address')
    parser.add_argument('-c', '--controller', type=str, required=True, help='xyz stage controller serial port address')
    parser.add_argument('-r', '--relayboard', type=str, help='relay board serial port address')
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
    target_type_str = input()
    target_type = int(target_type_str)

    # Handle single shot pulse request
    if int(target_type) == 999:
        # For only a single point EMP Pulse. Cheesy Hack to only run the nested for loops once. 
        x_width_mm = 1
        y_width_mm = 1
        x_stepsize_mm = 1
        y_stepsize_mm = 1
        single_shot_mode = True
    else:
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

    # TODO: check parameters. 

    input("\n *** Hit enter to start test and arm EMFI Blaster ***\n")

    # CNC Controller
    if single_shot_mode == False:
        cnc_controller = CNC_Grbl()
        cnc_controller.start(args.controller)

    if debug_xyz_stage_flag == False:

        # Startup and initialize the EMP Target
        if target_type == 2:      
            target = Stm32h7_Target_Tests(args.relayboard)
        elif target_type == 1 or target_type == 999:
            target = sram_emfi_target()
        else:
            print("Unsupported or temporarily deleted target")
            sys.exit()
        target.setup()

        # EMFI Blaster Startup
        emp_pulse = EmfiBlaster()

        retValue = emp_pulse.connect(args.emp)
        if retValue != True:
            if cnc_controller.isConnected():
                cnc_controller.disconnect()
            # if target.isConnected(): TODO
            #    target.disconnect()
            print("EMFI Pulse Device failed to open")
            sys.exit()

        # Everthing is setup and aiming at the target. 
        # **** Danger: Arming High Voltage ****
        if safe_debug:
            emp_pulse.disarm() # just in case this was left in ARMING position on a different run
            print("*** Safe Mode - No Arming of EMFI Blaster ***")
        else:
            print("*** Danger: Arming EMP Blaster ***")
            emp_pulse.arm(voltage) # TODO: add a power setting parameter
            time.sleep(5)  # Give time to charge up capacitors

    firstTimeReading = True

    # Create a 2D array of chip scan results.
    result_row = 0
    result_col = 0
    scan_results_array = np.ones((x_width_mm // x_stepsize_mm, y_width_mm // y_stepsize_mm))
    print(f"Calculated 2D Scan Array shape is : {scan_results_array.shape}")
    
    # Scan the Unit Under Test (UUT)
    positiveMovment = True
    for y_counts in range(y_width_mm // y_stepsize_mm):
        result_row = 0
        for x_counts in range(x_width_mm // x_stepsize_mm):

            # if not just testing xy-stage - initialize target, fire an EMP pulse, measure, repeat without
            # the user getting shocked by the EMP Blaster.
            if debug_xyz_stage_flag == False:
                # Step 1: Re-set the EMFI Target SRAM to random data.
                if target.reload_target():
                    target.load_target()

                # Step 2: Fire EMP Pulse
                if safe_debug != True:
                    emp_pulse.shoot()

                # Step 3: Check for EMFI bit flips and/or fatal reboot needed errors.
                if single_shot_mode:
                    # Single Shot Mode on SRAM Target returns an array of data.
                    point_scan_result = target.examine_target_single_shot()
                else:
                    # XY Stage scan/recon returns a single value.
                    point_scan_result = target.examine_target()

                    if point_scan_result != target.EXAMINE_RET_CODE.SUCCESS and single_shot_mode != True:
                        target.reload_target()

                    # Step 4: Check if a USB failure due to CPU/SWD crash from EMP pulse
                    #TODO: if (point_scan_result == target.EXAMINE_RET_CODE.USB_ERROR):
                    #    target.reset_jtag_swd_device() # TODO: check individual codes with AND. 
                    #    target.reconnect()

                    # Step 5: Populate the scan array with errors (or no errors) fdata point
                    scan_results_array[result_row][result_col] = point_scan_result
                    result_row += 1

                    # TODO: Reset statistics (or maybe keep a rolling tally? hence these 3 methods still exist)
                    target.reset_sram_error_count()
                    target.reset_register_error_count()
                    target.reset_fatal_error_count()

            # Move xy stage if not in  single shot mode. 
            if single_shot_mode != True:
                # Move EMP Blaster to next blast and examine position    
                if positiveMovment == True:
                    cnc_controller.move(x_stepsize_mm, 0, 0)
                else:
                    cnc_controller.move(-1*x_stepsize_mm, 0, 0) 
                time.sleep(1)

        # Move xy stage if not in  single shot mode. 
        if single_shot_mode != True:
            result_col += 1
            cnc_controller.move(0, y_stepsize_mm, 0)
            time.sleep(1)

            # Completed single x-direction scan. now to move 
            # opposite direction for next x-direction scan.
            positiveMovment = not positiveMovment

        # Save scan_array data. but also save metadata, stepsize, voltage, date, time, etc
 ###   TODO: pickle.dump(scan_results_array, open("filename", "wb"))
    
    # This is for SRAM Single-Shot Mode (999) only
    if single_shot_mode == True:
        errdatay = point_scan_result['errdatay']
        errdatax = point_scan_result['errdatax']
        errorlist = point_scan_result['errorlist']
        
        errorlistScanResults = errorlist
        firstTimeReading = False

        errorlistScanResults = np.bitwise_or(errorlistScanResults, errorlist)
            
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
    else:
        plotScanResults(scan_results_array)

    
    if debug_xyz_stage_flag == False:
        emp_pulse.disarm()
