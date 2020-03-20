import unittest
import logging
import datetime
import math

from prg1.utils.time_conversions import frac_to_time, time_to_frac


logger = logging.getLogger(__name__)


class DailyFractalTestCase(unittest.TestCase):
    """
    Implementing Example from:
    https://de.wikipedia.org/wiki/Tagesbruchteil
    """

    def setUp(self):
        self.fractal = 0.25420668
        self.time = datetime.time(hour=6, minute=6, microsecond=3457)

    def test_frac_to_time(self):
        time = frac_to_time(self.fractal)
        dt0 = datetime.datetime(2015, 3, 11, self.time.hour, self.time.minute, self.time.second)
        dt1 = datetime.datetime(2015, 3, 11, time.hour, time.minute, time.second)
        dt = dt0 - dt1
        #print(dt.total_seconds()*1000)
        self.assertTrue(dt.total_seconds() < 1e-4)

    def test_time_to_frac(self):
        fractal = time_to_frac(self.time)
        df = self.fractal - fractal
        self.assertTrue(math.fabs(df) < 5e-5)
