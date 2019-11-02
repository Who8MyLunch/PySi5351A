
import numpy as np

from .. import device
from .  import registers
from .  import constants
from .rational import rational_approximation


            
class Clock(device.Device):
    """Device: Si5351 A/B/C
    """
    def __init__(self, bus=1):
        """Instantiate device with register data for Si5351 clock generator
        """
        super().__init__(registers.address, registers.parameters, bus)
        self.f_XTAL = 25e6
        self.f_PLL = {'A': 0,
                      'B': 0}
        self.f_MS = {0: 0,
                     1: 0,
                     2: 0,
                     3: 0,
                     4: 0,
                     5: 0,
                     6: 0,
                     7: 0}
        
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
    
    def status_MS(self, x):
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
    
    def status_CLK(self, x):
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
            
    @property
    def parameter_names(self):
        names = list(self._parameters.keys())
        names.sort()
        return names
        
    def reset(self):
        """Configure device to default values with all outputs disabled
        """
        # Specify clock state when its disabled
        self['CLK0_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK1_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK2_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK3_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK4_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK5_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK6_DIS_STATE'] = constants.CLK_DIS_STATE_LOW
        self['CLK7_DIS_STATE'] = constants.CLK_DIS_STATE_LOW

        # Disable all clocks
        self['CLK0_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK1_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK2_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK3_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK4_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK5_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK6_OEB'] = constants.CLK_OEB_DISABLE
        self['CLK7_OEB'] = constants.CLK_OEB_DISABLE

        # Power down all output drivers
        self['CLK0_PDN'] = constants.CLK_PDN_OFF
        self['CLK1_PDN'] = constants.CLK_PDN_OFF
        self['CLK2_PDN'] = constants.CLK_PDN_OFF
        self['CLK3_PDN'] = constants.CLK_PDN_OFF
        self['CLK4_PDN'] = constants.CLK_PDN_OFF
        self['CLK5_PDN'] = constants.CLK_PDN_OFF
        self['CLK6_PDN'] = constants.CLK_PDN_OFF
        self['CLK7_PDN'] = constants.CLK_PDN_OFF

        # Set interrupt masks to null thus allowing all asserts to go through
        self['SYS_INIT_MASK'] = 0
        self['LOL_A_MASK'] = 0
        self['LOL_B_MASK'] = 0
        self['LOS_MASK'] = 0 

        # Fanout options
        self['CLKIN_FANOUT_EN'] = constants.FANOUT_DISABLE
        self['XO_FANOUT_EN'] =    constants.FANOUT_DISABLE
        self['MS_FANOUT_EN'] =    constants.FANOUT_DISABLE

    def config_input(self):
        """Configure clock/XTAL input parameters
        """
        # Crystal's internal load capacitance
        self['XTAL_CL'] = constants.XTAL_CL_10PF   # XTAL_CL_6PF, _8PF, or *_10PF*

        # Input clock frequency divider
        self['CLKIN_DIV'] = constants.CLKIN_DIV_1  # CLKIN_DIV_1, _2, _4, _8
        
    def config_PLL(self, f_PLL, PLL='A', src='XTAL', force_integer=False):
        """PLL configuration steps:
        - Input signal to PLL is XTAL (5351a) or CLKIN (5351a/c)
        - Compute a, b, c (and P1, P2, P3)
        - Write to P1, P2, P3 registers
        
        f_PLL : desired PLL output frequency
        """
        key = 'PLL{:s}_SRC'.format(PLL)

        if src.upper() == 'XTAL':
            self[key] = constants.PLL_SRC_XTAL
        elif src.upper() == 'CLKIN':
            self[key] = constants.PLL_SRC_CLKIN

        M_PLL = f_PLL/self.f_XTAL
        a, b, c = compute_abc(M_PLL)
        f_PLL_set = (a + b/c)*self.f_XTAL

        self.f_PLL[PLL.upper()] = f_PLL_set

        tpl = 'MSN{:s}_P{:d}'
        for k, P in enumerate(encode_abc(a, b, c)):
            key = tpl.format(PLL, k+1)
            self[key] = P

        # Even integer?
        key = 'FB{:s}_INT'.format(PLL)
        if b == 0 and not (a % 2):
            # Yes
            self[key] = 1
        else:
            # No
            self[key] = 0
        
    def config_MS(self, f_MS, MS, src_PLL='A'):
        """Configure specified MultiSynth
        - Input PLL
        - Divide by 4 (No!)
        - Conifg MS output frequency        
        """
        # Source PLL
        if src_PLL.upper() == 'A':
            MS_SRC = constants.MS_SRC_PLL_A
        elif src_PLL.upper() == 'B':
            MS_SRC = constants.MS_SRC_PLL_B            
        else:
            raise ValueError('Invalid PLL: {}'.format(src_PLL))
            
        key = 'MS{:d}_SRC'.format(MS)
        self[key] = MS_SRC
    
        # Divide by 4?  Nope!
        if MS <= 5:
            key = 'MS{:d}_DIVBY4'.format(MS)
            self[key] = constants.MS_DIVBY4_DISABLE

        # MS output frequency, f_MS
        f_PLL = self.f_PLL[src_PLL.upper()]
        M_MS = f_PLL/f_MS

        a, b, c = compute_abc(M_MS)
        f_MS_set = f_PLL/(a + b/c)
        
        self.f_MS[MS] = f_MS_set
        
        tpl = 'MS{:d}_P{:d}'
        for k, P in enumerate(encode_abc(a, b, c)):
            key = tpl.format(MS, k+1)
            self[key] = P
        
        # Even integer?
        key = 'MS{:d}_INT'.format(MS)
        if b == 0 and not (a % 2):
            # Yes
            self[key] = 1
        else:
            # No
            self[key] = 0

    def config_CLK(self, ix_CLK):
        """CLK source: match output CLK with corresponding Stage-2 MultiSynth divider.
        More complicated options are available.
        """
        key = 'CLK{:d}_SRC'.format(ix_CLK)
        self[key] = constants.CLK_SRC_MS
        
        key = 'CLK{:d}_INV'.format(ix_CLK)
        self[key] = constants.CLK_INV_FALSE
    
        # Clock drive current (what's the best setting here?)
        key = 'CLK{:d}_IDRV'.format(ix_CLK)
        self[key] = constants.CLK_IDRV_2
    
        # Initial phase values
        key = 'CLK{:d}_PHOFF'.format(ix_CLK)
        self[key] = constants.CLK_PHOFF_ZERO

        # C['CLK6_PHOFF'] = clock.constants.CLK_PHOFF_ZERO  # does not exist
        # C['CLK7_PHOFF'] = clock.constants.CLK_PHOFF_ZERO  # does not exist

        # Clock final divide (unity)
        key = 'R{:d}_DIV'.format(ix_CLK)
        self[key] = constants.R_DIV_1
    
    def soft_reset_PLL(self, s_PLL):
        key = 'PLL{:s}_RST'.format(s_PLL)
        self[key] = 1
        
    def enable_output(self, ix_CLK):
        # Power on
        key = 'CLK{:d}_PDN'.format(ix_CLK)
        self[key] = constants.CLK_PDN_ON
        
        # Clock signal enabled
        key = 'CLK{:d}_OEB'.format(ix_CLK)
        self[key] = constants.CLK_PDN_ON

#---------------------------------------------------------------

def compute_abc(value):
    """Decompse supplied value as integers: a + b/c
    """
    eps = 1e-10
    
    a = int(value)
    if abs(value - a) < eps:
        # Easy
        b = 0
        c = 1
    else:
        # Rational fractions approximation
        lohi_b = [0, 2**20]
        lohi_c = [1, 2**20]

        b, c = rational_approximation((value-a), lohi_num=lohi_b, lohi_den=lohi_c)
    
    return a, b, c
    
def encode_abc(a, b, c):
    """Encode a, b, and c parameters as P1, P2, and P3 register values
    """
    P1 = 128*a + np.floor(128*b/c) - 512
    P2 = 128*b - c*np.floor(128*b/c)
    P3 = c
    
    P1 = int(P1)
    P2 = int(P2)
    P3 = int(P3)
    
    return P1, P2, P3

#------------------------------------------
if __name__ == '__main__':
    pass
