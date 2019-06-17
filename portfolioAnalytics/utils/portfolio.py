# encoding: utf-8

# (c) 2019 Open Risk (https://www.openriskmanagement.com)
#
# portfolioAnalytics is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of correlationMatrix. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides simple functionality for holding portfolio data for calculation purposes."""


class Portfolio(object):
    """The Portfolio Class."""

    def __init__(self, psize=0, rating=[], exposure=[], factor=[]):
        """Initialize portfolio."""
        self.psize = psize
        self.exposure = exposure
        self.rating = rating
        self.factor = factor

    def loadjson(self, data):
        """Load portfolio data from JSON object."""
        self.psize = len(data)
        for x in data:
            self.exposure.append(float(x['EAD']))
            self.rating.append(float(x['Rating']))
            self.factor.append(x['Factor'])
