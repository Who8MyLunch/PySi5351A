
import numpy as np

from .. import device
from .  import registers
from .  import constants


            
class Clock(device.Device):
    """Device: Si5351 A/B/C
    """
    def __init__(self, bus=1):
        """Instantiate device with register data for Si5351 clock generator
        """
        super().__init__(registers.address, registers.parameters, bus)
        
    def status(self):
        """Print all status information
        """
        print()
        self.status_SYS()

        for PLL in ['A', 'B']:
            print()
            self.status_PLL(PLL)

        print()
        for MS in range(3):
            print()
            self.status_MS(MS)
        
        print()
        for CLK in range(3):
            print()
            self.status_CLK(CLK)


    def status_SYS(self):
        """Return device system status information
        """
        names = ['SYS_INIT', 'CLKIN_DIV', 'XTAL_CL', 'SSC_EN',
                 'CLKIN_FANOUT_EN', 'XO_FANOUT_EN', 'MS_FANOUT_EN'] 
        
        for n in names:
            print('{:15s}: {}'.format(n, self[n]))
    
    def status_PLL(self, x='A'):
        """Return device PLL status information.
        x = 'A' or 'B'
        """
        names = ['LOL_{}', 'PLL{}_SRC', 'MSN{}_P1', 'MSN{}_P2', 'MSN{}_P3', 'FB{}_INT']        
        for n in names:
            n = n.format(x)
            print('{:15s}: {}'.format(n, self[n]))
    
    def status_MS(self, x=0):
        """Return device multisynth status information
        x = 0, or 1, ... or ... 7
        """
        if 0 <= x and x <= 5:
            names = ['MS{}_SRC', 'MS{}_P1', 'MS{}_P2', 'MS{}_P3',
                     'MS{}_INT', 'MS{}_DIVBY4', 'R{}_DIV']
        elif 6 <= x and x <= 7:
            names = ['MS{}_SRC', 'MS{}_P1', 'R{}_DIV']
        else:
            raise ValueError('Invalid x: {}'.format(x))
        
        for n in names:
            n = n.format(x)
            print('{:15s}: {}'.format(n, self[n]))
    
    def status_CLK(self, x=0):
        """Return device clock status information
        x = 0, or 1, ... or ... 7
        """
        if 0 <= x and x <= 5:
            names = ['CLK{}_PDN', 'CLK{}_OEB', 'CLK{}_SRC',
                     'CLK{}_PHOFF', 'CLK{}_IDRV', 'CLK{}_INV', 'CLK{}_DIS_STATE']
        elif 6 <= x and x <= 7:
            names = ['CLK{}_PDN', 'CLK{}_OEB', 'CLK{}_SRC',
                     'CLK{}_IDRV', 'CLK{}_INV', 'CLK{}_DIS_STATE']
        else:
            raise ValueError('Invalid x: {}'.format(x))
        

        
        for n in names:
            n = n.format(x)
            print('{:15s}: {}'.format(n, self[n]))
    
    def rational_fractions(self):
        """See these links:
        
        https://docs.python.org/3.6/library/fractions.html#fractions.Fraction
        
        https://www.johndcook.com/blog/2010/10/20/best-rational-approximation/
        
        https://stackoverflow.com/questions/23344185/how-to-convert-a-decimal-number-into-fraction/23344270#23344270
        
        """
        pass
        
    @property
    def parameter_names(self):
        names = list(self._parameters.keys())
        names.sort()
        return names
        
    def initialize(self):
        """Initialize device to default values
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

    
    
class Multiplier():
    """Manage multipler (and divider) calculations and configuration.
    Compute values for register parameters P1, P2, and P3.
    """
    def __init__(self):
        self._P1 = None
        self._P2 = None
        self._P3 = None
        
    @property
    def P1(self):
        return self._P1
    
    @property
    def P2(self):
        return self._P2
    
    @property
    def P3(self):
        return self._P3
    
    @property
    def is_integer(self):
        """Return True if multiplier value is an even integer
        """
    
    
        
        
class PLL():
    """Helper class
    """
    def __init__(self, si5351):
        self._si5351 = si5351



class CLK():
    """Helper class
    """
    def __init__(self, si5351, PLL):
        self._si5351 = si5351
        self._PLL = PLL
    

#------------------------------------------
if __name__ == '__main__':
    pass
