import swd

##### STM32H7 Memory-Map
# SRAM1 = 0x24000000, 512k
# SRAM1 = 0x20000000, 128k
# SRAM2 = 0x30000000, 288k
# SRAM3 = 0x38000000, 64k
# SRAM4 = 0x00000000, 64k

class Stm32h7_Target_Tests:
    class EXAMINE_RET_CODE:
        SUCCESS             = 0x1     # No bit errors or USB(CPU crash) issues.
        USB_ERROR           = 0x2     # Fatal Error with CPU or USB connection.     
        SRAM_BIT_ERRORS     = 0x4     # Target's SRAM Bank comparision ended with bit flips.
        REGISTER_BIT_ERRORS = 0x8     # Target's Register File comparison ended with bit flips.

    def __init__(self):
        self.dev = None
        self.cm = None
        self.initialized = False
        self.reinitialize_target = True

        # multiple run accumulation counters
        self.sram_errors_count = 0     
        self.register_errors_count = 0
        self.fatal_error_count = 0

    def setup(self):
        if (self.initialized == False):
            self.dev = swd.Swd()
            self.cm = swd.CortexM(self.dev)

            # halt the processor so we can compare before/after EMP Pulse
            self.cm.halt()

            print("Target SWD Version: ", self.dev.get_version().str)
            print("Target Voltage: ", self.dev.get_target_voltage())
            print("Target ID Code: ", hex(self.dev.get_idcode()))
            
            self.initialized = True

    def reconnect(self):
        None # TODO:
        # check to see if lost USB communications or somethingelse
        # get version. if success, no re-initialization necesesary else try calling setup(). 

    def reset_sram_error_count(self):
        self.sram_errors_count = 0

    def reset_register_error_count(self):
        self.register_errors_count = 0        

    def reset_fatal_error_count(self):
        self.fatal_error_count

    def reload_target(self):
        return self.reload_target

    def load_target(self):
        if self.initialized == True:
            # Fill all SRAM Banks with known values. TODO: move to random numbers.
            print("Filling SRAM BANK 1") 
            sram_address = 0x24000000
            for i in range(512 * 1024 // 4):
                self.dev.set_mem32(sram_address, 0xaaaaaaaa)
                sram_address += 4

            print("Filling SRAM BANK 2")
            sram_address = 0x20000000
            for i in range(128 * 1024 // 4):
                self.dev.set_mem32(sram_address, 0xaaaaaaaa)
                sram_address += 4

            print("Filling SRAM BANK 3")
            sram_address = 0x30000000
            for i in range(288 * 1024 // 4 ):
                self.dev.set_mem32(sram_address, 0xaaaaaaaa)
                sram_address += 4

            print("Filling SRAM BANK 4")
            sram_address = 0x38000000
            for i in range(64 * 1024 // 4):
                self.dev.set_mem32(sram_address, 0xaaaaaaaa)
                sram_address += 4

            print("Filling SRAM BANK 5")
            sram_address = 0x00000000
            for i in range(64 * 1024 // 4):
                self.dev.set_mem32(sram_address, 0xaaaaaaaa)
                sram_address += 4

            # TODO: Load known register values to locate the register file.
            #
            # TODO: Return successful or not

    def examine_target(self):
        retValue = 0x0
        sram_errors = 0
        register_errors = 0

        try:
            sram_address = 0x24000000
            print("Reading SRAM BANK 1")
            for i in range(512 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    sram_errors += 1
                sram_address += 4

            print("Reading SRAM BANK 2")
            sram_address = 0x20000000
            for i in range(128 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    sram_errors += 1
                sram_address += 4

            print("Reading SRAM BANK 3")
            sram_address = 0x30000000
            for i in range(288 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    sram_errors += 1
                sram_address += 4

            print("Reading SRAM BANK 4")
            sram_address = 0x38000000
            for i in range(64 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    sram_errors += 1
                sram_address += 4

            print("Reading SRAM BANK 5")
            sram_address = 0x00000000
            for i in range(64 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    sram_errors += 1
                sram_address += 4

            # TODO: read core register values.
            # Perhaps we can locate the register file on the die.
            register_errors = 0

            # # Print Results. 
            print("Number of Byte Errors", sram_errors)
            if sram_errors > 0:
                self.reinitialize_target = True
            else:
                self.reinitialize_target = False

        except Exception as e:
            # e = StlinkException('AP WDATA error')
            self.fatal_error_count += 1
            reinitialize_target = True
            print("Possible SWD Debug USB failure")
            retValue = self.EXAMINE_RET_CODE.USB_ERROR

        # Successful. althought there could be bit errors. Instead of handling reinitialioze data, Let the parent
        # handle what needs to be done and let parent query each round. Perhaps the parents wants to accumulate
        # all of the errors for a single bit map. Probably end up always reinitializing processor with known 
        # data after each round but for now....
        self.sram_errors_count += sram_errors
        self.register_errors_count += register_errors
        
        if sram_errors > 0:
            retValue |= self.EXAMINE_RET_CODE.SRAM_BIT_ERRORS

        if register_errors > 0:
            retValue |= self.EXAMINE_RET_CODE.REGISTER_BIT_ERRORS

        # TODO: need to add register file test. 
        else:
            return self.EXAMINE_RET_CODE.SUCCESS

    def generate_bitmap_result(self):
        None