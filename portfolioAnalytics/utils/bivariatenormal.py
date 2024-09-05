# -*- coding: utf-8 -*-
# encoding: utf-8

"""Implementation of the bivariate normal function."""

# (c) 2017-2024 Open Risk (https://www.openriskmanagement.com)
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


import math

from scipy import stats


# all arguments are double

# wrapper for cumulative normal density
def N(x):
    """Standard Normal."""
    return stats.norm.cdf(x, loc=0.0, scale=1.0)


def BivariateNormalDistribution(a, b, rho):
    """Bivariate Normal Distribution.

    based on Z. Drezner, "Computation of the bivariate normal integral",
    Mathematics of Computation 32, pp. 277-279, 1978.
    uses 8-point Gaussian quadrature

    """
    Epsilon = 1e-12

    if rho > 1 - Epsilon:
        if a < b:
            value = N(a)
        else:
            value = N(b)
        return value

    if rho < -(1 - Epsilon):
        if a < -b:
            value = 0
        else:
            value = N(a) - N(-b)
        return value

    if a <= 0 and b <= 0 and rho <= 0:
        value = Phi_Sum(a, b, rho)
    elif a <= 0 <= b and rho >= 0:
        value = N(a) - Phi_Sum(a, -b, -rho)
    elif a >= 0 and b <= 0 and rho >= 0:
        value = N(b) - Phi_Sum(-a, b, -rho)
    elif a >= 0 and b >= 0 and rho <= 0:
        value = N(a) + N(b) - 1 + Phi_Sum(-a, -b, rho)
    else:
        value = BivariateNormalDistribution(a, 0, rhoc(a, b, rho))
        value = value + BivariateNormalDistribution(b, 0, rhoc(b, a, rho))
        if (a > 0 and b < 0) or (a < 0 and b > 0):
            value = value - 0.5
    return value


def BivariateNormalDensity(a, b, rho):
    """Bivariate Normal Density."""
    ONE_OVER_2PI = 0.15915494309189533576888376337251
    ONE_OVER_SQRT_ONE_MIN_RHO_SQRD = 1. / math.sqrt(1. - rho * rho)
    return ONE_OVER_2PI * ONE_OVER_SQRT_ONE_MIN_RHO_SQRD * math.exp(
        -0.5 * ONE_OVER_SQRT_ONE_MIN_RHO_SQRD * ONE_OVER_SQRT_ONE_MIN_RHO_SQRD * (a * a + b * b - 2. * rho * a * b))


def Phi_Sum(a, b, rho):
    """Phi Sum Helper Function."""
    PI = 3.1415926535897932384626433832795
    SUMNUM = 8

    Apara = [0.13410918845336,
             0.26833075447264,
             0.275953397988422,
             0.15744828261879,
             4.48141099174625E-02,
             5.36793575602526E-03,
             2.02063649132407E-04,
             1.19259692659532E-06]

    Bpara = [5.29786439318514E-02,
             0.267398372167767,
             0.616302884182402,
             1.06424631211623,
             1.58885586227006,
             2.18392115309586,
             2.86313388370808,
             3.6860071627244]

    srtomr2 = math.sqrt(1.0 - rho) * math.sqrt(1.0 + rho)
    fpa = a / (math.sqrt(2.0) * srtomr2)
    fpb = b / (math.sqrt(2.0) * srtomr2)

    sum = 0.0
    for i in range(SUMNUM):
        temp = 0.0
        fpai = Bpara[i] - fpa
        for j in range(SUMNUM):
            temp = temp + Apara[j] * math.exp(fpb * (2.0 * Bpara[j] - fpb) + 2.0 * rho * fpai * (Bpara[j] - fpb))
        sum = sum + Apara[i] * math.exp(fpa * (2.0 * Bpara[i] - fpa)) * temp

    return sum * srtomr2 / PI


def rhoc(a, b, rho):
    """Rho_c Helper Function."""
    x = 1.0
    if a < 0:
        x = -1.0
    return x * (rho * a - b) / math.sqrt(a * a - 2 * rho * a * b + b * b)
