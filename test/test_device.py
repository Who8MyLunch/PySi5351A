
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

from snail import device
from snail.Si5351_Clock import registers

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



class TestSetGetItem(unittest.TestCase):
    def setUp(self):
        A = None
        P = registers.parameters
        B = None

        self.D = device.Device(A, P, B, debug=True)

    def tearDown(self):
        pass

    def test_A(self):
        for name, values in registers.parameters.items():

            val = 1
            self.D.set_parameter(name, val)

            tst_a = self.D.get_parameter(name)
            tst_b = self.D[name]

            self.assertTrue(tst_a == val, (name, tst_a, val))
            self.assertTrue(tst_a == tst_b, (name, tst_a, tst_b))


            val = 0
            self.D.set_parameter(name, val)

            tst_a = self.D.get_parameter(name)
            tst_b = self.D[name]

            self.assertTrue(tst_a == val, (name, tst_a, val))
            self.assertTrue(tst_a == tst_b, (name, tst_a, tst_b))

    def test_B(self):
        for name, values in registers.parameters.items():

            val = 1
            self.D[name] = val

            tst_a = self.D.get_parameter(name)
            tst_b = self.D[name]

            self.assertTrue(tst_a == val, (name, tst_a, val))
            self.assertTrue(tst_a == tst_b, (name, tst_a, tst_b))


            val = 0
            self.D[name] = val

            tst_a = self.D.get_parameter(name)
            tst_b = self.D[name]

            self.assertTrue(tst_a == val, (name, tst_a, val))
            self.assertTrue(tst_a == tst_b, (name, tst_a, tst_b))



#------------------------------------------------
if __name__ == '__main__':
    unittest.main(verbosity=2)
