
import numpy as np
import ordered_namespace as ons

from . import device
from . import registers_Si5351

#------------------------------------------------
# Helper functions

def check_bits(parameters):
    """Consistency check
    """
    for name, values in parameters.items():
        for item in values:
            item = ons.Struct(item)
            d_reg = item.reg_MSB - item.reg_LSB
            try:
                d_dat = item.dat_MSB - item.dat_LSB

                if d_dat != d_reg:
                    raise ValueError('Bit fields are different sizes: {} {} vs {}'.fornat(name, d_reg, d_dat))

            except KeyError:
                pass



            
class Clock(device.Device):
    """Device: Si5351A/B/C
    """
    def __init__(self, bus):
        """Instantiate device with register data for Si5351 clock generator
        """
        super().__init__(registers_Si5351.address, registers_Si5351.parameters, bus)
        
    def status(self):
        """Return device status information
        """
        SYS_INIT
        LOS for CLKIN
        LOL for PLL_A and PLL_B
        
        CLKx_OEB
        CLKx_PDN for power down status
        
        PLLA_SRC
        PLLB_SRC
        
        
        