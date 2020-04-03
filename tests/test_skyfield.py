import unittest
import logging
import datetime
import os
import numpy as np
import csv

from skyfield.api import Topos, load

from prg1.models.orbit import Orbit
from prg1.models.point import GeocentricPoint
from prg1.utils.point_conversion import convert_ellipsoidal_to_cartesian, \
    convert_cartesian_to_ellipsoidal
from prg1.utils.polar_plot import generate_plot
from prg1.utils.plot_time import generate_plot as plot_time


PK_NORAD = "norad_id"
PK_COSPAR = "cospar_id"

logger = logging.getLogger(__name__)


class SkyFieldTestCase(unittest.TestCase):

    def setUp(self):

        # Declaration part
        self.duration = int(1440)  # 24*60
        # self.max_satellites = 1
        self.station_geocentric = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
        self.station_geographic = convert_cartesian_to_ellipsoidal(self.station_geocentric)
        # Day of observation
        self.t_start = datetime.datetime(year=2020, month=3, day=28, hour=0, minute=0, second=0).replace(tzinfo=datetime.timezone.utc)
        self.t_end = self.t_start + datetime.timedelta(days=1)
        # Where to get TLEs from
        self.this_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = os.path.join(
            os.path.dirname(self.this_dir),
            "data"
        )
        self.test_file = os.path.join(data_dir, self.t_start.strftime("%Y%m%d-active_satellites.txt"))
        assert os.path.exists(self.test_file)
        self.elevation_filter = 10.0
        self.satellite_filter_list = [ ]
        self.create_plot = True

        self.priority_file = os.path.join(
            data_dir, "cleaned",
            "FINAL_SORT_NORAD.csv"
        )

    def __get_priorities(self) -> dict:
        """
        TODO
        """
        priority_dict = {}
        with open(self.priority_file, "r") as f:
            csv_reader = csv.reader(f, delimiter=";")
            # (1, "GRACE-FO-1", 1804701, 43476)
            for row in csv_reader:
                if row[0].startswith("#"):
                    continue
                if str(row[3]).upper() == "UNKNOWN":
                    continue
                #print(row)
                tmp = {
                    PK_NORAD: "{:05d}".format(int(row[3])),
                    PK_COSPAR: row[2],
                    "priority": int(row[0]),
                    "name": row[1]
                }
                # print(tmp)
                priority_dict[tmp[PK_NORAD]] = tmp
        
        # {norad_id: {PK_NORAD: n_id, "cospar_id": c_id, "priority": p, "name": n}, ...}
        return priority_dict

    def __do_work(self, satellite, station, sat_info):
        orbit = None
        elevations = []
        azimuths = []
        ts = load.timescale()
        sat_name = sat_info["name"]

        thin = 1

        for time_ticks in range(int(self.duration/thin)):
            ti = self.t_start + datetime.timedelta(minutes=time_ticks*thin)
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
            orbit = Orbit(sat_name, np_a, np_e)

        if orbit is None:
            print("Satellite {} not on Greenbelt's sky".format(sat_name))

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

        i = 0

        priority_dict = self.__get_priorities()
        priority_list = [priority_dict[j][PK_NORAD] for j in priority_dict]
        recorded_ids = []

        with open(
            os.path.join(
                self.this_dir,
                self.t_start.strftime("%Y%m%d-skyfield-rise_and_set.log")
            ),
            "w") as skyfield_file:

            window_list_all = []

            for satellite_name in satellites:

                if isinstance(satellite_name, int):
                    continue

                satellite = satellites[satellite_name]
                norad_id = "{:05d}".format(int(satellite.model.satnum))
                
                if norad_id not in priority_list:
                    continue

                if norad_id in recorded_ids:
                    continue

                recorded_ids.append(norad_id)

                sat_info = {}
                for j in priority_dict:
                    if priority_dict[j][PK_NORAD] == norad_id:
                        sat_info = priority_dict[j]
                        break

                window_list_sat = []

                t, events = satellite.find_events(station, t0, t1, altitude_degrees=self.elevation_filter)
                window = []

                for ti, event in zip(t, events):
                    name = ('rise above 10°', 'culminate', 'set below 10°')[event]
                    skyfield_file.write("{},{},{}\n".format(ti.utc_iso(), satellite.name, name))
                    t_formatted = datetime.datetime.strptime(
                        ti.utc_strftime("%Y-%m-%dT%H:%M"),
                        "%Y-%m-%dT%H:%M"                      
                    )

                    if event == 0:  # Rise
                        window = [t_formatted,]
                    elif event == 2:  # Set, only if rised too
                        if len(window) == 0:
                            window = [t_formatted - datetime.timedelta(hours=t_formatted.hour, minutes=t_formatted.minute)]
                        window.append(t_formatted)

                    if len(window) == 2:
                        window_list_sat.append(window)

                if len(window) == 1:
                    t_formatted = datetime.datetime.strptime(
                        t1.utc_strftime("%Y-%m-%dT%H:%M"),
                        "%Y-%m-%dT%H:%M"                      
                    )
                    window.append(t_formatted)
                    window_list_sat.append(window)

                if window_list_sat:
                    window_list_all.append({
                        "satellite": sat_info["name"],
                        "windows": window_list_sat,
                        "priority": sat_info["priority"]
                    })

        window_list_all = sorted(window_list_all, key=lambda k: (k["priority"], k["satellite"]), reverse=True)

        if self.create_plot:
            plot_time(window_list_all, bar_height=10)

        self.assertTrue(False)


    def test_create_sky(self):
        station = Topos(
            latitude_degrees=self.station_geographic.lat,
            longitude_degrees=self.station_geographic.lon
        )
        print("\n", station)
        
        satellites = load.tle(self.test_file)
        satellite_counter = 0
        orbit_list = []

        priority_dict = self.__get_priorities()
        priority_list = [priority_dict[j][PK_NORAD] for j in priority_dict]
        recorded_ids = []

        i = 0

        for satellite_name in satellites:

            i += 1

            if isinstance(satellite_name, int):
                continue

            satellite = satellites[satellite_name]
            norad_id = "{:05d}".format(int(satellite.model.satnum))
            
            if norad_id not in priority_list:
                continue

            if norad_id in recorded_ids:
                continue

            recorded_ids.append(norad_id)

            sat_info = {}
            for j in priority_dict:
                if priority_dict[j][PK_NORAD] == norad_id:
                    sat_info = priority_dict[j]
                    break
    
            satellite = satellites[satellite_name]
            orbit = self.__do_work(satellite, station, sat_info)
            if orbit is not None:
                orbit_list.append({
                    "priority": sat_info["priority"],
                    "name": sat_info["name"],
                    "orbit": orbit
                })

        if orbit_list and self.create_plot:
            orbit_list = sorted(orbit_list, key=lambda k: (k["priority"], k["name"]), reverse=False)
            generate_plot(orbit_list=[o["orbit"] for o in orbit_list], show_plot=self.create_plot)

        self.assertTrue(False)



