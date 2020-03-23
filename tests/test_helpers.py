import unittest
import logging
import math
import datetime

from prg1.models.kepler_element_set import KeplerElementSet
from prg1.utils.orbit_to_cart import recursive_anomaly, orbit_to_geograpic_springer, orbit_to_cart
from prg1.utils.point_conversion import convert_cartesian_to_ellipsoidal


logger = logging.getLogger(__name__)


class HelpersTestCase(unittest.TestCase):

    def setUp(self):
        # Orbital Paramters
        self.base_time = datetime.datetime(2020, 3, 11).replace(tzinfo=datetime.timezone.utc)
        self.kepler_elements = KeplerElementSet(
            m0=math.radians(251.7436),
            a=6723842.235,
            e=0.0008835,
            omega=math.radians(122.3522),
            i=math.radians(51.6448),
            w=math.radians(257.3473),
            t0=self.base_time + datetime.timedelta(hours=4, minutes=3)
        )
        self.ti = self.base_time + datetime.timedelta(hours=33)

    def test_recursive_anomaly(self):

        m_k = self.kepler_elements.n * (self.ti - self.kepler_elements.t0).total_seconds()
        m_k += self.kepler_elements.m0

        # Iterational approach
        eps = 1e-12
        e_k_old = m_k
        e_k_new = self.kepler_elements.e * math.sin(e_k_old)
        while math.fabs(e_k_old - e_k_new) > eps:
            e_k_old = e_k_new
            e_k_new = m_k + self.kepler_elements.e * math.sin(e_k_new)

        # Recursive approach
        true_anomaly = recursive_anomaly(m_k, m_k, self.kepler_elements.e, 0, eps)
        self.assertAlmostEqual(true_anomaly, e_k_new, places=12)
