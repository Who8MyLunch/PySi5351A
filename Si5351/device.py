
import bitstruct as bs
import smbus2

from .memoize import Memoize

@Memoize
def _bitfield_packer(MSB, LSB):
    """Generate a compiled bitfield packer/unpacker.  Uses package bitstruct.
    """
    width = int(np.ceil(MSB/8)*8)
    
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
        """Read a byte from designated register
        """
        return self._smbus.read_byte_data(self._address, register)

    def read_parameter(self, name):
        """Extract parameter value from device register
        """
        value = 0
        for item in self._parameters[name]:
            print()
            print(item['register'])

            data_raw = self.read_byte(item['register'])
            
            packer = _bitfield_packer(item['reg_MSB'], item['reg_LSB'])
            data_bits = packer.unpack([data_raw])[0]
            
            if 'dat_LSB' in item:
                packer = _bitfield_packer(item['dat_MSB'], item['dat_LSB'])
                buff = packer.pack(data_bits)
                
                # https://stackoverflow.com/questions/444591/convert-a-string-of-bytes-into-an-int-python
                data = int.from_bytes(buff, 'big')
                
#                 data = np.frombuffer(buff, dtype=np.uint8)[0]
                
                print(data_raw, data_bits, data)
            else:
                print(0)
                data = data_part
                
            value += data
                
        return value
        
            


