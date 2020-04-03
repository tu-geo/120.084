import unittest
import os
import datetime
import numpy as np
import csv

from prg1.models.orbit import Orbit
from prg1.models.point import GeocentricPoint
from prg1.models.kepler_element_set import KeplerElementSet
from prg1.models.nuisance_parameter_set import NuisanceParameterSet
from prg1.utils.constants import *
from prg1.utils.polar_plot import generate_plot
from prg1.utils.orbit_to_cart import orbit_to_cart, orbit_to_geograpic_springer
from prg1.utils.time_conversion import calculate_theta
from prg1.utils.angle_conversion import rad_to_deg
from prg1.utils.point_conversion import convert_ellipsoidal_to_cartesian, \
    convert_cartesian_to_ellipsoidal, get_azimuth_and_elevation, xyz2ell


class PolarPlotTestCase(unittest.TestCase):

    def setUp(self):

        # Declaration part
        self.duration = int(1440)  # 24*60
        self.max_satellites = 1
        self.station_geocentric = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
        # Day of observation
        self.t_start = datetime.datetime(year=2020, month=3, day=28, hour=0, minute=0, second=0).replace(tzinfo=datetime.timezone.utc)
        self.sat_filter = ["GALILEO", ]
        self.create_plot = False

    def __do_work(self, p0c, t_start, tle_str, sat_filter=[], export_file=""):
        orbit_list = []
        tle = KeplerElementSet.read_tle(tle_str)
        row_list = []
        elevation = []
        azimuth = []
        fieldnames = ["Timestamp", "SatelliteName", "SatelliteNoradId", "ECEF_X", "ECEF_Y", "ECEF_Z", "Longitude", "Latitude", "height", "azimuth", "elevation"]
        do_work = False if sat_filter else True

        for sat in sat_filter:
            do_work = do_work or sat in tle["satellite_name"]

        if not do_work:
            return orbit_list
        
        kepler_element_set = KeplerElementSet.from_dict(tle)
        #print(kepler_element_set)
        t0e = datetime.datetime(2000, 1, 1).replace(tzinfo=datetime.timezone.utc)

        for i in range(self.duration):
            ti = t_start + datetime.timedelta(minutes=i)
            days = 0 if ti.weekday() == 6 else ti.weekday() + 1

            # Get the start of corresponding GPS-Week
            last_sunday = ti - datetime.timedelta(days=days,
                hours=ti.hour, minutes=ti.minute, seconds=ti.second,
                microseconds=ti.microsecond
            )
            #last_sunday = datetime.datetime(2000, 1, 1).replace(tzinfo=datetime.timezone.utc)
            # t0e = (ti - last_sunday).total_seconds()
            p0g = convert_cartesian_to_ellipsoidal(src_point=p0c)

            # Orbit to cartesian
            pic = orbit_to_cart(ke=kepler_element_set, ti=ti, nps=None, t0e=last_sunday)

            # Cartesian to ellipsoidal
            pig = convert_cartesian_to_ellipsoidal(axis_major=kepler_element_set.a,
                flattening=kepler_element_set.f,
                src_point=pic
            )

            ## Kepler to ellipsoidal
            #pig = orbit_to_geograpic_springer(ke=kepler_element_set,  ti=ti, t0e=last_sunday, apply_rotation=False)
            # delta_lambda = OMEGA_E_DOT * (kepler_element_set.t0 - t0e).total_seconds()
            #delta_lambda = OMEGA_E_DOT * (last_sunday - t0e).total_seconds()
            #delta_lambda = np.degrees(delta_lambda % (2 * np.pi))
            #pig.lon += delta_lambda

            a, e = get_azimuth_and_elevation(p0g, pig)
            if e > 90:
                #e = 180 - e
                e = 90 - (e % 90)

            # get columns
            row = [
                ti.strftime("%Y-%m-%dT%H:%M:%SZ"),
                tle["satellite_name"],
                tle["satellite_catalog_number_1"],
                pic.x, pic.y, pic.z,
                pig.lon, pig.lat, pig.ele,
                a, e
            ]
            # append rows
            row_list.append(row)

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

        if export_file:
            export_file = export_file.replace("XXXX", tle["satellite_catalog_number_1"])
            with open(export_file, "w", newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in row_list:
                    d = {}
                    for key, value in zip(fieldnames, row):
                        d[key] = value
                    writer.writerow(d)
            
        return orbit_list

    def test_jason(self):
        return True
        this_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(this_dir, "__jason.csv")
        azimuth = []
        elevation = []
        orbit_list = []

        with open(test_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                azimuth.append(float(row["azimuth"]))
                elevation.append(float(row["elevation"]))
            np_a = np.array(azimuth)
            np_e = np.array(elevation)
            np_a[np_e < 10] = np.nan
            np_e[np_e < 10] = np.nan
            orbit_list.append(
                Orbit("Jason", np_a, np_e)
            )
        generate_plot(orbit_list=orbit_list, show_plot=True)
        self.assertTrue(False)
        
    def test_plot_creation(self):
        return
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
        generate_plot(orbit_list=self.orbit_list, show_plot=self.create_plot)

    def test_plot_sat(self):
        return
        # generate azimuths and elevations
        this_dir = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.join(this_dir, "20200320-active_satellites.txt")
        # sat_filter = []
        orbit_list = []
        p0c = self.station_geocentric
        j = 0

        # Let's get all the satellite's orbits
        with open(test_file, "r") as tle:
            i = 0
            tle_set = []
            for row in tle:
                # Stop importing if sufficient orbits are processed
                if j >= self.max_satellites:
                    break
                
                tle_set.append(row)

                if i % 3 == 2:
                    tle_str = "".join(tle_set)
                    sat_name = tle_set[0].replace("\n", "").strip()
                    tle_set = []
                    result = self.__do_work(p0c, self.t_start, tle_str, self.sat_filter, os.path.join(this_dir, "results", "20200320-result-XXXX.csv"))
                    if result:
                        print("Processing -- {}".format(sat_name))
                        orbit_list += result
                        j += 1

                i += 1

        if orbit_list:
            # plot Orbit
            generate_plot(orbit_list=orbit_list, show_plot=self.create_plot)
        self.assertTrue(False)
