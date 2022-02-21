# encoding: utf-8

"""This module is part of the portfolioAnalytics package."""

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

import json

import portfolioAnalytics.vasicek as va


class LossDistribution(object):
    """The Loss Distribution object exposes the core functionality of the portfolioAnalytics library.a

    Depending on the selected method, it produces estimates of the moments of loss distribution, or point estimates for a given stress scenario.


    .. Todo:: Something to do
    """

    def __init__(self):
        """Create a new loss distribution object.

        :returns: returns a ThresholdSet object
        :rtype: object

        .. note:: The loss distribution object

        :Example:

        Instantiate a loss distribution object

        M = pa.model.LossDistribution()

        """
        # Single period is default
        self.periods = 1
        self.mean = []
        self.stddev = []
        self.quantiles = {}

    def calculate(self, method=None, periods=None, portfolio=None, asset_correlation=None, scenario=None):
        """Calculate a loss distribution given a method, a portfolio and (optionally) a scenario.

        .. note::

        """
        # Calculate moments for all periods
        print('Calculating Loss Distribution using Method: ', method)
        for t in range(self.periods):
            print('Period: ', t)
            if method == 'Finite_Vasicek':
                # calculate average PD
                N, p = portfolio.preprocess_portfolio()
                self.mean.append(va.vasicek_base_el(N, p, asset_correlation))
                self.stddev.append(va.vasicek_base_ul(N, p, asset_correlation))

    def to_json(self, json_file=None, accuracy=5):
        """Serialize to JSON.


        """
        something = []
        serialized = json.dumps(something, indent=2, separators=(',', ': '))
        return serialized

    def from_json(self, json_file):
        """Read from JSON.

        """
        pass

    def print_moments(self, format_type='Standard', accuracy=2):
        """Pretty print the distribution moments.

        :param format_type: formatting options (Standard, Percent)
        :type format_type: str
        :param accuracy: number of decimals to display
        :type accuracy: int

        """
        """
        Pretty-print a summary of estimation results (values and confidence intervals)
        """
        print('                      Loss Distribution Calculation Results                    ')
        print('==============================================================================')
        print('Confidence Levels: ', self.quantiles)
        print('------------------------------------------------------------------------------')
        for t in range(self.periods):
            print('Mean    Stddev')
            format_string = "{0:." + str(accuracy) + "f}"
            # print(format_string.format(self.mean[t]) + ' ', end='')
            el = self.mean[t]
            ul = self.stddev[t]
            print('{0:.4f} {1:.4f} {2:.4f} {3:.4f} {4:.4f}'.format(el, ul, 0, 0, 0))
            print('..............................................................................')
        print('==============================================================================')


    def plot(self, rating):
        """Plot the loss distributions.

        """
        pass
