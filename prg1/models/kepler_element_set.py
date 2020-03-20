import math
import re

from prg1.utils.constants import GE


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
        

class KeplerElementSet(object):
    def __init__(self, m0, e, a, omega, i, w):
        self.m0 = m0  # anomaly
        self.e = e  # eccentricity
        self.a = a  # major axis
        self.omega = omega  # longitude of the ascending node
        self.i = i  # inclination
        self.w = w  # argument of periapsis

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
        for line in norad_str.split("\n"):
            #print("Parsing", line)
            if len(line) <= 24:
                d["satellite_number"] = line.strip()
            else:
                # NORAD Line 1
                if line[0] == "1":
                    d["satellite_catalog_number"] = line[2:7]
                    d["classification"] = line[7].strip()
                    d["launch_year"] = line[9:11].strip()
                    d["launch_year_number"] = line[11:14].strip()
                    d["launch_piece"] = line[14:17].strip()
                    d["epoch_year"] = line[18:20].strip()
                    d["epoch_date"] = extract_decimal(line[20:32])
                    d["ballistic_coefficient"] = extract_decimal(line[33:43])
                    d["mean_motion_dot_dot"] = extract_decimal(line[44:52])
                    d["radiation_pressure_coefficient"] = extract_decimal(line[52:62])
                    d["ephemeris_type"] = line[62].strip()
                    d["element_set_number"] = line[64:68].strip()
                    d["checksum_1"] = line[68].strip()
                elif line[0] == "2":
                    # d["satellite_catalog_number"] = line[2:6]
                    d["inclination"] = extract_decimal(line[8:16])
                    d["right_ascension"] = extract_decimal(line[17:25])
                    d["eccentricity"] = extract_decimal(line[26:33])
                    d["argument_of_perigee"] = extract_decimal(line[34:42])
                    d["mean_anomaly"] = extract_decimal(line[43:51])
                    d["mean_motion"] = extract_decimal(line[52:63])
                    d["revolutions"] = extract_decimal(line[63:67])
                    d["checksum_2"] = line[68].strip()

                    # derived attributes
                    d["major_axis"] = math.pow(GE/math.pow(d["mean_motion"]*2*math.pi/86400, 2), 1.0/3.0)
        return d