
from __future__ import division, print_function, unicode_literals, absolute_import

import setuptools


version = '2017.12.27'

dependencies = ['smbus2']


setuptools.setup(install_requires=dependencies,
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 version=version)
