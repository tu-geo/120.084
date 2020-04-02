import math

def great_circle(lon_a, lat_a, lat_b, lon_b):
    """
    Calculate great circle between two points on a squere

    :param lon_a: Longitude, point A [rad]
    :type lon_a: float
    :param lat_a: Latitude, point A [rad]
    :type lat_a: float
    :param lon_b: Longitude, point B [rad]
    :type lon_b: float
    :param lat_b: Latitude, point B [rad]
    :type lat_b: float
    :return: Angle of creat circle between point A and B [rad]
    :rtype: float
    """

    return math.acos(
        math.sin(lat_a) * math.sin(lat_b) + \
        math.cos(lat_a) * math.cos(lat_b) * math.cos(lon_b - lon_a)
    )
