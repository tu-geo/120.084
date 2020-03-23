import unittest
import logging
import math
import datetime

from prg1.models.point import GeocentricPoint
from prg1.models.kepler_element_set import KeplerElementSet
from prg1.models.nuisance_parameter_set import NuisanceParameterSet
from prg1.utils.orbit_to_cart import orbit_to_cart


logger = logging.getLogger(__name__)


class OrbitalTestCase(unittest.TestCase):

    def setUp(self):
        # Orbital Paramters
        self.base_time = datetime.datetime(2000, 1, 1)
        self.kepler_elements = KeplerElementSet(
            m0=-1.80185708521, e=0.484641175717e-3,
            a=math.pow(5153.58584023, 2), omega=2.89000380005,
            i=0.959622949611, w=-2.75505104383, t0=self.base_time + datetime.timedelta(hours=16)
        )
        self.nuisance_parameter_set = NuisanceParameterSet(
            delta_n=0.457447625958e-8,
            omega_dot=-0.799283293357e-8, i_dot=-0.560380484954e-9,
            c_us=0.976212322712e-5, c_uc=-0.109896063805e-5,
            c_is=0.428408384323e-7, c_ic=0.763684511185e-7,
            c_rs=-0.207812500000e2, c_rc=0.188562500000e3
        )

    def test_orbit_to_cart_1(self):
        pi = GeocentricPoint(13003500.208, 15810633.330, 16915621.431)
        di = self.__do_work(pi, self.base_time + datetime.timedelta(hours=17))
        d = 2.5918
        self.assertAlmostEqual(di, d, places=4)

    def test_orbit_to_cart_2(self):
        pi = GeocentricPoint(-7097758.924,  13953345.740, -21451613.819)
        di = self.__do_work(pi, self.base_time + datetime.timedelta(hours=22))
        d = 36.1411
        self.assertAlmostEqual(di, d, places=4)        

    def __do_work(self, pi, ti):
        logger.info("Calculate new Point")
        # print(self.kepler_elements)
        pn = orbit_to_cart(ke=self.kepler_elements, nps=self.nuisance_parameter_set, ti=ti, t0e=self.kepler_elements.t0 - datetime.timedelta(seconds=0.403200000000e6))
        logger.info("Pi: {}".format(pi))
        logger.info("Pn: {}".format(pn))
        diff = (pn - pi).get_norm()
        logger.info("Difference: {:22.3f}".format(diff))
        return diff

