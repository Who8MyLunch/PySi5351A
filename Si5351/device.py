
import math

import smbus2

from .memoize import Memoize

#--------------------------------------------------------------------
# Helper functions

# Pack
# Return a byte string containing the values v1, v2, ... packed
# according to the compiled format string. If the total number
# of bits are not a multiple of 8, padding will be added at the
# end of the last byte.

# Unpack
# Unpack `data` (byte string, bytearray or list of integers)
# according to the compiled format string. The result is a tuple
# even if it contains exactly one item.

@Memoize
def _compiled_bitfield(MSB, LSB):
    """Generate a compiled bitfield packer/unpacker.  Uses package bitstruct.
    Only a single data field is packed/unpacked.
    """
    # Enforce multiples of 8 bits
    width = int(math.ceil(MSB/8)*8)
    
    N_lead = width - MSB - 1
    N_data = MSB - LSB + 1
    N_trail = LSB

    fmt = 'p{:d}u{:d}p{:d}'.format(N_lead, N_data, N_trail)

    cfmt = bs.compile(fmt)

    return cfmt



def number_of_bits(value):
    value = int(value)
    if value == 0:
        return 0
    else:
        return math.floor(math.log2(value) + 1 )

def number_of_bytes(value):
    value = int(value)
    if value == 0:
        return 0
    else:
        return math.ceil(number_of_bits(value)/8)



@Memoize
def _mask(MSB, LSB):
    """Create mask to select bits between LSB and MSB (inclusive)
    """
    mask_MSB = (1 << MSB) - 1
    mask_LSB = (1 << LSB) - 1
    
    return mask_MSB & ~mask_LSB
    

def _unpack_bits(data_binary, MSB, LSB):
    """Extract bits between MSB and LSB (inclusive)
    """
    if data_binary == 0:
        return 0
    
    data_masked = data_binary & _mask(MSB, LSB)
    data_shifted = data_masked >> LSB
    
#     data_binary = int(data_binary)  
#     N = number_of_bytes(data_binary)
#     N = max([N, math.ceil(MSB/8)])
#     cfmt = _compiled_bitfield(MSB, LSB)
#     # Unpack function receives a string of bytes, and always returns a sequence, even for size-1 data
#     seq = data_binary.to_bytes(N, 'big')
#     data_value = cfmt.unpack(seq)[0]

    return data_shifted



def _pack_bits(data_bits, MSB, LSB):
    """Pack unsigned-integer data value into zero-padded bitfield
    """
    if data_bits == 0:
        return 0

    data_shifted = data_bits << LSB
    data_masked = data_shifted & _mask(MSB, LSB)
    
#     cfmt = _compiled_bitfield(MSB, LSB)
#     # Pack function returns a byte string
#     buff = cfmt.pack(data_value)
#     # Convert byte string to unsigned integer
#     # https://stackoverflow.com/questions/444591/convert-a-string-of-bytes-into-an-int-python
#     data_binary = int.from_bytes(buff, 'big')

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

    def write_byte(self, register, data):
        """Write a byte to designated register
        """
        self._smbus.write_byte_data(self._address, register, data)

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
            print(data_reg_byte)
            data_intermed = _unpack_bits(data_reg_byte, register['reg_MSB'], register['reg_LSB'])

            if 'dat_LSB' in register and register['dat_LSB'] > 0:
                data_value = _pack_bits(data_intermed, register['dat_MSB'], register['dat_LSB'])
            else:
                data_value = data_intermed

            value += data_value

        return value
        
    def set_parameter(self, name, value):
        """Bit-pack data value and write byte(s) to device register(s)
        """
        if value < 0:
            raise ValueError('Unsigned integers only: {}'.format(value))

        value = int(value)
        
        print()
        print()
        print(value)
        
        for register in self._parameters[name]:
            print()
            print(register['register'])
            
            # Unpack data (if necessary)
            if 'dat_LSB' not in register:
                register['dat_MSB'] = 7
                register['dat_LSB'] = 0
                
            data_intermed = _unpack_bits(value, register['dat_MSB'], register['dat_LSB'])
                
            print('I', data_intermed, register['dat_MSB'], register['dat_LSB'])
            
            # Pack to register byte, zero padded outside data range
            if register['reg_LSB'] > 0:
                data_reg_byte = _pack_bits(data_intermed, register['reg_MSB'], register['reg_LSB'])
                print('R', data_reg_byte, register['reg_MSB'], register['reg_LSB'])
            else:
                data_reg_byte = data_intermed
                
            
            if 7 > register['reg_MSB'] or register['reg_LSB'] > 0:
                # Read and mask device's existing register value
                data_prior_byte = self.read_byte(register['register'])
                data_prior_byte &= ~_mask(register['reg_MSB'], register['reg_LSB']) 

                # Update
                assert((data_reg_byte &  _mask(register['reg_MSB'], register['reg_LSB'])) == data_reg_byte)
                assert((data_reg_byte & ~_mask(register['reg_MSB'], register['reg_LSB'])) == 0)
                
                data_reg_byte += data_prior_byte
                
            print(data_reg_byte)
            # Write byte to register address
#             self.write_byte(register['register'], data_reg_byte)

            
            
            
    #####


