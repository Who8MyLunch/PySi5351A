
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
    
    def rational_fractions(self):
        """See these links:
        
        https://docs.python.org/3.6/library/fractions.html#fractions.Fraction
        
        https://www.johndcook.com/blog/2010/10/20/best-rational-approximation/
        
        https://stackoverflow.com/questions/23344185/how-to-convert-a-decimal-number-into-fraction/23344270#23344270
        
        """
        
    def configure(self):
        """Write all parameters to the clock device.  Workflow based on Figure 12 from Si5153 A/B/C datasheet.
        """
        
        # Define clock off state at registers 24 and 25

        # Disable outputs
        # Set ; register 3 = 0xff
        
        # Power down all output drivers
        # registers 16-22 = 0x80
        
        # Set interrupt masks with register 2
        
        # Write clock parameters
        
        # Apply PLLA and PLLB soft reset
        # Reg 177 = 0xAC
        
        # Enable desired output at register 3
        
        
        
        
        
        