import unittest
import logging
import math
import os
import pprint
import datetime

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
            m0=math.radians(251.7436),
            a=6723842.235,
            e=0.0008835,
            omega=math.radians(122.3522),
            i=math.radians(51.6448),
            w=math.radians(257.3473)
        )
        self.timestamp = datetime.datetime(2006, 2, 9, 20, 26, 0)

    def test_file_read(self):
        with open(self.test_file, "r") as tle:
            tle_str = "".join(tle.readlines())
            tle = KeplerElementSet.read_tle(tle_str)
            kepler_element_set = KeplerElementSet.from_dict(tle)
            # print("\n\n", kepler_element_set)
            # self.assertTrue(math.fabs(tle["major_axis"] - self.kepler_element_set.a) <= 1e-3)
            self.assertAlmostEqual(self.kepler_element_set.i, kepler_element_set.i, places=4)
            self.assertAlmostEqual(self.kepler_element_set.a, kepler_element_set.a, places=3)
