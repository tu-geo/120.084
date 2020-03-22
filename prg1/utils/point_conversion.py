import logging
import numpy as np

from prg1.models.point import GeographicPoint, GeocentricPoint
from prg1.utils.angle_conversion import deg_to_rad as d2r, rad_to_deg as r2d


ELLIPSOID_AXIS_MAJOR = 6378137.0
ELLIPSOID_FLATTENING = 1/298.257222101
ELLIPSOIDAL_EPS = 1e-12


logger = logging.getLogger(__name__)


def convert_ellipsoidal_to_cartesian(src_point, axis_major=ELLIPSOID_AXIS_MAJOR, flattening=ELLIPSOID_FLATTENING):
    """
        Conversion from ellipsoidal to cartesian coordinates

        :param src_point: Source point with geographic coordinates
        :param axis_major: Major axis 'a' of ellipsoid
        :param flattening: Flattening 'f' of ellipsoid

        :returns: Point with cartesian coordinates
    """
    e2 = 2 * flattening - np.power(flattening, 2)
    phi_rad = d2r(src_point.lat)
    lam_rad = d2r(src_point.lon)
    height = src_point.ele
    cuvature_radius = axis_major / np.sqrt( 1.0 - e2 * np.power(np.sin(phi_rad), 2))
    x = (cuvature_radius + height) * np.cos(phi_rad) * np.cos(lam_rad)
    y = (cuvature_radius + height) * np.cos(phi_rad) * np.sin(lam_rad)
    z = ((1.0 - e2) * cuvature_radius + height) * np.sin(phi_rad)
    return GeocentricPoint(x, y, z)


def convert_cartesian_to_ellipsoidal(src_point, axis_major=ELLIPSOID_AXIS_MAJOR, flattening=ELLIPSOID_FLATTENING, eps=ELLIPSOIDAL_EPS):
    """
        Conversion from cartesian to ellipsoidal coordinates

        :param src_point: Source point with cartesian coordinates
        :param axis_major: Major axis 'a' of ellipsoid
        :param flattening: Flattening 'f' of ellipsoid

        :returns: Point with ellipsoidal coordinates
    """
    e2 = 2 * flattening - np.power(flattening, 2)
    x = src_point.x
    y = src_point.y
    z = src_point.z

    # Determine Longitude
    lon_rad = np.arctan2(y, x)

    # Determine Latitude
    p = np.sqrt(np.power(x, 2) + np.power(y, 2))
    phi_new = np.arctan2(z, (1 - e2) * p)  # Initial latidude
    delta_e = eps+1
    i = 0
    while delta_e >= eps and i < 20:
        i += 1
        phi_old = phi_new
        n_i = axis_major / np.sqrt(1 - e2 * np.power(np.sin(phi_old), 2))
        h_i = p / np.cos(phi_old) - n_i
        phi_new = np.arctan2(z, (1 - e2 * n_i / (n_i + h_i)) * p)
        delta_e = np.absolute(phi_old - phi_new)
    logger.debug("Needed {} iterations".format(i))
    phi_rad = phi_new
    ele = h_i
    return GeographicPoint(r2d(lon_rad) % 360, r2d(phi_rad), ele)


def to_local_enu(point_station, point_satellite):
    """
        Get local vector from station to satellite

        :param point_station: Ellipsoidal coordinates of station
        :param point_satellite: Ellipsoidal coordinates of satellite
        :returns: vector ENU from station to satellite
    """
    assert isinstance(point_satellite, GeographicPoint)
    assert isinstance(point_station, GeographicPoint)

    phi = d2r(point_station.lat)
    lam = d2r(point_station.lon)

    sta_xyz = convert_ellipsoidal_to_cartesian(point_station)
    sat_xyz = convert_ellipsoidal_to_cartesian(point_satellite)
    
    diff_xyz = sat_xyz - sta_xyz
    diff_vec = np.array((
        (diff_xyz.x),
        (diff_xyz.y),
        (diff_xyz.z)
    ))

    # Create Rotation Matrix
    rotation_e = np.array((
        (-np.sin(lam),                  np.cos(lam),                   0.0),
        (-np.sin(phi) * np.cos(lam), -np.sin(phi) * np.sin(lam), np.cos(phi)),
        (np.cos(phi) * np.cos(lam),  np.cos(phi) * np.sin(lam),  np.sin(phi))
    ))

    # Create local vector ENU
    enu_vec = np.dot(rotation_e, diff_vec/np.linalg.norm(diff_vec))
    return enu_vec


