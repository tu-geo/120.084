import unittest
import logging
import math
import os
import pprint

from prg1.models.kepler_element_set import KeplerElementSet
from prg1.models.nuisance_parameter_set import NuisanceParameterSet
from prg1.utils.constants import GE


logger = logging.getLogger(__name__)


class NoradImportTestCase(unittest.TestCase):
    """
    Implementing Example from:
    https://de.wikipedia.org/wiki/Satellitenbahnelement#Das_Two_Line_Elements_Format_TLE
    """

    def setUp(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.test_file = os.path.join(this_dir, "__norad_25544.txt")
        self.kepler_element_set = KeplerElementSet(
            m0=251.7436,
            a=6723842.235,
            e=0.0008835,
            omega=122.3522,
            i=51.6448,
            w=257.3473
        )

    def test_file_read(self):
        with open(self.test_file, "r") as tle:
            tle_str = "".join(tle.readlines())
            tle = KeplerElementSet.read_tle(tle_str)

            print("\n\n{}\n".format(tle_str))
            pprint.pprint(tle)

            major_axis = math.pow(GE/math.pow(tle["mean_motion"]*2*math.pi/86400, 2), 1.0/3.0)
            print("a: {}".format(major_axis))

            self.assertTrue(False)