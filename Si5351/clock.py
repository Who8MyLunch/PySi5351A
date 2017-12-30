
import numpy as np
import ordered_namespace as ons

from . import constants
from . import registers

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


