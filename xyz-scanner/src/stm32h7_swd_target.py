import swd

##### STM32H7 Memory-Map
# SRAM1 = 0x24000000, 512k
# SRAM1 = 0x20000000, 128k
# SRAM2 = 0x30000000, 288k
# SRAM3 = 0x38000000, 64k
# SRAM4 = 0x00000000, 64k

class Stm32hf_Target_Tests:
    def __init__(self):
        self.dev = None
        self.cm = None
        self.byte_errors_count = 0
        self.fatal_error_count = 0
        self.initialized = False
        self.reinitialize_target = True

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

    def reset_byte_error_count(self):
        self.byte_errors_count = 0

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
        try:    
            byte_errors = 0
            sram_address = 0x24000000
            print("Reading SRAM BANK 1")
            for i in range(512 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    byte_errors_count += 1
                sram_address += 4

            print("Reading SRAM BANK 2")
            sram_address = 0x20000000
            for i in range(128 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    byte_errors_count += 1
                sram_address += 4

            print("Reading SRAM BANK 3")
            sram_address = 0x30000000
            for i in range(288 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    byte_errors_count += 1
                sram_address += 4

            print("Reading SRAM BANK 4")
            sram_address = 0x38000000
            for i in range(64 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    byte_errors_count += 1
                sram_address += 4

            print("Reading SRAM BANK 5")
            sram_address = 0x00000000
            for i in range(64 * 1024 // 4):
                if self.dev.get_mem32(sram_address) !=  0xaaaaaaaa:
                    byte_errors_count += 1
                sram_address += 4

            # TODO: read core register values.
            # Perhaps we can locate the register file on the die.

            # # Print Results. 
            # print("Number of Byte Errors", byte_errors_count)
            if byte_errors_count > 0:
                self.reinitialize_target = True
            else:
                self.reinitialize_target = False

        except Exception as e:
            # e = StlinkException('AP WDATA error')
            self.fatal_error_count = 0
            reinitialize_target = True
            print("Possible SWD Debug USB failure")

        # TODO: Return Success or Failure