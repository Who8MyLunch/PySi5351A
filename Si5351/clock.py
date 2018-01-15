
import numpy as np
import ordered_namespace as ons

from . import device
from . import registers_Si5351
from . import clock_defaults as defaults


            
class Clock(device.Device):
    """Device: Si5351 ABC
    """
    def __init__(self, bus):
        """Instantiate device with register data for Si5351 clock generator
        """
        super().__init__(registers_Si5351.address, registers_Si5351.parameters, bus)
        
    def status_SYS(self):
        """Return device system status information
        """
        names = ['SYS_INIT', 'CLKIN_DIV', 'XTAL_CL', 'SSC_EN', 'CLKIN_FANOUT_EN', 'XO_FANOUT_EN', 'MS_FANOUT_EN'] 
        
        for n in names:
            print('{:15s}: {}'.format(n, self[n]))
    
    def status_PLL(self, x='A'):
        """Return device PLL status information
        """
        names = ['LOL_{}', 'PLL{}_SRC', 'MSN{}_P1', 'MSN{}_P2', 'MSN{}_P3', 'FB{}_INT']        
        for n in names:
            n = n.format(x)
            print('{:15s}: {}'.format(n, self[n]))
    
    def status_MS(self, x=0):
        """Return device multisynth status information
        """
        names = ['MS{}_SRC', 'MS{}_P1', 'MS{}_P2', 'MS{}_P3', 'MS{}_INT', 'MS{}_DIVBY4', 'R{}_DIV']
        
        for n in names:
            n = n.format(x)
            print('{:15s}: {}'.format(n, self[n]))
    
    def status_CLK(self, x=0):
        """Return device clock status information
        """
        names = ['CLK{}_PDN', 'CLK{}_OEB', 'CLK{}_SRC',
                 'CLK{}_PHOFF', 'CLK{}_IDRV', 'CLK{}_INV', 'CLK{}_DIS_STATE']

        for n in names:
            n = n.format(x)
            print('{:15s}: {}'.format(n, self[n]))
    
    def set_SYS(self):
        XTAL_CL = 3
        CLKIN_DIV
        
        
    def rational_fractions(self):
        """See these links:
        
        https://docs.python.org/3.6/library/fractions.html#fractions.Fraction
        
        https://www.johndcook.com/blog/2010/10/20/best-rational-approximation/
        
        https://stackoverflow.com/questions/23344185/how-to-convert-a-decimal-number-into-fraction/23344270#23344270
        
        """
        pass
        
    def initialize(self):
        """Initialize device
        """
        pass
        
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
        
        
    def shutdown(self):
        """shutdown device
        """
        pass

        
if __name__ == '__main__':
    pass

        