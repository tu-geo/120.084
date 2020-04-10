import unittest
import logging
import math
import datetime
import numpy as np
import os
import csv

from prg1.models.observation_scheduler import ObservationScheduler, \
    SORT_COL_CHORD, SORT_COL_PRIORITY, PK_COSPAR, PK_NORAD
from prg1.models.point import GeographicPoint, GeocentricPoint
from prg1.models.orbit import Orbit
#from prg1.models.folding_square import FoldingSquare
from prg1.utils.point_conversion import convert_cartesian_to_ellipsoidal
from prg1.utils.plot_polar import generate_plot as plot_sky
from prg1.utils.plot_time import generate_plot as plot_time
from prg1.utils.plot_hist import generate_plot as plot_hist

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class ObservationSchedulerTestCase(unittest.TestCase):

    def setUp(self):
        station_geocentric = GeocentricPoint(x=1130745.549, y=-4831368.033, z=3994077.168)
        station_geographic = convert_cartesian_to_ellipsoidal(station_geocentric)
        self.timestamp = datetime.datetime(2020, 3, 28, 0, 0)
        self.sort_key = SORT_COL_PRIORITY
        #self.sort_key = SORT_COL_CHORD
        self.intervall = 1

        self.scheduler = ObservationScheduler(
            station_name="Greenbelt",
            intervall=self.intervall,
            # duration=200,
            sort_col=self.sort_key,
            # skip_known=1,
            station_location=station_geographic,
            station_folding_elevation=math.radians(0.0),
            station_folding_azimuth=math.radians(0.0),
            t_start=self.timestamp
        )

    def __generate_plot_time(self, action_list):
        time_list = []
        sorter_dict = {}
        last_pk = None

        for action in action_list:
            pk = action[PK_COSPAR]

            print("PK", pk)

            if not pk:
                pk = "SITE"

            if last_pk is None:
                last_pk = pk

            print("LAST_PK")

            if pk not in sorter_dict:
                sorter_dict[pk] = {
                    "priority": action["priority"],
                    "name": action["target"],
                    PK_COSPAR: action[PK_COSPAR],
                    PK_NORAD: action[PK_NORAD],
                    "windows": []
                }

            ts = datetime.datetime.strptime(action["timestamp"], "%Y%m%dT%H:%M")

            if last_pk != pk or len(sorter_dict[pk]["windows"]) == 0:
                sorter_dict[pk]["windows"].append([])

            # Close old timewindow in case of new sat
            if last_pk != pk:
                if len(sorter_dict[last_pk]["windows"][-1]) < 2:
                    sorter_dict[last_pk]["windows"][-1].append(ts)

            if len(sorter_dict[pk]["windows"][-1]) == 0:
                sorter_dict[pk]["windows"][-1].append(ts)

            elif len(sorter_dict[pk]["windows"][-1]) == 1:
                sorter_dict[pk]["windows"][-1].append(ts)

            elif len(sorter_dict[pk]["windows"][-1]) == 2:
                sorter_dict[pk]["windows"][-1][-1] = ts

            # print(last_pk, sorter_dict[last_pk]["windows"][-1])
            last_pk = pk

        for sat in sorter_dict:
            time_list.append({
                "priority": sorter_dict[sat]["priority"],
                "name": sorter_dict[sat]["name"],
                "windows": sorter_dict[sat]["windows"]
            })

        return sorted(time_list, key=lambda k: (k["priority"], k["name"]), reverse=True)

    def __generate_plot_sky(self, action_list):
        orbit_list = []
        sorter_dict = {}
        last_pk = None

        for action in action_list:
            pk = action[PK_COSPAR]

            if not pk:
                pk = "SITE"

            if last_pk is None:
                last_pk = pk

            if pk not in sorter_dict:
                sorter_dict[pk] = {
                    "priority": action["priority"],
                    "name": action["target"],
                    PK_COSPAR: action[PK_COSPAR],
                    PK_NORAD: action[PK_NORAD],
                    "foldings": {
                        "azimuth": [],
                        "elevation": []
                    }
                }

            if last_pk != pk and len(sorter_dict[last_pk]["foldings"]["azimuth"]) > 0:
                sorter_dict[pk]["foldings"]["azimuth"].append(np.nan)
                sorter_dict[pk]["foldings"]["elevation"].append(np.nan)

            sorter_dict[pk]["foldings"]["azimuth"].append(float(action["azimuth"]))
            sorter_dict[pk]["foldings"]["elevation"].append(float(action["elevation"]))
            last_pk = pk

        for sat in sorter_dict:
            if sat == "SITE":
                continue
            # print(sorter_dict[sat])
            sat_orbit = Orbit(
                satellite_id=sorter_dict[sat]["name"],
                azimuth_list=np.array(sorter_dict[sat]["foldings"]["azimuth"]),
                elevation_list=np.array(sorter_dict[sat]["foldings"]["elevation"])
            )
            orbit_list.append({
                "orbit": sat_orbit,
                "name": sorter_dict[sat]["name"],
                "priority": sorter_dict[sat]["priority"]
            })

        return sorted(orbit_list, key=lambda k: (k["priority"], k["name"]), reverse=False)

    def __generate_plot_hist(self, action_list, intervall=1):
        duration_list = []
        sorter_dict = {}
        last_pk = None

        for action in action_list:
            pk = action[PK_COSPAR]

            if not pk:
                pk = "SITE"

            if last_pk is None:
                last_pk = pk

            if pk not in sorter_dict:
                sorter_dict[pk] = {
                    "priority": action["priority"],
                    "name": action["target"],
                    PK_COSPAR: action[PK_COSPAR],
                    PK_NORAD: action[PK_NORAD],
                    "timestamp": action["timestamp"],
                    "duration": 0
                }
            
            sorter_dict[pk]["duration"] += intervall
            last_pk = pk  # not really neccessary

        for sat in sorter_dict:
            duration_list.append({
                "name": sorter_dict[sat]["name"],
                "priority": sorter_dict[sat]["priority"],
                "duration": sorter_dict[sat]["duration"],
            })

        return sorted(duration_list, key=lambda k: (k["priority"], k["name"]), reverse=False)

    def __import_action_list(self, action_file):
        """
        """
        action_list = []
        with open(action_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                # print(row)
                action_list.append(row)
        return action_list

    def test_execute(self):
        return
        action_list = self.scheduler.execute()
        self.assertTrue(False)

    def test_plot_sky(self):
        return 
        action_file = os.path.join(
            ROOT_DIR, "data", "results", 
            self.timestamp.strftime("%Y%m%d-observations-{}-{:02d}.csv".format(self.sort_key, self.intervall))
        )
        action_list = self.__import_action_list(action_file)
        # Sky Plot
        orbit_list = self.__generate_plot_sky(action_list)
        # print("Orbit List", orbit_list)        
        plot_sky(orbit_list=[o["orbit"] for o in orbit_list], show_plot=True)

    def test_plot_time(self):
        return
        action_file = os.path.join(
            ROOT_DIR, "data", "results", 
            self.timestamp.strftime("%Y%m%d-observations-{}-{:02d}.csv".format(self.sort_key, self.intervall))
        )
        action_list = self.__import_action_list(action_file)
        # Time Plot
        time_list = self.__generate_plot_time(action_list)
        # print("Time List", time_list)
        plot_time(time_list, bar_height=10)

    def test_plot_hist(self):
        action_file = os.path.join(
            ROOT_DIR, "data", "results", 
            self.timestamp.strftime("%Y%m%d-observations-{}-{:02d}.csv".format(self.sort_key, self.intervall))
        )
        action_list = self.__import_action_list(action_file)
        duration_list = self.__generate_plot_hist(action_list, self.intervall)
        plot_hist(duration_list, bar_width=0.8)
