import math
import re


def extract_decimal(value):
    result = re.match(r"(-?\d*\.\d*)|((-?\d*)([-+])(\d+))", str(value))
    rg = result.groups()
    if rg[0] is not None:
        return float(rg[0])
    else:
        return eval("{}e{}{}".format(
            rg[2], rg[3], rg[4]
        ))
        

class KeplerElementSet(object):
    def __init__(self, m0, e, a, omega, i, w):
        self.m0 = m0  # anomaly
        self.e = e  # eccentricity
        self.a = a  # major axis
        self.omega = omega  # longitude of the ascending node
        self.i = i  # inclination
        self.w = w  # argument of periapsis

    def from_norad(self, norad_str):
        """
        S-NET D
        1 43186U 18014G   20072.38042328 -.00000140  00000-0 -71529-5 0  9993
        2 43186  97.7004 341.7679 0010641 181.4469 178.6724 14.96767359115170
        """
        norad_str = """S-NET D
0         1         2         3         4         5         6         7
01234567890123456789012345678901234567890123456789012345678901234567890
1 43186U 18014G   20072.38042328 -.00000140  00000-0 -71529-5 0  9993
2 43186  97.7004 341.7679 0010641 181.4469 178.6724 14.96767359115170"""
        for line in norad_str.split("\n"):
            if len(line) <= 24:
                satellite_number = line.strip()
            else:
                # NORAD Line 1
                if line[0] == "1":
                    satellite_catalog_number = line[2:6]
                    classification = line[7]
                    launch_year = line[9:10]
                    launch_year_number = line[11:13]
                    launch_piece = line[14:16]
                    epoch_year = line[18:19]
                    epoch_date = extract_decimal(line[20:31])
                    ballistic_coefficient = extract_decimal(line[33:42])
                    mean_motion_dot_dot = extract_decimal(line[44:51])
                    radiation_pressure_coefficient = extract_decimal(line)
                    ephemeris_type = line[62]
                    element_set_number = line[64:67]
                    checksum_1 = line[68]
                elif line[0] == "2":
                    satellite_catalog_number = line[2:6]
                    inclination = extract_decimal(line[8:15])
                    right_ascension = extract_decimal(line[17:24])
                    eccentricity = extract_decimal(line[26:32])
                    argument_of_perigee = extract_decimal(line[34:41])
                    mean_anomaly = extract_decimal(line[43:50])
                    mean_motion = extract_decimal(line[52:62])
                    revolutions = extract_decimal(line[63:67])
                    checksum_2 = line[68]
