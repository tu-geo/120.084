import unittest
import logging
import datetime
import os
import numpy as np

from skyfield.api import Topos, load

from prg1.models.orbit import Orbit
from prg1.models.point import GeocentricPoint
from prg1.utils.point_conversion import convert_ellipsoidal_to_cartesian, \
    convert_cartesian_to_ellipsoidal
from prg1.utils.polar_plot import generate_plot


logger = logging.getLogger(__name__)


class SkyFieldTestCase(unittest.TestCase):

    def setUp(self):

        # Declaration part
        self.duration = int(1440)  # 24*60
        self.max_satellites = 20
        self.station_geocentric = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
        self.station_geographic = convert_cartesian_to_ellipsoidal(self.station_geocentric)
        # Day of observation
        self.t_start = datetime.datetime(year=2020, month=3, day=20, hour=0, minute=0, second=0).replace(tzinfo=datetime.timezone.utc)
        self.t_end = self.t_start + datetime.timedelta(days=1)
        # Where to get TLEs from
        self.this_dir = os.path.dirname(os.path.realpath(__file__))
        self.test_file = os.path.join(self.this_dir, "20200320-active_satellites.txt")
        self.elevation_filter = 10.0
        self.duration = 1440
        self.satellite_filter_list = ["GALILEO", ]
        self.create_plot = True

    def __do_work(self, satellite, station):
        orbit = None
        elevations = []
        azimuths = []
        ts = load.timescale()

        for time_ticks in range(self.duration):
            ti = self.t_start + datetime.timedelta(minutes=time_ticks * 1)
            difference = satellite - station
            geometry = difference.at(ts.utc(ti.year, ti.month, ti.day, ti.hour, ti.minute))
            alt, az, distance = geometry.altaz()
            # print(ti, alt.degrees, az.degrees)
            elevations.append(alt.degrees)
            azimuths.append(az.degrees)

        np_e = np.array(elevations)
        np_a = np.array(azimuths)
        np_e[np_e < 10] = np.nan
        np_a[np_e < 10] = np.nan

        if len(np.extract(np_e >= self.elevation_filter, np_e)) > 0:
            orbit = Orbit(satellite.name, np_a, np_e)

        if not orbit is None:
            print("Satellite {} not on Greenbelt's sky".format(satellite.name))

        return orbit

    def test_rise_and_set(self):
        station = Topos(
            latitude_degrees=self.station_geographic.lat,
            longitude_degrees=self.station_geographic.lon
        )
        ts = load.timescale()
        t0 = ts.utc(self.t_start.year, self.t_start.month, self.t_start.day)
        t1 = ts.utc(self.t_end.year, self.t_end.month, self.t_end.day)
        satellites = load.tle(self.test_file)

        with open(os.path.join(self.this_dir, "__skyfield_rise_and_set.log"), "w") as skyfield_file:

            for satellite_name in satellites:
                satellite = satellites[satellite_name]
                t, events = satellite.find_events(station, t0, t1, altitude_degrees=self.elevation_filter)
                for ti, event in zip(t, events):
                    name = ('rise above 10°', 'culminate', 'set below 10°')[event]
                    skyfield_file.write("{},{},{}\n".format(ti.utc_iso(), satellite.name, name))

        self.assertTrue(False)


    def test_create_topo(self):
        return
        station = Topos(
            latitude_degrees=self.station_geographic.lat,
            longitude_degrees=self.station_geographic.lon
        )
        print("\n", station)
        
        satellites = load.tle(self.test_file)
        satellite_counter = 0
        orbit_list = []

        for satellite_name in satellites:

            # print("Satellite", satellite_name, type(satellite_name))

            if len(orbit_list) >= self.max_satellites:
                break

            found_sat = False
            if not self.satellite_filter_list:
                found_sat = True

            for satellite_filter in self.satellite_filter_list:
                # print("Test filter {} in {}".format(satellite_filter, satellite_name))
                if satellite_filter in str(satellite_name):
                    found_sat = True

            if not found_sat:
                continue

            print("Processing {}".format(satellite_name))
    
            satellite = satellites[satellite_name]
            orbit = self.__do_work(satellite, station)
            if orbit is not None:
                orbit_list.append(orbit)

        if orbit_list and self.create_plot:
            generate_plot(orbit_list=orbit_list, show_plot=self.create_plot)

        self.assertTrue(False)


