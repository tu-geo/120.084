import datetime
import os
import csv
import math
import pprint

from skyfield.api import Topos, load
from prg1.models.point import GeographicPoint
from prg1.models.folding_square import FoldingSquare

PK_NORAD = "norad_id"
PK_COSPAR = "cospar_id"

MODE_TURNING = "trn"
MODE_OBSERVING = "obs"

BIG_VALUE = 9999999


class ObservationScheduler:

    TLE_DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))),  # "code" directory
        "data"
    )

    def __init__(self, station_name, t_start: datetime.datetime, elevation_cutoff: float=10.0, duration: int=1440, **kwargs):
        """
        :param t_start: Starttime of Scheduler
        :type t_start: datetime.datetime
        :param elevation_cutoff: Elevation angle for cutoff
        :type elevation_cutoff: float
        :param duration: Duration time to observe
        :type duration: int
        :param station_location: Geographic coordinate of station
        :type station_location: GeographicPoint
        :param station_folding: Initial/current folding square of station
        :type station_folding: FoldingSquare
        :param station_folding_azimuth: intial azimuth of station [deg]. If defined, param station_folding will be overruled
        :type station_folding_azimuth: float
        :param station_folding_elevation: intial elevation of station [deg]. If defined, param station_folding will be overruled
        :type station_folding_elevation: float
        :param tle_data_dir: Folder of TLE data
        :type tle_data_dir: str
        """
        # print(ObservationScheduler.TLE_DATA_DIR)
        self._data_dir = kwargs.get("tle_data_dir", ObservationScheduler.TLE_DATA_DIR)
        self._observation_time = 0  # minutes
        self._station_location = kwargs.get("station_location", None)
        self._station_topo = None
        self._station_name = kwargs.get("station_name")
        self.__telescope_velocity = math.radians(50.0)  # 50 degrees per minute
        self._t_start = t_start
        self._observed_list = []
        self._duration = duration
        self.__current_satellite = None
        self.history = []
        self.elevation_cutoff = elevation_cutoff  # degrees
        self._timescale = load.timescale()
        # self.max_satellites = 15
        self.skip_known = 3

        assert os.path.exists(self._data_dir)
        assert isinstance(t_start, (datetime.datetime, datetime.date))
        assert isinstance(self._station_location, (type(None), GeographicPoint))

        self._t_end = t_start + datetime.timedelta(minutes=self._duration)

        if isinstance(self._station_location, GeographicPoint):
            self.__update_station_topo(self._station_location)

        if "station_folding_azimuth" in kwargs and "station_folding_elevation" in kwargs:
            azimuth = kwargs.get("station_folding_azimuth", 0.0)
            elevation = kwargs.get("station_folding_elevatin", 0.0)
            assert isinstance(azimuth, (int, float))
            assert isinstance(elevation, (int, float))
            kwargs["station_folding"] = FoldingSquare(azimuth, elevation)

        self._station_folding = kwargs.get("station_folding", FoldingSquare(0.0, 0.0))

    def get_station_location(self):
        return self._station_location

    def set_station_location(self, location: GeographicPoint):
        assert isinstance(location, GeographicPoint)
        self._station_location = location
        self.__update_station_topo(self._station_location)

    def get_station_folding(self):
        return self._station_folding

    def set_station_folding(self, value: FoldingSquare):
        self._station_folding = value

    def get_station_topo(self):
        """
        Get station location as skyfield.Topo
        """
        return self._station_topo

    def __update_station_topo(self, location):
        if isinstance(location, GeographicPoint):
            self._station_topo = Topos(
                latitude_degrees=location.lat,
                longitude_degrees=location.lon,
                elevation_m=location.ele
            )
            return self._station_topo
        return self._station_topo

    def add_observed_satellite(self, cospar_id):
        new_list = []
        if len(self._observed_list) < self.skip_known:
            new_list.append(cospar_id)
        for i, old_id in enumerate(self._observed_list):
            if i + len(new_list) < self.skip_known and cospar_id not in new_list:
                new_list.append(old_id)
            else:
                break
        self._observed_list = new_list

    station_location = property(get_station_location, set_station_location)
    station_folding = property(get_station_folding, set_station_folding)
    station_topo = property(get_station_topo)

    def get_latest_tle(self, latest_tle=None):
        latest_tle_file = None

        if latest_tle is None:
            latest_tle_file = os.path.join(
                self._data_dir,
                self._t_start.strftime("%Y%m%d-active_satellites.txt")
            )
            if not os.path.exists(latest_tle_file):
                l = glob.glob(os.path.join(
                    self._data_dir, "????????-active_satellites.txt"
                ))
                l.sort()
                latest_tle_file = l[-1]

        assert latest_tle_file is not None
        assert os.path.exists(latest_tle_file)
        return latest_tle_file

    def get_current_satellites(self, satellites, ti: datetime.datetime, sort_col: str=None):
        """

        """
        current_satellites = []
        # print("GetCurrentFoldings::Start")

        for item in satellites:
            satellite = item["earth_satellite"]
            difference = satellite - self.station_topo
            geometry = difference.at(self._timescale.utc(ti.year, ti.month, ti.day, ti.hour, ti.minute))
            alt, az, distance = geometry.altaz()  # rad, rad, m

            if alt.degrees < self.elevation_cutoff:
                # print(item["name"], "too low")
                continue

            # skip duplicates
            if item[PK_COSPAR] in [i[PK_COSPAR] for i in current_satellites]:
               continue

            folding = FoldingSquare(
                azimuth=math.radians(az.degrees),
                elevation=math.radians(alt.degrees),
                distance=distance.km*1000.0
            )

            current_satellites.append({
                "name": item["name"],
                PK_NORAD: item[PK_NORAD],
                PK_COSPAR: item[PK_COSPAR],
                "folding": folding,
                "chord": self.station_folding.get_chord_from_values(folding.azimuth, folding.elevation),
                "priority": item["priority"],
                "earth_satellite": satellite
            })

        if sort_col in ["priority", "chord"]:
            # print("Sort by {}".format(sort_col))
            current_satellites = sorted(current_satellites, key=lambda k: k[sort_col], reverse=False)
        
        return current_satellites

    def get_priorities(self) -> dict:
        """
        TODO
        """
        priority_file = os.path.join(
            self._data_dir, "cleaned",
            "FINAL_SORT_NORAD.csv"
        )
        priority_dict = {}
        with open(priority_file, "r") as f:
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

    def sort_satellites_by_priority(self, priority_dict, satellite_list):
        """
        """
        l = []
        for sat in satellite_list:
            if isinstance(sat, int):
                continue
            sat_norad = "{:05d}".format(int(satellite_list[sat].model.satnum))
            for prio in priority_dict:
                if prio != sat_norad:
                    continue
                tmp = {**priority_dict[prio]}
                tmp["earth_satellite"] = satellite_list[sat]
                l.append(tmp)
        return sorted(l, key=lambda k: (k["priority"], k["name"]), reverse=False)
        
    def has_enough_obs(self):
        return self._observation_time >= 10

    def execute(self):
        # Get Priorities
        priority_dict = self.get_priorities()

        # Get TLEs
        tle_file = self.get_latest_tle()
        satellites = load.tle(tle_file)

        # Sort satellites by priority
        sorted_satellites = self.sort_satellites_by_priority(priority_dict, satellites)
        # {'norad_id': '43476', 'cospar_id': '1804701', 'priority': 1, 'name': 'GRACE-FO-1', 'earth_satellite': <EarthSatellite 'GRACE-FO 1' number=43476 epoch=2020-03-30T04:22:00Z>}
        # {'norad_id': '37158', 'cospar_id': '1004501', 'priority': 53, 'name': 'QZS-1', 'earth_satellite': <EarthSatellite 'QZS-1 (MICHIBIKI-1)' number=37158 epoch=2020-03-29T11:31:43Z>}

        te = self._timescale.utc(
            self._t_end.year, self._t_end.month, self._t_end.day,
            self._t_end.hour, self._t_end.minute
        )

        current_mode = MODE_TURNING

        action_list = []
        i = 0

        action_dummy = {
            "timestamp": None,
            "mode": None,
            "azimuth": None,
            "elevation": None,
            "target": None,
            "observation_time": None,
            "total_minutes": None,
            "comments": None
        }

        while i < self._duration:

            # print("--- New Iteration ---\n")
            # get current datetime and skyfield.time
            ti = self._t_start + datetime.timedelta(minutes=i)
            ts = self._timescale.utc(ti.year, ti.month, ti.day, ti.hour, ti.minute)
            action = {
                "timestamp": ti.strftime("%Y%m%dT%H:%M"),
                "mode": None,
                "azimuth": None,
                "elevation": None,
                "target": None,
                "observation_time": None,
                "total_minutes": i,
                "comments": None
            }
            comments = []

            # get current satellites, sorted by chord
            current_satellites = self.get_current_satellites(sorted_satellites, ti, sort_col="chord")
            no_other = len(current_satellites) == 0

            if no_other:
                comments.append("NO_OTHER_SAT")

            # Initial Satellite choice
            if self.__current_satellite is None:
                self.__current_satellite = current_satellites[0]
                self._observation_time = 0

            # What if chosen satellite is not available
            if self.__current_satellite[PK_COSPAR] not in [j[PK_COSPAR] for j in current_satellites]:
                for satellite in current_satellites:
                    if satellite[PK_COSPAR] not in self._observed_list or no_other:
                        # print("Choosed a new, because of no availability")
                        comments.append("NOT_AVAILIBLE")
                        current_mode = MODE_TURNING
                        self.__current_satellite = current_satellites[0]
                        self._observation_time = 0
                        break

            for satellite in current_satellites:
                if self.has_enough_obs():
                    if satellite[PK_COSPAR] != self.__current_satellite[PK_COSPAR] and \
                        (satellite[PK_COSPAR] not in self._observed_list or no_other):
                        # print("Choosed a new, because it was time")
                        comments.append("TIME_FOR_NEW")
                        current_mode = MODE_TURNING
                        self.__current_satellite = satellite
                        self.add_observed_satellite(self.__current_satellite[PK_COSPAR])
                        self._observation_time = 0
                        break
                else:
                    if satellite[PK_COSPAR] == self.__current_satellite[PK_COSPAR]:
                        self.__current_satellite = satellite
                        current_mode = MODE_OBSERVING

            big_chord = self.__current_satellite["chord"] >= self.__telescope_velocity

            if not no_other and (self.has_enough_obs() or big_chord):
                # TODO turn telescope as much as possible
                # print("Turn to", self.__current_satellite["name"])
                action["target"] = self._station_name
                self._observation_time = 0
                # TODO set correct azimuth and elevation

                delta_folding = self.__current_satellite["folding"] - self.station_folding

                sign_azimuth = math.copysign(1, int(delta_folding.azimuth))
                sign_elevation = math.copysign(1, int(delta_folding.elevation))
                new_azimuth = delta_folding.azimuth if delta_folding.azimuth < self.__telescope_velocity else self.__telescope_velocity * sign_azimuth
                new_elevation = delta_folding.elevation if delta_folding.elevation < self.__telescope_velocity else self.__telescope_velocity * sign_elevation

                new_azimuth = (self.station_folding.azimuth + new_azimuth) % (2*math.pi)
                new_elevation = (self.station_folding.elevation + new_elevation) % (math.pi)

                self.station_folding = FoldingSquare(
                    azimuth=new_azimuth,
                    elevation=new_elevation,
                    distance=self.__current_satellite["folding"].distance
                )

            else:
                # TODO turn telescope
                # current_mode = MODE_OBSERVING
                self._observation_time += 1
                # set new folding of telescope
                action["target"] = self.__current_satellite["name"]
                self.set_station_folding(self.__current_satellite["folding"])

            # print("Station", self.station_folding)

            action["mode"] = current_mode
            action["azimuth"] = math.degrees(self.station_folding.azimuth)
            action["elevation"] = math.degrees(self.station_folding.elevation)
            action["observation_time"] = self._observation_time
            action["comments"] = ",".join(comments)
                     
            action_list.append(action)
            i += 1

        # show performed actions
        outfile = os.path.join(
            self.TLE_DATA_DIR, "results", 
            self._t_start.strftime("%Y%m%d-observations.csv")
        )
        with open(outfile, 'w', newline='') as csvfile:
            fieldnames = [k for k in action_dummy]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(action)
