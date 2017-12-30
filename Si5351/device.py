
import math
import smbus2

#--------------------------------------------------------------------
# Helper functions
def number_of_bits(value):
    value = int(value)
    if value == 0:
        return 0
    else:
        return math.floor(math.log2(value) + 1)


    
def number_of_bytes(value):
    value = int(value)
    if value == 0:
        return 0
    else:
        return math.ceil(number_of_bits(value)/8)



def mask(MSB, LSB):
    """Create mask to select bits between LSB and MSB (inclusive)
    """
    mask_p = (1 << MSB+1) - 1
    mask_q = (1 << LSB  ) - 1
    
    return mask_p & ~mask_q



def unpack_bits(data_binary, MSB, LSB):
    """Extract bits between MSB and LSB (inclusive)
    """
    if data_binary == 0:
        return 0
    
    data_masked = data_binary & mask(MSB, LSB)
    data_shifted = data_masked >> LSB
    
    return data_shifted



def pack_bits(data_bits, MSB, LSB):
    """Pack unsigned-integer data value into zero-padded bitfield
    """
    if data_bits == 0:
        return 0

    data_shifted = data_bits << LSB
    data_masked = data_shifted & mask(MSB, LSB)
    
    return data_masked


#----------------------------------------------------------------------

class Device():
    """Manage data IO with a given I32C/SMBus device
    """
    def __init__(self, address, parameters, bus):
        """Instantiate device manager given device parameters
        """
        self._address = address
        self._parameters = parameters
        self._smbus = smbus2.SMBus(bus)

    def write_byte(self, register, data_byte):
        """Write a byte to designated register
        """
        self._smbus.write_byte_data(self._address, register, data_byte)

    def read_byte(self, register):
        """Read a byte from designated register
        """
        return self._smbus.read_byte_data(self._address, register)

    def get_parameter(self, name):
        """Extract parameter value from device register(s)
        """
        value = 0
        for register in self._parameters[name]:
            data_reg_byte = self.read_byte(register['register'])
            
            data_intermed = unpack_bits(data_reg_byte, register['reg_MSB'], register['reg_LSB'])

            if 'dat_LSB' not in register:
                register['dat_MSB'] = 7
                register['dat_LSB'] = 0
                
            data_value = pack_bits(data_intermed, register['dat_MSB'], register['dat_LSB'])
            value += data_value

        return value
        
    def set_parameter(self, name, value):
        """Bit-pack data value and write byte(s) to device register(s)
        """
        if value < 0:
            raise ValueError('Only unsigned integers allowed: {}'.format(value))

        value = int(value)
        
        for register in self._parameters[name]:
            if 'dat_LSB' not in register:
                register['dat_MSB'] = 7
                register['dat_LSB'] = 0
                
            # Unpack data bits
            data_intermed = unpack_bits(value, register['dat_MSB'], register['dat_LSB'])
                
            # Pack to register byte, zero padded outside data range
            data_reg_byte = pack_bits(data_intermed, register['reg_MSB'], register['reg_LSB'])

            if register['reg_MSB'] < 7 or register['reg_LSB'] > 0:
                # Read and mask device's existing register value
                data_prior_byte = self.read_byte(register['register'])
                data_prior_byte &= ~mask(register['reg_MSB'], register['reg_LSB']) 

#                 assert((data_reg_byte &  mask(register['reg_MSB'], register['reg_LSB'])) == data_reg_byte)
#                 assert((data_reg_byte & ~mask(register['reg_MSB'], register['reg_LSB'])) == 0)
                
                # Update
                data_reg_byte += data_prior_byte
            
            # Write byte to register address
            print(data_reg_byte)
#             self.write_byte(register['register'], data_reg_byte)
            
