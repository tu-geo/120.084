import unittest
import os
import datetime
import numpy as np

from prg1.models.orbit import Orbit
from prg1.models.point import GeocentricPoint
from prg1.models.kepler_element_set import KeplerElementSet
from prg1.models.nuisance_parameter_set import NuisanceParameterSet
from prg1.utils.polar_plot import generate_plot
from prg1.utils.orbit_to_cart import orbit_to_cart
from prg1.utils.angle_conversion import rad_to_deg
from prg1.utils.point_conversion import convert_ellipsoidal_to_cartesian, \
    convert_cartesian_to_ellipsoidal, get_azimuth_and_elevation, xyz2ell

class PolarPlotTestCase(unittest.TestCase):

    def setUp(self):
        elevation = []
        azimuth1 = []
        azimuth2 = []

        max_angle = 360

        self.duration = int(1440)

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

    def __do_work(self, p0g, t_start, tle_str, sat_filter=[]):
        orbit_list = []
        tle = KeplerElementSet.read_tle(tle_str)

        if sat_filter:
            do_work = False
        else:
            do_work = True

        for sat in sat_filter:
            do_work = do_work or sat in tle["satellite_name"]

        if not do_work:
            return orbit_list
        
        kepler_element_set = KeplerElementSet.from_dict(tle)
        t0 = tle["timestamp"].replace(tzinfo=datetime.timezone.utc)
        elevation = []
        azimuth = []

        nuisance_parameter_set = None

        # nuisance_parameter_set = NuisanceParameterSet(
        #     delta_n=0.457447625958e-8,
        #     omega_dot=-0.799283293357e-8, i_dot=-0.560380484954e-9,
        #     c_us=0.976212322712e-5, c_uc=-0.109896063805e-5,
        #     c_is=0.428408384323e-7, c_ic=0.763684511185e-7,
        #     c_rs=-0.207812500000e2, c_rc=0.188562500000e3
        # )

        for i in range(self.duration):
            ti = t_start + datetime.timedelta(minutes=i + 1)
            if ti.weekday() == 6:
                days = 0
            else:
                days = ti.weekday() +1
            last_sunday = ti - datetime.timedelta(days=days,
                hours=ti.hour, minutes=ti.minute, seconds=ti.second,
                microseconds=ti.microsecond
            )
            t0e = (ti - last_sunday).total_seconds()
            # print("t0e: {:.4f}".format(t0e))

            pic = orbit_to_cart(ke=kepler_element_set, nps=nuisance_parameter_set,
                t0=t0.timestamp(), ti=ti.timestamp(), t0e=t0e)
            pig = convert_cartesian_to_ellipsoidal(axis_major=kepler_element_set.a,
                flattening=tle["flattening"],
                src_point=pic
            )
            # print(pig)
            # pig = xyz2ell(src_point=pic, axis_major=kepler_element_set.a, flattening=tle["flattening"])
            # print(pig)
            a, e = get_azimuth_and_elevation(p0g, pig)

            # if e > 180:
            #     print("HÄH")
            #     e = 0
            if e > 90:
                #print(e)
                #e = 180 - e
                e = 90 - (e % 90)

            #print(a, e)

            elevation.append(e)
            azimuth.append(a)

        np_e = np.array(elevation)
        np_a = np.array(azimuth)

        np_e[np_e < 10] = np.nan
        np_a[np_e < 10] = np.nan

        if len(np.extract(np_e >= 10, np_e)) > 0:
            orbit_list.append(Orbit(tle["satellite_name"], np_a, np_e))

        if not orbit_list:
            print("Satellite {} not on Greenbelt's sky".format(tle["satellite_name"]))

        return orbit_list

    def test_plot_sat(self):
        # generate azimuths and elevations
        this_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(this_dir, "20200320-active_satellites.txt")
        sat_filter = ["LAGEOS", "GRACE", "ICE", "CRYO"]
        sat_filter = []
        orbit_list = []
        p0c = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
        p0g = convert_cartesian_to_ellipsoidal(src_point=p0c)
        # print(p0g)
        t_start = datetime.datetime(year=2020, month=3, day=20, hour=20, minute=57, second=13).replace(tzinfo=datetime.timezone.utc)
        max_satellites = 20
        j = 0

        with open(test_file, "r") as tle:
            i = 0
            tle_set = []
            for row in tle:
                tle_set.append(row)

                if i % 3 == 2:
                    tle_str = "".join(tle_set)
                    sat_name = tle_set[0].replace("\n", "").strip()
                    tle_set = []
                    result = self.__do_work(p0g, t_start, tle_str, sat_filter)
                    if result:
                        print("Processing -- {}".format(sat_name))
                        orbit_list += result
                        j += 1

                if j > max_satellites:
                    break
                i += 1

        if orbit_list:
            # plot Orbit
            generate_plot(orbit_list=orbit_list, show_plot=True)
        self.assertTrue(False)
