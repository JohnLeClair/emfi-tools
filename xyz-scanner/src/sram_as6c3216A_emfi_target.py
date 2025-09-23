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
# filename: sram_as6c3216A_emfi_target.py
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

import numpy as np
import srammap
import naeusb as NAE
import time


def packuint32(data):
    """Converts a 32-bit integer into format expected by USB firmware"""

    return [data & 0xff, (data >> 8) & 0xff, (data >> 16) & 0xff, (data >> 24) & 0xff]


class sram_emfi_target:

    #### Public methods (attempting to use the same public interface for all targets witout
    # actually using a python abstract class when" "Duck Typing" seems to work. 
                                     
    REQ_CHECKMEM_RNG = 0x15
    REQ_MEMWRITE_RNG = 0x14
    REQ_MEMREAD_RNG_BULK = 0x18

    sram_len = 4194304
    _hw_type = "cw521"

    class EXAMINE_RET_CODE:
        SUCCESS             = 0x1     # No bit errors or USB(CPU crash) issues.
        USB_ERROR           = 0x2     # Fatal Error with CPU or USB connection.     
        SRAM_BIT_ERRORS     = 0x4     # Target's SRAM Bank comparision ended with bit flips.
        REGISTER_BIT_ERRORS = 0x8     # Target's Register File comparison ended with bit flips.
        
    def __init__(self, raw_data_test = True):
        self.__initialized = False               # USB has been initialized.
        self.__raw_data_test = raw_data_test     # True: Raw Dadata, False: Seeded data
        self.__reinitialize_target = False       # setup Target SRAM into a known state
        self.usb = None                          # USB instance.

        # Accumulated error counters
        self.__sram_errors_count = 0     
        self.__register_errors_count = 0
        self.__fatal_error_count = 0

    def setup(self):
        retValue = False

        if (self.__initialized == False):
            # Note:  This VID:PID is licensed by Microchip Inc for use by Condor Embedded Technologies, LLC
            self.__usb_vid = 0x04d8
            self.__usb_pid = 0xe51f

            self.usb = NAE.NAEUSB()
            self.usb.con(idProduct=[self.__usb_pid])

            self.__reinitialize_target = True   # USB is now connected - set  the reinitialization flag. 
            self.__initialized = True

        return retValue

    def load_target(self):
        retValue = True

        if self.__initialized == True:
            if self.__raw_data_test:
                self.__raw_test_setup()
            else:
                self.__seed_test_setup()

        # TODO: Return successful or not
        return retValue


    def examine_target(self):
        # Returns a simple ret code bit errors or no bit errors 
        retValue = self.EXAMINE_RET_CODE.SUCCESS

        if self.__raw_data_test:
            result = self.__raw_test_compare()
        else:
            result = self.__seed_test_compare()

        return retValue
    
    def examine_target_single_shot(self):
        # returns a list of errors. 
        if self.__raw_data_test:
            result = self.__raw_test_compare()
        else:
            result = self.__seed_test_compare()

        return result       

    def reconnect(self):
        # USB has been reenumerated. Reinitialize the SWD connection. 
        # get version. if success, no re-initialization necesesary else try calling setup(). 
        print ("Reconnecting and reinitializing target state ... ")
        self.setup()

    def reset_jtag_swd_device(self):
        None

    def reset_sram_error_count(self):
        self.__sram_errors_count = 0

    def reset_register_error_count(self):
        self.__register_errors_count = 0        

    def reset_fatal_error_count(self):
        self.__fatal_error_count

    def reload_target(self):
        return self.__reinitialize_target