def get_azimuth_and_elevation(point_station, point_satellite):
    """
        Get azimuth und elevation from station to satellite

        :param point_station: Ellipsoidal coordinates of station
        :param point_satellite: Ellipsoidal coordinates of satellite
        :returns: azimuth and elevation from station to satellite
    """
    lat_sta = d2r(point_station.lat)  # B
    lon_sta = d2r(point_station.lon)  # L
    lon_sat = d2r(point_satellite.lon)  # P
    lon_diff = lon_sta - lon_sat

    sta_xyz = convert_ellipsoidal_to_cartesian(point_station)
    sat_xyz = convert_ellipsoidal_to_cartesian(point_satellite)
    diff_xyz = sat_xyz - sta_xyz
    diff_vec = np.array((
        (diff_xyz.x),
        (diff_xyz.y),
        (diff_xyz.z)
    ))
    diff_l = np.linalg.norm(diff_vec)

    azimuth = np.arctan2(
        - np.sin(lon_sta) * diff_xyz.x + np.cos(lon_sta) * diff_xyz.y,
        - np.sin(lat_sta) * np.cos(lon_sta) * diff_xyz.x - np.sin(lat_sta) * np.sin(lon_sta) * diff_xyz.y + np.cos(lat_sta) * diff_xyz.z
    )
    elevation = np.arccos((
        np.cos(lat_sta) * np.cos(lon_sta) * diff_xyz.x + np.cos(lat_sta) * np.sin(lon_sta) * diff_xyz.y + np.sin(lat_sta) * diff_xyz.z
    ) / diff_l)

    return [r2d(azimuth), r2d(elevation)]



def xyz2ell(src_point, axis_major, flattening):
    """
    JUST COMPARING (Transformator.bev.gv.at) convert_cartesian_to_ellipsoidal
    Geocentric -> Geographic

    :type point: GeocentricPoint
    :type ellipsoid: Ellipsoid
    :rtype: GeographicPoint

    see header of ell2xyz

    input:  x     x-coordinate in meters
            y     y coordinate in meters
            z     z-coordinate in meters
            ellipsoid  input of type ell (defined in module trafo)
    output: lon   ellipsoidal longitude in degree
            lat   ellipsoidal (geodetic) latitude idegreee
            h     ellipsoidal height in meters
    """

    # check for numeric and dim must be one

    x = src_point.x
    y = src_point.y
    z = src_point.z

    a = axis_major
    b = a * (1.0 - flattening)
    e2 = 2 * flattening - np.power(flattening, 2)

    p = np.sqrt(x**2 + y**2)

    curlon = np.arctan2(y, x)
    if p == 0:
        #logger.warn("point is at pole -> lon is arbitrary (set to 0)")
        curlon = 0
        if z < 0:  # south pole:
            curlat = -np.pi / 2
            curh = -z - b
        else:  # north pole
            curh = z - b
            curlon = np.pi / 2

    N = 0
    h = 0
    lastlat = 99999
    curlat = np.arctan2(z, (1 - e2) * p)
    maxk = 1000000
    k = 1

    while abs(curlat - lastlat) > 1e-15:
        k += 1
        N = a / np.sqrt(1 - e2 * np.power(np.sin(lastlat), 2))
        h = p / np.cos(lastlat) - N
        lastlat = curlat
        curlat = np.arctan2(z, (1 - e2 * N / (N + h)) * p)
        # break when max num is reached
        if k == maxk:
            break

    return GeographicPoint(
        #name=point.name,
        lat=r2d(curlat),
        lon=r2d(curlon),
        ele=h
    )
