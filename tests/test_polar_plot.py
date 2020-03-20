import unittest
import numpy as np

from prg1.models.orbit import Orbit
from prg1.utils.polar_plot import generate_plot


class PolarPlotTestCase(unittest.TestCase):

    def setUp(self):
        elevation = []
        azimuth1 = []
        azimuth2 = []

        max_angle = 360

        for i in range(max_angle):
            e = i / (max_angle / 90.0)
            elevation.append(e)
            azimuth1.append(2 * np.pi * np.radians(e))
            azimuth2.append(1 * np.pi * np.radians(e))

        self.orbit_list = [
            Orbit("S1", azimuth1, elevation),
            Orbit("S2", azimuth2, elevation),
        ]
        
    def test_plot_creation(self):
        generate_plot(orbit_list=self.orbit_list, show_plot=False)
