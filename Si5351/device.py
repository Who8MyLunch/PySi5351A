
import numpy as np
import bitstruct as bs
import smbus2

# Helper functions
def _bitfield_parser(MSB, LSB, width=8):
    """Generate a compiled bitfield packer/unpacker.  Uses package bitstruct.
    """
    N_lead = width - MSB - 1
    N_data = MSB - LSB + 1
    N_trail = LSB

    fmt = 'p{:d}u{:d}p{:d}'.format(N_lead, N_data, N_trail)

    cfmt = bs.compile(fmt)

    return cfmt


# Main event
class Device():
    """Manage bits and bytes IO with a specific I32C/SMBus device
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
        for item in self._parameter[name]:
            r = item['register']

            b = self.read_byte(r)



