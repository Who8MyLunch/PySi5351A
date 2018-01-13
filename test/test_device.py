
from __future__ import division, print_function, unicode_literals

"""
Test Examples
=============


## Python Tests
self.assertTrue(value)
self.assertFalse(value)

self.assertGreater(first, second, msg=None)
self.assertGreaterEqual(first, second, msg=None)
self.assertLess(first, second, msg=None)
self.assertLessEqual(first, second, msg=None)

self.assertAlmostEqual(first, second, places=7, msg=None, delta=None)
self.assertNotAlmostEqual(first, second, places=7, msg=None, delta=None)

self.assertItemsEqual(actual, expected, msg=None)
self.assertSequenceEqual(seq1, seq2, msg=None, seq_type=None)
self.assertListEqual(list1, list2, msg=None)
self.assertTupleEqual(tuple1, tuple2, msg=None)
self.assertSetEqual(set1, set2, msg=None)
self.assertDictEqual(expected, actual, msg=None)

self.assertRaises(Exception, some_func, arg, arg_nother)

"""

import unittest
import os
import pathlib

import context

from Si5351 import device
from Si5351 import registers_Si5351 as registers

_path_module = pathlib.Path(__file__).parent.absolute()


#------------------------------------------------

class TestDeviceParameters(unittest.TestCase):
    def setUp(self):
        A = None
        P = registers.parameters
        B = None
        
        self.D = device.Device(A, P, B, debug=True)

    def tearDown(self):
        pass

    def test_set_zero_a(self):
        val = 0
        for name, values in registers.parameters.items():
            self.D.set_parameter(name, val)
               
    def test_set_get_zero(self):
        val = 0
        for name, values in registers.parameters.items():
            self.D.set_parameter(name, 0)
            tst = self.D.get_parameter(name)            
            self.assertTrue(tst == val, (name, tst, val))

    def test_set_get_one(self):
        val = 1
        for name, values in registers.parameters.items():
            self.D.set_parameter(name, val)
            tst = self.D.get_parameter(name)            
            self.assertTrue(tst == val, (name, tst, val))

    def test_set_get_max(self):
        for name, values in registers.parameters.items():
            MSB = 0
            for r in values:
                t = r['reg_MSB'] - r['reg_LSB'] 
                if t > MSB:
                    MSB = t
            val = 2**(MSB+1) - 1

            self.D.set_parameter(name, val)
            tst = self.D.get_parameter(name)            
            self.assertTrue(tst == val, (name, tst, val))

                    



#------------------------------------------------
if __name__ == '__main__':
    unittest.main(verbosity=2)
