
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

_path_module = pathlib.Path(__file__).parent.absolute()


#------------------------------------------------

class TestPack(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pack_bits_a(self):
        dat = 0
        MSB = 0
        LSB = 0
        
        val = 0
        tst = device.pack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_pack_bits_b(self):
        dat = 1
        MSB = 1
        LSB = 1

        val = 0b10
        tst = device.pack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_pack_bits_c(self):
        dat = 1
        MSB = 2
        LSB = 1
        
        val = 0b10
        tst = device.pack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_pack_bits_d(self):
        dat = 1
        MSB = 7
        LSB = 7

        val = 0b000010000000   # 128
        tst = device.pack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_pack_bits_e(self):
        dat = 2
        MSB = 12
        LSB = 6

        val = 0b000010000000   # 128
        tst = device.pack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_pack_bits_f(self):
        dat = 3
        MSB = 12
        LSB = 6

        val = 0b000011000000   # 128 + 64
        tst = device.pack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))


        
class TestUnpack(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_unpack_bits_a(self):
        dat = 0
        MSB = 0
        LSB = 0
        
        val = 0
        tst = device.unpack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_unpack_bits_b(self):
        dat = 128
        MSB = 100
        LSB = 6
        
        val = 0b10
        tst = device.unpack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_unpack_bits_c(self):
        dat = 0b10000000
        MSB = 100
        LSB = 7
        
        val = 1
        tst = device.unpack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_unpack_bits_d(self):
        dat = 0b10101010
        MSB = 7
        LSB = 5
        
        val = 0b00000101
        tst = device.unpack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))

    def test_unpack_bits_e(self):
        dat = 0b10110101
        MSB = 7
        LSB = 5

        val = 0b00000101
        tst = device.unpack_bits(dat, MSB, LSB)
        
        self.assertTrue(tst == val, (tst, val))



class TestPackUnpack(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_round_trip(self):
        dat = 0b00000101

        MSB = 5
        LSB = 3

        val = 0b00101000
        packed = device.pack_bits(dat, MSB, LSB)
        self.assertTrue(packed == val, (packed, val))
        
        unpacked = device.unpack_bits(packed, MSB, LSB)
        self.assertTrue(dat == unpacked, (dat, unpacked))

        
#------------------------------------------------
if __name__ == '__main__':
    unittest.main(verbosity=2)
