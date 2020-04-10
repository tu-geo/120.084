import datetime
import os
import csv
import math
import pprint
import glob

from skyfield.api import Topos, load
from prg1.models.point import GeographicPoint
from prg1.models.folding_square import FoldingSquare
from prg1.utils.constants import PK_NORAD, PK_COSPAR


MODE_TURNING = "trn"
MODE_OBSERVING = "obs"

SORT_COL_PRIORITY = "priority"
SORT_COL_CHORD = "chord"
SORT_COL_CHOICES = [SORT_COL_PRIORITY, SORT_COL_CHORD]

BIG_VALUE = 9999999

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

planets = load(
    os.path.join(
        ROOT_DIR,
        'de421.bsp'
    )
)



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
        self._current_satellite = None
        self.history = []
        self.elevation_cutoff = elevation_cutoff  # degrees
        self._timescale = load.timescale()
        self.sort_col = kwargs.get("sort_col", None)
        self.__main_planet = kwargs.get("main_planet", "earth")
        # self.max_satellites = 15
        self.__intervall = kwargs.get("intervall", 1)
        self.skip_known = kwargs.get("skip_known", 0)
        assert isinstance(self.skip_known, int)

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
            return planets[self.__main_planet] + self._station_topo
        return self._station_topo

    def add_observed_satellite(self, cospar_id):
        new_list = []

        if self.skip_known == 0:
            self._observed_list = new_list
            return

        if len(new_list) < self.skip_known:
            new_list.append(cospar_id)

        # print(new_list)

        for i, old_id in enumerate(self._observed_list):
            # print("test", old_id)
            if len(new_list) >= self.skip_known:
                break
            if old_id not in new_list:
                new_list.append(old_id)
            
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

        if sort_col in SORT_COL_CHOICES:
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

    def execute(self) -> list:
        """
        Compute Action plan. Dict format:

        {
            "timestamp": datetime.datetime,
            "mode": str,
            "azimuth": float,
            "elevation": float,
            "target": str,
            "observation_time": int,
            "total_minutes": int,
            "comments": str,
            "priority": int,
            "cospar_id": str,
            "norad_id": str
        }

        :returns: List of fullfilled actions
        :rtype: list
        """
        print("\n- START THE MAGIC -")
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

        action_fields = [
            "timestamp", "mode",
            "azimuth", "elevation",
            "target", "observation_time", "total_minutes",
            "comments", "priority",
            PK_COSPAR, PK_NORAD,
        ]

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
                "target": MODE_TURNING.upper(),
                "observation_time": None,
                "total_minutes": i,
                "comments": None,
                "priority": None,
                PK_COSPAR: None,
                PK_NORAD: None,
            }
            comments = []

            current_mode = MODE_OBSERVING

            # get current satellites, sorted by chord
            current_satellites = self.get_current_satellites(sorted_satellites, ti, sort_col=self.sort_col)
            no_other = len(current_satellites) == 1

            print("\n--- {} ---\n".format(ti.strftime("%Y-%m-%dT%H:%M")))

            #for obj in current_satellites:
            #    print(obj[PK_COSPAR], "{:03d}".format(obj["priority"]), "{:.2f}".format(obj["chord"]), obj["folding"], obj["name"])

            # print(self._observed_list)
            
            # Initial Satellite choice
            if self._current_satellite is None:
                self._current_satellite = current_satellites[0]
                self._observation_time = -1
                current_mode = MODE_TURNING
                comments.append("INITIAL::{}".format(self._current_satellite["name"]))

            # print("\nOLD", self.station_folding, self._current_satellite["name"], "# %04d" % self._observation_time)

            # What if chosen satellite is not available
            do_alternative = False
            if self._current_satellite[PK_COSPAR] not in [j[PK_COSPAR] for j in current_satellites]:
                current_mode = MODE_TURNING
                for satellite in current_satellites:
                    # just choose a satellite which is not already observerd or if there is no other available
                    if satellite[PK_COSPAR] not in self._observed_list or no_other:
                        # print("Choosed a new, because of no availability")
                        s = "NOT_AVAILABLE::{}".format(self._current_satellite["name"])
                        # print(s)
                        comments.append(s)
                        # Reset observation time just if a new satellite will be observed
                        if self._current_satellite[PK_COSPAR] != satellite[PK_COSPAR]:
                            self._observation_time = 0   
                        else:
                            current_mode = MODE_OBSERVING                     
                        self._current_satellite = satellite
                        do_alternative = True
                        s = "SWITCH::{}".format(self._current_satellite["name"])
                        # print(s)
                        comments.append(s)
                        break

            if no_other:
                self._current_satellite = current_satellites[0]
                comments.append("NO_OTHER_SAT::{}".format(
                    current_satellites[0]["name"]
                ))

            for satellite in current_satellites:
                # print(satellite)
                other_cospar = satellite[PK_COSPAR] != self._current_satellite[PK_COSPAR]
                same_cospar = not other_cospar

                if do_alternative:
                    current_mode = MODE_TURNING
                    break

                # Same Sat, no other, 
                if same_cospar and no_other:
                    # print("Keep observing, but has no choice")
                    current_mode = MODE_OBSERVING
                    self._current_satellite = satellite
                    break 

                if self.has_enough_obs() and not no_other:

                    current_mode = MODE_TURNING

                    if other_cospar:
                        # print("Take next")
                        self._current_satellite = satellite
                        self.add_observed_satellite(self._current_satellite[PK_COSPAR])
                        comments.append("TIME_FOR_NEW::{}".format(self._current_satellite["name"]))
                        break

                # keep measuring, easy part
                else:
                    if not other_cospar:
                        # print("Keep observing")
                        self._current_satellite = satellite
                        current_mode = MODE_OBSERVING
                        break

            # Clean folding square
            # print("SAT", self._current_satellite["folding"], self._current_satellite["name"])

            delta_folding = self._current_satellite["folding"] - self.station_folding
            # print("DLT ..............azimuth={:11.6f}, elevation={:11.6f}".format(math.degrees(delta_folding.azimuth), math.degrees(delta_folding.elevation)))
            if math.fabs(delta_folding.azimuth) > math.pi:
                #delta_folding.azimuth = delta_folding.azimuth - 2 * math.pi
                turn_direction = math.copysign(1.0, delta_folding.azimuth)
                delta_folding.azimuth = (math.fabs(delta_folding.azimuth) - 2 * math.pi) * turn_direction
               
            if math.fabs(delta_folding.azimuth) > self.__telescope_velocity:
                comments.append("BIG_AZ")
            if math.fabs(delta_folding.elevation) > self.__telescope_velocity:
                comments.append("BIG_EL")
            # if math.fabs(self._current_satellite["chord"]) > self.__telescope_velocity:
            #     comments.append("BIG_CH")

            sign_azimuth = math.copysign(1, delta_folding.azimuth)
            sign_elevation = math.copysign(1, delta_folding.elevation)
            delta_azimuth = delta_folding.azimuth if math.fabs(delta_folding.azimuth) < self.__telescope_velocity else self.__telescope_velocity * sign_azimuth
            delta_elevation = delta_folding.elevation if math.fabs(delta_folding.elevation) < self.__telescope_velocity else self.__telescope_velocity * sign_elevation

            big_chord = math.fabs(delta_azimuth) >= self.__telescope_velocity or \
                math.fabs(delta_elevation) >= self.__telescope_velocity  # or \
                # self._current_satellite["chord"] >= self.__telescope_velocity
            new_azimuth = (self.station_folding.azimuth + delta_azimuth) % (2*math.pi)
            new_elevation = (self.station_folding.elevation + delta_elevation) % (math.pi)

            # print("ALT ..............azimuth={:11.6f}, elevation={:11.6f}".format(math.degrees(delta_azimuth), math.degrees(delta_elevation)))
               
            if big_chord:
                current_mode = MODE_TURNING
                comments.append("FAR_AWAY")

            if self.has_enough_obs() and (not no_other or not do_alternative):
                current_mode == MODE_TURNING

            if current_mode == MODE_TURNING:
                self._observation_time = 0
                # action["target"] = self._current_satellite["name"]
                action["priority"] = 9999

            elif current_mode == MODE_OBSERVING:
                self._observation_time += 1
                action["target"] = self._current_satellite["name"]
                action["priority"] = self._current_satellite["priority"]
                action[PK_COSPAR] = self._current_satellite[PK_COSPAR]
                action[PK_NORAD] = self._current_satellite[PK_NORAD]
                comments.append("OBS::{}".format(self._current_satellite["name"]))
            else:
                assert True==False, "How did i got here?"

            self.station_folding = FoldingSquare(
                azimuth=new_azimuth,
                elevation=new_elevation,
                distance=self._current_satellite["folding"].distance
            )

            # print("NEW", self.station_folding, self._current_satellite["name"], "# %04d" % self._observation_time)
            self.add_observed_satellite(self._current_satellite[PK_COSPAR])

            action["mode"] = current_mode
            action["azimuth"] = math.degrees(self.station_folding.azimuth)
            action["elevation"] = math.degrees(self.station_folding.elevation)
            action["observation_time"] = self._observation_time
            action["comments"] = ",".join(comments)

            if action["comments"]:
                print("\n# {}".format(action["comments"]))
                     
            action_list.append(action)
            i += self.__intervall
        
        sort_key = ""
        if self.sort_col in SORT_COL_CHOICES:
            sort_key = "-{}".format(self.sort_col)

        # show performed actions
        outfile = os.path.join(
            self.TLE_DATA_DIR, "results", 
            self._t_start.strftime("%Y%m%d-observations{}-{:02d}.csv".format(sort_key, self.__intervall))
        )

        with open(outfile, 'w', newline='') as csvfile:
            fieldnames = action_fields
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for action in action_list:
                writer.writerow(action)

        return action_list
