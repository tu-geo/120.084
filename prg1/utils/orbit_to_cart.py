import math

from prg1.models.point import GeocentricPoint
from prg1.models.nuisance_parameter_set import NuisanceParameterSet
from prg1.utils.constants import GE, OMEGA_E_DOT
from prg1.utils.angle_conversion import deg_to_rad as d2r, rad_to_deg as r2d


def orbit_position(ke, ti, eps=1e-10):
    """
    http://calculuscastle.com/orbit.pdf - Algorithm 44.2 "OrbitPosition"
    returns (x, y)
    """
    delta_t = (ti - ke.t0).total_seconds()
    big_m = ke.n * delta_t
    big_e = big_m + ke.e * math.sin(big_m)
    tmp_e = big_m
    # i = 0
    while math.fabs(big_e - tmp_e) > eps:
        tmp_e = big_e
        big_e = big_m + ke.e * math.sin(tmp_e)
        # i += 1
    # print("Took {} iterations", i)
    x = ke.a * (math.cos(big_e) - ke.e)
    y = ke.a * math.sqrt(1 - math.pow(ke.e, 2)) * math.sin(big_e)
    return [x, y]


def pq_to_xyz(ke, p, q):
    """
    http://calculuscastle.com/orbit.pdf - Algorithm 44.4 "PQ2XYZ"

    (p, q), coordinates in (p, q) (from OrbitPosition)
    1: px ← cos ω cos Ω − sin ω cos i sin Ω
    2: py ← cos ω sin Ω + sin ω cos i cos Ω
    3: pz ← sin ω sin i
    4: qx ← − sin ω cos Ω − cos ω cos i sin Ω
    5: qy ← − sin ω sin Ω + cos ω cos i cos Ω
    6: qz ← sin i cos ω
    7: wx ← sin i sin Ω
    8: wy ← − sin i cos Ω
    9: wz ← cos i
    10: r ← (ppx + qqx)i + (ppy + qqy)j + (ppz + qqz)k
    11: return r
    """
    px = math.cos(ke.w) * math.cos(ke.omega) - math.sin(ke.w) * math.cos(ke.i) * math.sin(ke.omega)
    py = math.cos(ke.w) * math.sin(ke.omega) + math.sin(ke.w) * math.cos(ke.i) * math.cos(ke.omega)
    pz = math.sin(ke.w) * math.sin(ke.i)

    qx = -math.sin(ke.w) * math.cos(ke.omega) - math.cos(ke.w) * math.cos(ke.i) * math.sin(ke.omega)
    qy = -math.sin(ke.w) * math.sin(ke.omega) + math.cos(ke.w) * math.cos(ke.i) * math.cos(ke.omega)
    qz = math.sin(ke.i) * math.sin(ke.omega)

    return GeocentricPoint(
        x=p * px + q * qx,
        y=p * py + q * qy,
        z=p * pz + q * qz
    )


def orbit_to_cart2(ke, ti, eps=1e-10):
    """
    """
    p, q = orbit_position(ke, ti, eps)
    return pq_to_xyz(ke, p, q)


def orbit_to_cart(ke, nps, ti, t0e=0.0, eps=1e-10):
    """
        Calculate cartesian coordinates for a setllite at a specific time
        :param ke: Kepler elements
        :type ke: KeplerElements
        :param nps: Nuisance parameter set
        :type nps: NuisanceParameterSet
        :param t0: Start time of orbital parameters
        :param ti: Time for which coordinates shall be calculated
        
        :returns: Geocentric Point at time for orbital parameters
        :rtype: Geocentric Point
    """

    m0 = ke.m0
    i = ke.i
    w = ke.w
    omega = ke.omega

    if nps is None:
        nps = NuisanceParameterSet()
    # Zeitdifferenz
    delta_t = (ti - ke.t0).total_seconds()
    # korrektur der mittleren Bewegung
    n_k  = math.sqrt(GE/math.pow(ke.a, 3)) + nps.delta_n
    # Berechnung der mittleren Anomalie
    m_k = m0 + n_k * delta_t
    # Berechnung der exzentrischen Anomalie
    e_k_old = m_k
    e_k_new = m_k + ke.e * math.sin(e_k_old)
    while math.fabs(e_k_old - e_k_new) > eps:
        e_k_old = e_k_new
        e_k_new = m_k + ke.e * math.sin(e_k_old)
    e_k = e_k_new
    # Berechnung der wahren Anomalie
    v_k = 2 * math.atan(math.sqrt((1.0 + ke.e)/(1.0 - ke.e)) * math.tan(e_k/2.0))
    # Berechnung der Breite
    phi_k = w + v_k
    # Breiten_korrektur
    delta_u = nps.c_uc * math.cos(2.0 * phi_k) + nps.c_us * math.sin(2.0 * phi_k)
    # Radiuskorrektur
    delta_r = nps.c_rc * math.cos(2.0 * phi_k) + nps.c_rs * math.sin(2.0 * phi_k)
    # In_klinationskorrektur
    delta_i = nps.c_ic * math.cos(2.0 * phi_k) + nps.c_is * math.sin(2.0 * phi_k)
    # Korrigiertes Argument der Breite
    u_k = phi_k
    u_k += delta_u
    # Korrigierter Radius
    r_k = ke.a * (1.0 - ke.e * math.cos(e_k))
    r_k += delta_r
    # Korrigierte Inklination
    i_k = i
    i_k += nps.i_dot * delta_t + delta_i
    # Korrigierte Rektaszension
    omega_k = omega - OMEGA_E_DOT * t0e
    omega_k -= (OMEGA_E_DOT - nps.omega_dot) * delta_t
    # Position in der Bahnebene
    x_ks = r_k * math.cos(u_k)
    y_ks = r_k * math.sin(u_k)
    # Position im Raum
    x_k = x_ks * math.cos(omega_k) - y_ks * math.sin(omega_k) * math.cos(i_k)
    y_k = x_ks * math.sin(omega_k) + y_ks * math.cos(omega_k) * math.cos(i_k)
    z_k = y_ks * math.sin(i_k)
    
    return GeocentricPoint(x_k, y_k, z_k)
