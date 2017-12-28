
import smbus2
import numpy as np

from . import constants


# look at this code for more ideas
# https://github.com/M0WUT/Python_Si5351/blob/master/Si5351_wut.py

class Si5351(object):

    def __init__(self, address=constants.I2C_ADDRESS_DEFAULT, bus_id=1):

        self.crystalFreq     = constants.CRYSTAL_FREQ_25MHZ
        self.crystalLoad     = constants.CRYSTAL_LOAD_10PF
        self.pllA_freq       = 0
        self.pllB_freq       = 0

        self._smbus = smbus2.SMBus(bus_id)
        self._address = address

        # Disable all outputs setting CLKx_DIS high
        self.write_byte(constants.REGISTER_3_OUTPUT_ENABLE_CONTROL, 0xFF)

        # Power down all output drivers
        self.write_byte(constants.REGISTER_16_CLK0_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_17_CLK1_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_18_CLK2_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_19_CLK3_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_20_CLK4_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_21_CLK5_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_22_CLK6_CONTROL, 0x80)
        self.write_byte(constants.REGISTER_23_CLK7_CONTROL, 0x80)

        # Set the load capacitance for the XTAL
        self.write_byte(constants.REGISTER_183_CRYSTAL_INTERNAL_LOAD_CAPACITANCE, self.crystalLoad)


    def write_byte(self, register, value):
        """Write a byte to designated register
        """
        self._smbus.write_byte_data(self._address, register, value)

    def read_byte(self, register):
        """Read single byte from designated register
        """
        return self._smbus.read_byte_data(self._address, register)

    def set_frequency(self, pll, output, freqMHz):
        """Set the output frequency
        """
        synthDiv = int(np.ceil(600/freqMHz))

        if(synthDiv < 6): # Si5351 requires it to be between 6 and 1800
            synthDiv += 6 - synthDiv

        if(synthDiv > 1800): # Si5351 requires it to be between 6 and 1800
            raise ValueError("synthDiv > 1800, calculated as: {}".format((synthDiv)))

        intFreq = freqMHz*synthDiv # intermediate PLL frequency
        if(intFreq > 900):
            raise ValueError("Error calculating multisynth divisor for " + str(freqMHz) + " tried " + str(synthDiv))

        pllMult = intFreq/25 # PLL multiplier as a floating point number
        pllBase = int(pllMult) # base multiplier for the PLL
        if((pllBase < 15) or (pllBase > 90)):
            raise ValueError("pllBase outside of [0,90], calculated as: " + str(pllBase))

        pllDenom = 1000000 # PLL multiplier denominator
        pllNum = int(np.modf(pllMult)[0]*pllDenom) # PLL multiplier numerator

        self.setupPLL(pll, pllBase, pllNum, pllDenom)
        self.setupMultisynth(output, pll, synthDiv)


    def setupPLL(self, pll, mult, num=0, denom=1):

        # @brief  Sets the multiplier for the specified PLL
        # @param  pll   The PLL to configure, which must be one of the following:
        #               - constants.PLL_A
        #               - constants.PLL_B
        # @param  mult  The PLL integer multiplier (must be between 15 and 90)
        # @param  num   The 20-bit numerator for fractional output (0..1,048,575).
        #               Set this to '0' for integer output.
        # @param  denom The 20-bit denominator for fractional output (1..1,048,575).
        #               Set this to '1' or higher to avoid divider by zero errors.
        # @section PLL Configuration
        #     fVCO is the PLL output, and must be between 600..900MHz, where:
        #     fVCO = fXTAL * (a+(b/c))
        #     fXTAL = the crystal input frequency
        #     a     = an integer between 15 and 90
        #     b     = the fractional numerator (0..1,048,575)
        #     c     = the fractional denominator (1..1,048,575)
        # @note Try to use integers whenever possible to avoid clock jitter
        #     (only use the a part, setting b to '0' and c to '1').
        #     See: http://www.silabs.com/Support%20Documents/TechnicalDocs/AN619.pdf
        #
        # Feedback Multisynth Divider Equation
        # where: a = mult, b = num and c = denom
        # P1[17:0] = 128 * mult + floor(128*(num/denom)) - 512
        # P2[19:0] = 128 * num - denom * floor(128*(num/denom))
        # P3[19:0] = denom

        # Set the main PLL config registers
        P1 = 128 * mult + int(128.0 * num / denom) - 512
        P2 = 128 * num - denom * int(128.0 * num / denom)
        P3 = denom

        # Get the appropriate starting point for the PLL registers
        baseaddr = 26 if pll == constants.PLL_A else 34

        # The datasheet is a nightmare of typos and inconsistencies here!
        self.write_byte(baseaddr,      (P3 & 0x0000FF00) >> 8)
        self.write_byte(baseaddr + 1,  (P3 & 0x000000FF))
        self.write_byte(baseaddr + 2,  (P1 & 0x00030000) >> 16)
        self.write_byte(baseaddr + 3,  (P1 & 0x0000FF00) >> 8)
        self.write_byte(baseaddr + 4,  (P1 & 0x000000FF))
        self.write_byte(baseaddr + 5, ((P3 & 0x000F0000) >> 12) | ((P2 & 0x000F0000) >> 16) )
        self.write_byte(baseaddr + 6,  (P2 & 0x0000FF00) >> 8)
        self.write_byte(baseaddr + 7,  (P2 & 0x000000FF))

        # Reset both PLLs
        self.write_byte(constants.REGISTER_177_PLL_RESET, (1<<7) | (1<<5))

        # Store the frequency settings for use with the Multisynth helper
        fvco = int(self.crystalFreq * (mult + float(num) / denom))
        if pll == constants.PLL_A:
            self.pllA_freq = fvco
        else:
            self.pllB_freq = fvco


    def setupRdiv(self, output, div):

        if output == 0:
            Rreg = constants.REGISTER_44_MULTISYNTH0_PARAMETERS_3
        if output == 1:
            Rreg = constants.REGISTER_52_MULTISYNTH1_PARAMETERS_3
        if output == 2:
            Rreg = constants.REGISTER_60_MULTISYNTH2_PARAMETERS_3

        return self.write_byte(Rreg, (div & 0x07) << 4)


    def setupMultisynth(self, output, pll, div, num=0, denom=1):

        # @brief  Configures the Multisynth divider, which determines the
        #         output clock frequency based on the specified PLL input.
        #
        # @param  output    The output channel to use (0..2)
        # @param  pll       The PLL input source to use, which must be one of:
        #                   - constants.PLL_A
        #                   - constants.PLL_B
        # @param  div       The integer divider for the Multisynth output.
        #                   If pure integer values are used, this value must
        #                   be one of:
        #                   - constants.MULTISYNTH_DIV_4
        #                   - constants.MULTISYNTH_DIV_6
        #                   - constants.MULTISYNTH_DIV_8
        #                   If fractional output is used, this value must be
        #                   between 8 and 900.
        # @param  num       The 20-bit numerator for fractional output
        #                   (0..1,048,575). Set this to '0' for integer output.
        # @param  denom     The 20-bit denominator for fractional output
        #                   (1..1,048,575). Set this to '1' or higher to
        #                   avoid divide by zero errors.
        #
        # @section Output Clock Configuration
        #
        # The multisynth dividers are applied to the specified PLL output,
        # and are used to reduce the PLL output to a valid range (500kHz
        # to 160MHz). The relationship can be seen in this formula, where
        # fVCO is the PLL output frequency and MSx is the multisynth
        # divider:
        #     fOUT = fVCO / MSx
        # Valid multisynth dividers are 4, 6, or 8 when using integers,
        # or any fractional values between 8 + 1/1,048,575 and 900 + 0/1
        # The following formula is used for the fractional mode divider:
        #     a + b / c
        # a = The integer value, which must be 4, 6 or 8 in integer mode (MSx_INT=1)
        #     or 8..900 in fractional mode (MSx_INT=0).
        # b = The fractional numerator (0..1,048,575)
        # c = The fractional denominator (1..1,048,575)
        # @note   Try to use integers whenever possible to avoid clock jitter
        # @note   For output frequencies > 150MHz, you must set the divider
        #         to 4 and adjust to PLL to generate the frequency (for example
        #         a PLL of 640 to generate a 160MHz output clock). This is not
        #         yet supported in the driver, which limits frequencies to
        #         500kHz .. 150MHz.
        # @note   For frequencies below 500kHz (down to 8kHz) Rx_DIV must be
        #         used, but this isn't currently implemented in the driver.
        #
        # Output Multisynth Divider Equations
        # where: a = div, b = num and c = denom
        # P1[17:0] = 128 * a + floor(128*(b/c)) - 512
        # P2[19:0] = 128 * b - c * floor(128*(b/c))
        # P3[19:0] = c

        # Set the main PLL config registers
        P1 = 128 * div + int(128.0 * num / denom) - 512
        P2 = 128 * num - denom * int(128.0 * num / denom)
        P3 = denom

        # Get the appropriate starting point for the PLL registers
        if output == 0:
            baseaddr = constants.REGISTER_42_MULTISYNTH0_PARAMETERS_1
        if output == 1:
            baseaddr = constants.REGISTER_50_MULTISYNTH1_PARAMETERS_1
        if output == 2:
            baseaddr = constants.REGISTER_58_MULTISYNTH2_PARAMETERS_1

        # Set the MSx config registers
        self.write_byte(baseaddr,      (P3 & 0x0000FF00) >> 8)
        self.write_byte(baseaddr + 1,  (P3 & 0x000000FF))
        self.write_byte(baseaddr + 2,  (P1 & 0x00030000) >> 16)  # ToDo: Add DIVBY4 (>150MHz) and R0 support (<500kHz) later
        self.write_byte(baseaddr + 3,  (P1 & 0x0000FF00) >> 8)
        self.write_byte(baseaddr + 4,  (P1 & 0x000000FF))
        self.write_byte(baseaddr + 5, ((P3 & 0x000F0000) >> 12) | ((P2 & 0x000F0000) >> 16) )
        self.write_byte(baseaddr + 6,  (P2 & 0x0000FF00) >> 8)
        self.write_byte(baseaddr + 7,  (P2 & 0x000000FF))

        # Configure the clk control and enable the output
        # 8mA drive strength, MS0 as CLK0 source, Clock not inverted, powered up
        clkControlReg = 0x0F
        if pll == constants.PLL_B:
            clkControlReg |= (1 << 5)   # Uses PLLB

        if num == 0:
            # Integer mode
            clkControlReg |= (1 << 6)

        if output == 0:
            self.write_byte(constants.REGISTER_16_CLK0_CONTROL, clkControlReg)
        if output == 1:
            self.write_byte(constants.REGISTER_17_CLK1_CONTROL, clkControlReg)
        if output == 2:
            self.write_byte(constants.REGISTER_18_CLK2_CONTROL, clkControlReg)


    def enableOutputs(self, enabled):

        # Enabled desired outputs (see Register 3)
        val = 0x00 if enabled else 0xFF
        self.write_byte(constants.REGISTER_3_OUTPUT_ENABLE_CONTROL, val)

