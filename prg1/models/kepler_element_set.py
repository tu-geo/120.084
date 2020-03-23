import math
import re
import datetime

from prg1.utils.constants import *
from prg1.utils.time_conversion import frac_to_time


def extract_decimal(value, show=False):
    result = re.match(r"(\ *(-?\d+)([-+])(\d+))|\ *(-?\d*\.?\d*)", str(value))
    rg = result.groups()
    if show:
        print("value: {}".format(value))
        print("groups: ", rg)
    if rg[-1] is not None:
        if "." in rg[-1]:
            return float(rg[-1])
        else:
            return eval("0.{}".format(rg[-1].strip()))
    else:
        return eval("0.{}e{}{}".format(
            rg[1].strip(), rg[2].strip(), rg[3].strip()
        ))


def get_dpa(p1, p2):
    return eval("0.{}e{}".format(
        p1.strip(), p2.strip()
    ))
        

class KeplerElementSet(object):

    DICTIONARY = {
        "m0": "mean_anomaly",
        "a": "major_axis",
        "e": "eccentricity",
        "omega": "right_ascension",
        "i": "inclination",
        "w": "argument_of_perigee",
        "t0": "timestamp"
    }

    def __init__(self, m0, e, a, omega, i, w, t0=None, **kwars):
        """
        Create KeplerElementSet

        :param m0: mean anomaly [rad]
        :type m0: float
        :param e: eccentricity
        :type e: float
        :param a: major axis
        :type a: float
        :param omega: longitude of the ascending node [rad]
        :type omega: float
        :param i: inclination [rad]
        :type i: float
        :param w: argument of periapsis [rad]
        :type w: float
        :param t0: time of periapsis
        :type t0: datetime.datetime
        """
        t0 = t0 if t0 is not None else datetime.datetime(2000, 1, 1).replace(tzinfo=datetime.timezone.utc)
        self.m0 = m0  # mean anomaly
        self.e = e  # eccentricity
        self.a = a  # major axis
        self.omega = omega  # longitude of the ascending node
        self.i = i  # inclination
        self.w = w  # argument of periapsis
        self.t0 = t0  # time of periapsis

    def __str__(self):
        return "KeplerElementSet(m0={0.m0}, e={0.e}, a={0.a}, omega={0.omega}, i={0.i}, w={0.w}, t0={0.t0}, n={0.n})".format(self)
    
    @property
    def n(self):
        """
        Get mean motion

        :return: mean motion of kepler elements [1/sec]
        :rtype: float
        """
        return math.sqrt(GE / math.pow(self.a, 3))

    @property
    def b(self):
        """
        Get minor axis

        :return: minor axis b of kepler elmenets [m]
        :rtype: float
        """
        return math.sqrt((1 - math.pow(self.e, 2)) * math.pow(self.a, 2))

    @property
    def f(self):
        """
        Get flattening

        :return: flattening f of kepler elmenets
        :rtype: float
        """
        return 1 - self.b / self.a
                
    def get_mean_anomaly(self, ti: datetime.datetime) -> float:
        """
        Get mean anomaly "M" for given timestamp ti

        :param ti: Timestamp to compute anomaly
        :type ti: datetime.datetime
        :return: Mean anomaly "M" for given timestamp [rad]
        :rtype: float
        """
        dt = (ti - self.t0).total_seconds()
        return self.n * dt

    @staticmethod
    def from_dict(kes: dict):
        kwargs = {}
        for k in KeplerElementSet.DICTIONARY:
            kwargs.update({k: kes[KeplerElementSet.DICTIONARY[k]]})
        return KeplerElementSet(**kwargs)

    @staticmethod
    def read_tle(norad_str):
        """
        0         1         2         3         4         5         6         7
        01234567890123456789012345678901234567890123456789012345678901234567890
        S-NET D
        1 43186U 18014G   20072.38042328 -.00000140  00000-0 -71529-5 0  9993
        2 43186  97.7004 341.7679 0010641 181.4469 178.6724 14.96767359115170
        """
        d = {}

        tle_title = re.compile(REGEX_TLE_TITLE)
        tle_line1 = re.compile(REGEX_TLE_1)
        tle_line2 = re.compile(REGEX_TLE_2)

        for line in norad_str.split("\n"):

            if len(line) <= 24 and tle_title.match(line):
                d["satellite_name"] = line.strip()
            else:
                if line.startswith("1"):
                    # NORAD Line 1
                    tle = tle_line1.match(line)
                    tle_groups = tle.groups()

                    d["satellite_catalog_number_1"] = tle_groups[0].strip()
                    d["classification"] = tle_groups[1].strip()
                    d["launch_year"] = tle_groups[2].strip()
                    d["launch_year_number"] = tle_groups[3].strip()
                    d["launch_piece"] = tle_groups[4].strip()
                    d["epoch_year"] = tle_groups[5].strip()
                    d["epoch_doy"] = int(tle_groups[7])
                    d["epoch_fractal"] = float(tle_groups[8])
                    d["ballistic_coefficient"] = float(tle_groups[9])
                    d["mean_motion_dot_dot"] = get_dpa(tle_groups[11], tle_groups[12])
                    d["radiation_pressure_coefficient"] = get_dpa(tle_groups[14], tle_groups[15])
                    d["ephemeris_type"] = tle_groups[16].strip()
                    d["element_set_number"] = tle_groups[17].strip()
                    d["checksum_1"] = tle_groups[18].strip()

                    # derived attributes #1
                    t = frac_to_time(d["epoch_fractal"])
                    ts = datetime.datetime.strptime(
                        "{}-{:03d}T{:02d}:{:02d}:{:09.6f}".format(
                            d["epoch_year"], d["epoch_doy"],
                            t.hour, t.minute, t.second + t.microsecond * 1e-3
                        ),
                        "%y-%jT%H:%M:%S.%f"
                    ).replace(tzinfo=datetime.timezone.utc)
                    d["timestamp"] = ts

                elif line.startswith("2"):
                    # NORAD Line 2
                    tle = tle_line2.match(line)
                    tle_groups = tle.groups()

                    d["satellite_catalog_number_2"] = tle_groups[0].strip()
                    d["inclination"] = math.radians(float(tle_groups[1].strip()))
                    d["right_ascension"] = math.radians(float(tle_groups[2].strip()))
                    d["eccentricity"] = eval("0.{}".format(tle_groups[3].strip()))
                    d["argument_of_perigee"] = math.radians(float(tle_groups[4]))
                    d["mean_anomaly"] = math.radians(float(tle_groups[5]))
                    d["mean_motion"] = float(tle_groups[6])
                    d["revolutions"] = int(tle_groups[7].strip())
                    d["checksum_2"] = tle_groups[8].strip()

                    # derived attributes #2
                    d["major_axis"] = math.pow(GE / math.pow(d["mean_motion"] * 2 * math.pi / 86400, 2), 1.0 / 3.0)
                    d["minor_axis"] = math.sqrt((1 - math.pow(d["eccentricity"], 2)) * math.pow(d["major_axis"], 2))
                    d["flattening"] = 1 - d["minor_axis"]/d["major_axis"]
                    d["period_of_revolution"] = math.sqrt(4 * math.pow(math.pi, 2) * math.pow(d["major_axis"], 3) / GE)
        return d
