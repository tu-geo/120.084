import unittest
import os
import datetime
import numpy as np

from prg1.models.orbit import Orbit
from prg1.models.point import GeocentricPoint
from prg1.models.kepler_element_set import KeplerElementSet
from prg1.utils.polar_plot import generate_plot
from prg1.utils.orbit_to_cart import orbit_to_cart
from prg1.utils.point_conversion import convert_ellipsoidal_to_cartesian, \
    convert_cartesian_to_ellipsoidal, get_azimuth_and_elevation

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
        return
        generate_plot(orbit_list=self.orbit_list, show_plot=False)

    
    def test_plot_sat(self):
        # generate azimuths and elevations
        this_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(this_dir, "__norad_37158.txt")
        orbit_list = []
        with open(test_file, "r") as tle:
            tle_str = "".join(tle.readlines())
            tle = KeplerElementSet.read_tle(tle_str)
            kepler_element_set = KeplerElementSet.from_dict(tle)

            t0 = tle["timestamp"].replace(tzinfo=datetime.timezone.utc)
            t_start = datetime.datetime(year=t0.year, month=t0.month, day=t0.day
            ).replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(days=2)

            p0c = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
            p0g = convert_cartesian_to_ellipsoidal(axis_major=kepler_element_set.a,
                flattening=tle["flattening"],
                src_point=p0c
            )

            elevation = []
            azimuth = []

            print("range")
            for i in range(96):
                ti = t_start + datetime.timedelta(seconds=i+1)            
                pic = orbit_to_cart(ke=kepler_element_set, nps=None, t0=t0.timestamp(), ti=ti.timestamp(), t0e=tle["period_of_revolution"])
                pig = convert_cartesian_to_ellipsoidal(axis_major=kepler_element_set.a,
                    flattening=tle["flattening"],
                    src_point=pic
                )
                a, e = get_azimuth_and_elevation(p0g, pig)
                if a < 0:
                    a += 360
                if e > 90:
                    e = 90 - (e % 90)
                if e >= 10:
                    elevation.append(e)
                    azimuth.append(a)
                    append = True
                else:
                    append = False

                if append:
                    print(a, e)
                    append = False

            if elevation:
                orbit_list.append(Orbit(tle["satellite_name"], azimuth, elevation))

            else:
                print("Satellite {} not on Greenbelt's sky".format(tle["satellite_name"]))

        
        if orbit_list:
            # plot Orbit
            generate_plot(orbit_list=orbit_list, show_plot=True)
        self.assertTrue(False)
