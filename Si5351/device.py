
import numpy as np
import bitstruct as bs
import smbus2

# Helper functions
def _bitfield_packer(MSB, LSB, width=8):
    """Generate a compiled bitfield packer/unpacker.  Uses package bitstruct.
    """
    N_lead = width - MSB - 1
    N_data = MSB - LSB + 1
    N_trail = LSB

    fmt = 'p{:d}u{:d}p{:d}'.format(N_lead, N_data, N_trail)

    cfmt = bs.compile(fmt)

    return cfmt


# Pack
# Return a byte string containing the values v1, v2, ... packed
# according to the compiled format string. If the total number
# of bits are not a multiple of 8, padding will be added at the
# end of the last byte.


# Unpack
# Unpack `data` (byte string, bytearray or list of integers)
# according to the compiled format string. The result is a tuple
# even if it contains exactly one item.


def _width(parameter)


# Main event
class Device():
    """Manage data IO with a given I32C/SMBus device
    """
    def __init__(self, address, parameters, bus):
        """Instantiate device manager given device parameters
        """
        self._address = address
        self._parameters = parameters

        self._smbus = smbus2.SMBus(bus)

    def write_byte(self, register, value):
        """Write a byte to designated register
        """
        self._smbus.write_byte_data(self._address, register, value)

    def read_byte(self, register):
        """Read single byte from designated register
        """
        return self._smbus.read_byte_data(self._address, register)

    def read_parameter(self, name):
        """Extract parameter value from device register
        """
        value = 0
        for item in self._parameters[name]:
            data_byte = self.read_byte(item['register'])
            print(data_byte)

            packer = _bitfield_packer(item['reg_MSB'], item['reg_LSB'])
            print(packer.unpack([data_byte]))

            data_part = packer.unpack([data_byte])[0]            
            
            if 'dat_LSB' in item:
                packer = _bitfield_packer(item['dat_MSB'], item['dat_LSB'])
                buff = packer.pack(data_part)
                data = np.frombuffer(buff, dtype=np.uint8)[0]
                print(data_part, data)
            else:
                data = data_part
                
            value += data
                
        return value
        
            


