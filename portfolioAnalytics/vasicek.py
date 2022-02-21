# encoding: utf-8
# (c) 2017-2022 Open Risk (https://www.openriskmanagement.com)
#
# portfolioAnalytics is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of TransitionMatrix. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.

""" Implementing the credit portfolio model of Vasicek.

See `Vasicek Distribution <https://www.openriskmanual.org/wiki/Vasicek_Distribution>`_


"""

import math

from scipy import stats
from sympy import binomial

from portfolioAnalytics import settings


def vasicek_base(N, k, p, rho):
    """Vasicek Base Discrete distribution.

    :param N: The number of entities in the portfolio
    :param k: The number of defaults
    :param p:   The probability of default (uniform across the portfolio)
    :param rho: The asset correlation parameter
    :return: The probability of k defaults
    """

    zmin = - settings.SCALE
    zmax = settings.SCALE
    grid = settings.GRID_POINTS

    dz = float(zmax - zmin) / float(grid - 1)
    a = stats.norm.ppf(p, loc=0.0, scale=1.0)
    integral = 0
    for i in range(1, grid):
        z = zmin + dz * i
        arg = (a - rho * z) / math.sqrt(1 - rho * rho)
        phi_den = stats.norm.pdf(z, loc=0.0, scale=1.0)
        phi_cum = stats.norm.cdf(arg, loc=0.0, scale=1.0)
        integrant = phi_den * math.pow(phi_cum, k) * math.pow(1 - phi_cum, N - k) * binomial(N, k)
        integral = integral + integrant
    return dz * integral


def vasicek_base_el(N, p, rho):
    """Expected Loss for the Vasicek Base distribution.

    :param N: The number of entities in the portfolio
    :param p:   The probability of default
    :param rho: The asset correlation (not needed here)
    :return: The average default rate / loss
    """
    return N * p


def vasicek_base_ul(N, p, rho):
    """Unexpected Loss (Standard Deviation) for the Vasicek Base distribution.

    :param N: The number of entities in the portfolio
    :param p: The probability of default
    :param rho: The asset correlation (not needed here)
    :return: The default rate volatility (UL)
    """
    zmin = - settings.SCALE
    zmax = settings.SCALE
    grid = settings.GRID_POINTS

    dz = float(zmax - zmin) / float(grid - 1)
    a = stats.norm.ppf(p, loc=0.0, scale=1.0)
    integral = 0
    for i in range(1, grid):
        z = zmin + dz * i
        arg = (a - rho * z) / math.sqrt(1 - rho * rho)
        phi_den = stats.norm.pdf(z, loc=0.0, scale=1.0)
        phi_cum = stats.norm.cdf(arg, loc=0.0, scale=1.0)
        integrant = phi_den * math.pow(phi_cum, 2)
        integral = integral + integrant
    result = p / N - p * p + float(N - 1) / float(N) * dz * integral
    return N * math.sqrt(result)


def vasicek_lim(theta, p, rho):
    """The Large-N limit of the Vasicek Distribution.

    :param theta: The target default rate
    :param p:   The probability of default
    :param rho: The asset correlation
    :return: Cumulative probability
    """
    a1 = stats.norm.ppf(p, loc=0.0, scale=1.0)
    arg1 = stats.norm.ppf(theta, loc=0.0, scale=1.0)
    arg2 = (math.sqrt(1 - rho * rho) * arg1 - a1) / rho
    result = stats.norm.cdf(arg2, loc=0.0, scale=1.0)
    return result


def vasicek_lim_el(p, rho):
    """The expected loss of the large n limit of the Vasicek distribution.

    :param p: The probability of default
    :param rho: The asset correlation (not needed)
    :return: The expected default rate
    """
    return p


def vasicek_lim_ul(p, rho):
    """The unexpected loss of the large n limit of the Vasicek distribution.

    :param p:  The probability of default
    :param rho: The asset correlation
    :return: The default rate volatility
    """
    zmin = - settings.SCALE
    zmax = settings.SCALE
    grid = settings.GRID_POINTS
    dz = float(zmax - zmin) / float(grid - 1)
    a = stats.norm.ppf(p, loc=0.0, scale=1.0)
    integral = 0
    for i in range(1, grid):
        z = zmin + dz * i
        arg = (a - rho * z) / math.sqrt(1 - rho * rho)
        phi_den = stats.norm.pdf(z, loc=0.0, scale=1.0)
        phi_cum = stats.norm.cdf(arg, loc=0.0, scale=1.0)
        integrant = phi_den * math.pow(phi_cum, 2)
        integral = integral + integrant
    result = - p * p + dz * integral
    return math.sqrt(result)


def vasicek_lim_q(alpha, p, rho):
    """The quantile of the large-n Limit of the Vasicek distribution.

    :param alpha: The desired quantile
    :param p:   The probability of default
    :param rho: The asset correlation
    :return:  The default rate at that confidence level
    """
    a1 = stats.norm.ppf(p, loc=0.0, scale=1.0)
    a2 = stats.norm.ppf(alpha, loc=0.0, scale=1.0)
    arg = (a1 + rho * a2) / math.sqrt(1 - rho * rho)
    return stats.norm.cdf(arg, loc=0.0, scale=1.0)