#------------------------------------------------

def fraction_solve(x0):
    """Return numerator and denominator for best expression for the decimal x0 (0<x0<1)
    """
    if(x0 < 0 or x0 > 1):
        raise Exception("Decimal supplied (x) must satisfy 0 < x < 1")

    err = 1e-10

    g = abs(x0)

    a = 0.0
    b = 1.0
    c = 1.0
    d = 0.0
    s = 0.0

    count = 0

    while count < 1000:
        s = np.floor(g)
        num = a + s*c
        den = b + s*d

        a = c
        b = d
        c = num
        d = den

        try:
            g = 1/(g - s)

        except ZeroDivisionError:
            # g=s at very very close solutions so will terminate next time
            g = g

        if (abs((num/den) - x0) < err):
            if (b > 1048575 or c > 1048575):
                raise Exception("Produced values for fraction out of specified range")

            return (num, den)

        count += 1

    #Have tried a thousand times, give up (most values this was run on returned within 20 iterations
    raise Exception("Could not find adequate results to express {:f} as a fraction".format(x0))
#------------------------------------------------

if __name__ == '__main__':
    si = Si5351()

    print("Set Output #0 to 13.703704 MHz")

    # vco = 25 MHz * (24 + 2 / 3) = 616.67 MHz
    si.setupPLL(si.PLL_A, 24, 2, 3)
    # out = 616.67 MHz / 45 = 13.703704 MHz
    si.setupMultisynth(0, si.PLL_A, 45)
    # si.setupRdiv(0, si.R_DIV_64)
    si.enableOutputs(True)

