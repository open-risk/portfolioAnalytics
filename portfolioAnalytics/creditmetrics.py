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


import math

from scipy import stats

from portfolioAnalytics.utils import bivariatenormal as bv

"""Implement Credit Metrics style variance calculations.


"""


# wrapper for inverse cumulative normal density
def Ninv(x):
    """Inverse normal function.

    """
    return stats.norm.ppf(x, loc=0.0, scale=1.0)


# calculate portfolio default rate variance


def variance(portfolio, correlation, loadings):
    """Variance calculation.


    """
    n = portfolio.psize
    variance_sum = 0.0
    name_var = 0.0

    # Portfolio Variance du to correlation
    for i in range(n):
        for j in range(i):
            p1 = portfolio.rating[i]
            p2 = portfolio.rating[j]
            a1 = Ninv(p1)
            a2 = Ninv(p2)
            Omega = correlation[portfolio.factor[i], portfolio.factor[j]]
            rho = loadings[portfolio.factor[i]] * loadings[portfolio.factor[j]] * Omega
            variance_pair = portfolio.exposure[i] * portfolio.exposure[j] * (
                    bv.BivariateNormalDistribution(a1, a2, rho) - p1 * p2)
            variance_sum += variance_pair

    # Idiosyncratic Portfolio Variance due to name concentration
    for i in range(n - 1):
        p1 = portfolio.rating[i]
        name_var += portfolio.exposure[i] * portfolio.exposure[i] * (p1 - p1 * p1)

    return 2 * variance_sum + name_var


def creditmetrics_el(portfolio, correlation, loadings):
    """Credit Metrics Expected Loss Calculation.


    """
    n = portfolio.psize
    el = 0.0
    print(portfolio)
    for entry in portfolio:
        print(entry['EAD'])

    # TODO FIX THIS
    for i in range(n):
        p1 = portfolio.rating[i]
        # el += portfolio.[i] * p1
        el += 0
    return el


def creditmetrics_ul(portfolio, correlation, loadings):
    """Credit Metrics Loss Volatility (Standard Deviation of Loss)

    """
    result = variance(portfolio, correlation, loadings)
    return math.sqrt(result)
