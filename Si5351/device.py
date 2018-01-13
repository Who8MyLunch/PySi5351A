
import smbus2
import numpy as np

#--------------------------------------------------------------------
# Helper functions
def check_bits(parameters):
    for name, values in parameters.items():
        for item in values:
            if item['reg_MSB'] < 0:
                raise ValueError('{} reg_MSB cannot be negative: {}'.format(name, item['reg_MSB']))
            if item['reg_LSB'] < 0:
                raise ValueError('{} reg_LSB cannot be negative: {}'.format(name, item['reg_LSB']))
            if item['reg_MSB'] < item['reg_LSB']:
                raise ValueError('{} reg_MSB cannot be less than reg_LSB: {}, {}'.format(name, item['reg_MSB'], item['reg_LSB']))                
            d_reg = item['reg_MSB'] - item['reg_LSB']
            try:
                d_dat = item['dat_MSB'] - item['dat_LSB']

                if item['dat_MSB'] < 0:
                    raise ValueError('{} dat_MSB cannot be negative: {}'.format(name, item['dat_MSB']))
                if item['dat_LSB'] < 0:
                    raise ValueError('{} dat_LSB cannot be negative: {}'.format(name, item['dat_LSB']))
                if item['dat_MSB'] < item['dat_LSB']:
                    raise ValueError('{} dat_MSB cannot be less than dat_LSB: {}, {}'.format(name, item['dat_MSB'], item['dat_LSB']))
                if d_dat != d_reg:
                        raise ValueError('Bit fields are different sizes {}: {} vs {} [{}]'.format(name, d_reg, d_dat, item))

            except KeyError:
                pass

            
            
def number_of_bits(value):
    """Return number of bits required to represent the provided number
    """
    value = int(value)
    if value == 0:
        return 0
    else:
        return np.floor(np.log2(value) + 1)


    
def number_of_bytes(value):
    """Return number of bytes required to represent the provided number
    """
    value = int(value)
    if value == 0:
        return 0
    else:
        return np.ceil(number_of_bits(value)/8)



def mask(MSB, LSB):
    """Create mask to select bits between LSB and MSB (inclusive)
    """
    if MSB < 0:
        raise ValueError('MSB cannot be negative: {}, {}'.format(MSB, LSB))

    mask_p = (1 << MSB+1) - 1
    mask_q = (1 << LSB  ) - 1
    
    return mask_p & ~mask_q



def pack_bits(data_bits, MSB, LSB):
    """Pack unsigned-integer data value into zero-padded bitfield
    """
    if data_bits < 0:
        raise ValueError('data_bits must be non-negative: {}'.format(data_bits))
        
    if data_bits == 0:
        return 0

    data_shifted = data_bits << LSB
    data_binary = data_shifted & mask(MSB, LSB)
    
    return data_binary



def unpack_bits(data_binary, MSB, LSB):
    """Extract bits between MSB and LSB (inclusive)
    """
    if data_binary < 0:
        raise ValueError('data_binary must be non-negative: {}'.format(data_binary))
        
    if data_binary == 0:
        return 0
    
    data_masked = data_binary & mask(MSB, LSB)
    data_bits = data_masked >> LSB
    
    return data_bits


def check_byte_value(val):
    if val < 0:
        raise ValueError('Byte value may not be negative: {}'.format(val))
        
    if val > 255:
        raise ValueError('Byte value may not be greater than 255: {}'.format(val))
            


#----------------------------------------------------------------------


class Device():
    """Manage data parameters with I2C/SMBus device
    """
    def __init__(self, address, parameters, bus, debug=False):
        """Instantiate device manager
        """
        self._debug = debug
        self._address = address

        check_bits(parameters)
        self._ingest_parameters(parameters)
        check_bits(self._parameters)

        if self._debug:
            self._smbus = None

            N = 500  # max. number of registers
            self._cache = np.zeros(N, dtype=np.uint8)
        else:
            self._smbus = smbus2.SMBus(bus)
            self._cache = None

    def _ingest_parameters(self, parameters):
        """Process provided device parameters, store internally.
        Also check for missing data MSB/LSB values (that's OK) and compute default values
        assuming LSB = 0 and MSB is derived from required register LSB/MSB values.
        """
        self._parameters = {}
        
        # Loop over data parameters
        for name, values in parameters.items():
            self._parameters[name] = []
            # Loop over device registers associated with this parameter
            for R in values:
                register = {}
                register.update(R)

                if not 'dat_LSB' in register:
                    # Compute default data LSB/MSB based on register storage values
                    register['dat_MSB'] = R['reg_MSB'] - R['reg_LSB']
                    register['dat_LSB'] = 0
                    
                self._parameters[name].append(register)

    def write_byte(self, register, data_byte):
        """Write a byte to designated register
        """
        check_byte_value(data_byte)
            
        if self._debug:
            self._cache[register] = data_byte
        else:
            self._smbus.write_byte_data(self._address, register, data_byte)

    def read_byte(self, register):
        """Read a byte from designated register
        """
        if self._debug:
            return self._cache[register]
        else:
            return self._smbus.read_byte_data(self._address, register)

    def get_parameter(self, name):
        """Extract parameter value from device register(s)
        """
        value = 0
        for register in self._parameters[name]:
            data_reg_byte = self.read_byte(register['register'])
            
            data_intermed = unpack_bits(data_reg_byte, register['reg_MSB'], register['reg_LSB'])

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
            self.write_byte(register['register'], data_reg_byte)
            
    def __setitem__(self, name, value):
        self.set_parameter(name, value)
        
    def __getitem__(self, name):
        return self.get_parameter(name)
        
#---------------------------------------------------
if __name__ == '__main__':
    pass