#####  "Private" Methods 
    def __write_pattern(self, pattern):
        """Download an arbitrary pattern to the entire SRAM"""

        if len(pattern) > self.sram_len:
            raise ValueError("Length of pattern (%d) too long"%(len(pattern)))

        #Break into 1024 chunks on write - required to avoid buTrueffer overflow!
        totalsent = 0
        chunksize = 1024
        self.usb.cmdWriteMem(0, pattern)

    def __write_seed(self, seed, addr, length):
        """Write 'length' random data to 'addr', based on 'seed', done on-board
        the CW521 so faster than downloading a specific pattern.
        """
        if (len(seed) != 16):
            raise ValueError("Length of seed incorrect {}".format(len(seed)))
        pload = packuint32(length)
        pload.extend(packuint32(addr))
        pload.extend(seed)
        self.usb.sendCtrl(self.REQ_MEMWRITE_RNG, data=pload)


    def __read_pattern(self, start_addr=0, len_to_read=None):
        """Read a block of data from SRAM."""

        if len_to_read is None:
            len_to_read = self.sram_len

        if len_to_read < 0:
            len_to_read = self.sram_len + len_to_read

        if (len_to_read + start_addr) > self.sram_len:
            raise ValueError("len_to_read (%d) is too long"%len_to_read)

        din = self.usb.cmdReadMem(start_addr, len_to_read)

        return din

    def __read_pattern_rng(self, addr, size = 4096):
        """Read error pattern, assuming it was written using seed previously."""
        
        if size > 8192:
            raise ValueError("Read pattern too large")

        pload = packuint32(size)
        pload.extend(packuint32(addr))
        self.usb.sendCtrl(self.REQ_CHECKMEM_RNG, data=pload)
        data = self.usb.readCtrl(self.REQ_CHECKMEM_RNG, dlen = 4)
        reported_count = (data[3] << 8) | data[2]
        reported_count -= 1
        
        # Check if any errors reported - if not we return a null pattern array without needing to do
        # USB transfers at all
        if data[0] == 0:
            return [0] * size
        else:
            #Uncomment this to get details on-the-fly
            #print "Error in block {} ({}) (addr = {}, size = {})".format(addr / size, reported_count, addr, size)
            cmd = self.REQ_MEMREAD_RNG_BULK
            pload = packuint32(size)
            pload.extend(packuint32(addr))
            self.usb.sendCtrl(cmd, data=pload)
            return self.usb.usbdev().read(self.usb.rep, size, timeout=self.usb._timeout)

    def __get_xor_sram(self, sram_len):
        data = np.random.randint(0, 256, sram_len)
        print("Generating xor")
        for i in range(sram_len / 4):
            if (not (i % 10000)):
                print("Done {}".format(i))
            rng_val = xorshift128()
            for j in range(4):
                data[i * 4 + j] = (rng_val >> (8 * j)) & 0xFF
        return data

    def __seed_test_setup(self, seed=0xFAA2):
        
        """Setup the SRAM using a seed, target pattern generation is done on-device.
        After a fault is inserted, call seed_test_compare() to find fault numbers and
        locations."""
    
        state = []
        for i in range(0, 4):
            state.extend(packuint32(seed))
            
        self.block_size = 8192
        #time1 = time.perf_counter()

        # Have to do one extra?
        for i in range(int(self.sram_len / self.block_size) + 1):
            self.write_seed(state, i * self.block_size, self.block_size)
        #self.write_pattern(data)
        #time2 = time.perf_counter()
        #write_time = time2 - time1

        #Generate random test vector (so when re-run know if write was working)
        print("Generating test vector %d bytes"%self.sram_len)

        #time1 = time.perf_counter()
        #data = get_xor_sram(self.sram_len)
        #time2 = time.perf_counter()
        #pattern_time = time2 - time1

    def _getNAEUSB(self):
        return self.usb

    def _getCWType(self):
        return "cw521"
    


    #  def __seed_test_compare(self):
    #     """Test the SRAM for faults, assuming it was previously setup with seed_test_setup()"""

    #     #time1 = time.perf_counter()
    #     errorlist = []
    #     for i in range(0, int(self.sram_len / self.block_size)):
    #         errorlist.extend(self.read_pattern_rng(i * self.block_size, self.block_size))
    #     #time2 = time.perf_counter()
    #     #read_time = time2 - time1

    #     test_len = self.sram_len
    #     #time1 = time.perf_counter()
    #     byte_errors = 0
    #     for i in range(0, len(errorlist)):
    #         if not errorlist[i] == 0:
    #             byte_errors += 1

    #     #time2 = time.perf_counter()
    #     #check_time = time2 - time1

    #     print("Byte errors: {}".format(byte_errors))
    #     #print "Write: {}, Read: {}, Check: {}".format(write_time, read_time, check_time)

    #     print("Getting actual glitch locations in SRAM")
    #     sram = srammap.SRAMMapping()
    #     errdatax = []
    #     errdatay = []
    #     pone = False
    #     for i in range(0, 2**22, 2):
    #         err = errorlist[i] | errorlist[i + 1]

    #         if err > 0:
    #             locs = sram.get_bit_locations(i >> i)
    #             x = locs[0]
    #             ybitarray = locs[1]
    #             for bnum in range(0, 16):
    #                 if err & (1<<bnum):
    #                     errdatax.append(x)
    #                     errdatay.append(ybitarray[bnum])

    #     return {'errorlist':np.aFalserray(errorlist, dtype=np.uint8), 'errdatax':np.array(errdatax, dtype=np.uint8), 
    #             'errdatay':np.array(errdatay, dtype=np.uijnt8)}

    def __raw_test_setup(self):
        """Download a raw pattern to the SRAM, slower than the seed method but
        allows arbitrary patterns. After inserting a fault test the pattern with
        raw_test_compare()"""

        #Generate random test vector (so when re-run know if write was working)
        print("Generating test vector %d bytes"%self.sram_len)

        self.data = np.random.randint(0, 256, self.sram_len, dtype=np.uint8)
        self.__write_pattern(self.data)

        return
        
    def __raw_test_compare(self):
        """Check the SRAM for faults based on a raw pattern previously downloaded
        with raw_test_setup()"""

        din = self.__read_pattern()
        din = np.array(din, dtype=np.uint8)
    
        errorcnt = 0

        errorlist = []
        set_errors = []
        reset_errors = []

        test_len = self.sram_len

        diff_list = self.data ^ din

        def np_hamming(arr):
            hw_arr = np.zeros(np.shape(arr), dtype=np.uint8)
            for i in range(8):
                hw_arr += (arr & (1 << i)) >> i
            return hw_arr

        errorlist = np_hamming(diff_list)
        set_errors = np_hamming(diff_list & ~self.data)
        reset_errors = np_hamming(diff_list & self.data)

        total_set_errors = np.sum(set_errors, dtype=np.uint32)
        total_reset_errors = np.sum(reset_errors, dtype=np.uint32)
