import math

from prg1.models.point import GeocentricPoint
from prg1.models.nuisance_parameter_set import NuisanceParameterSet
from prg1.utils.constants import GE, OMEGA_E_DOT, T_0E


def orbit_to_cart(ke, nps, t0, ti, t0e=T_0E, eps=1e-10):
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

    if nps is None:
        nps = NuisanceParameterSet()
    # Zeitdifferenz
    delta_t = ti - t0
    # korrektur der mittleren Bewegung
    n_k  = math.sqrt(GE/math.pow(ke.a, 3)) + nps.delta_n
    # Berechnung der mittleren Anomalie
    m_k = ke.m0 + n_k * delta_t
    # Berechnung der exzentrischen Anomalie
    e_k_new = m_k + ke.e * math.sin(m_k)
    delta_e = eps+1
    i = 0
    while delta_e >= eps:
        i += 1
        e_k_old = e_k_new
        e_k_new = m_k + ke.e * math.sin(e_k_old)
        delta_e = math.fabs(e_k_old - e_k_new)
    e_k = e_k_new
    # Berechnung der wahren Anomalie
    v_k = 2 * math.atan(math.sqrt((1.0 + ke.e)/(1.0 - ke.e)) * math.tan(e_k/2.0))
    # Berechnung der Breite
    phi_k = ke.w + v_k
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
    i_k = ke.i
    i_k += nps.i_dot * delta_t + delta_i
    # Korrigierte Rektaszension
    omega_k = ke.omega - OMEGA_E_DOT * T_0E
    omega_k -= (OMEGA_E_DOT - nps.omega_dot) * delta_t
    # Position in der Bahnebene
    x_ks = r_k * math.cos(u_k)
    y_ks = r_k * math.sin(u_k)
    # Position im Raum
    x_k = x_ks * math.cos(omega_k) - y_ks * math.sin(omega_k) * math.cos(i_k)
    y_k = x_ks * math.sin(omega_k) + y_ks * math.cos(omega_k) * math.cos(i_k)
    z_k = y_ks * math.sin(i_k)
    return GeocentricPoint(x_k, y_k, z_k)