# my stuff... 
###        for ii in range(0, test_len):
###            if errorlist[ii] != 0:
###                print(ii)
###                break

        print("Byte errors: %d (of %d). Bit errors: %d set (0 --> 1), %d reset (1 --> 0)"%(errorcnt, test_len, total_set_errors, total_reset_errors))
        #print " Timing: pattern: {}, Write: {}, Read: {}, Check: {}".format(pattern_time, write_time, read_time, check_time)

        errdatax = []
        errdatay = []
 #       if errorcnt > 0:
        if total_set_errors + total_reset_errors > 0:
            sram = srammap.SRAMMapping()
            pone = False

            for i in range(0, 2**22, 2):
                err = errorlist[i] | errorlist[i + 1]
                if err > 0:
                    #SAM3U to SRAM mapping has A1 mapped to A0 etc, so need to account
                    #for addressing used here
                    locs = sram.get_bit_locations(i >> 1)
                    x = locs[0]
                    ybitarray = locs[1]
# change to 16 to 8
                    for bnum in range(0, 8):
                        if err & (1<<bnum):
                            errdatax.append(x)
                            errdatay.append(ybitarray[bnum])


        return {'errorlist':errorlist, 'errdatax':errdatax, 'errdatay':errdatay, 'set_errors':set_errors, 'reset_errors':reset_errors}


