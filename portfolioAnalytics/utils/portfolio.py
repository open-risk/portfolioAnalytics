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

""" This module provides simple functionality for holding portfolio data for calculation purposes.

* Portfolio_ implements a simple portfolio data container

"""


import numpy as np


class Portfolio(object):
    """ The _`Portfolio` object implements a simple portfolio data structure. See `loan tape <https://www.openriskmanual.org/wiki/Loan_Tape>`_ for more general structures.

    """

    def __init__(self, psize=0, rating=[], exposure=[], factor=[]):
        """Initialize portfolio.

        :param psize: initialization values
        :param rating: list of default probabilities
        :param exposure: list of exposures (numerical values, e.g. `Exposure At Default <https://www.openriskmanual.org/wiki/Exposure_At_Default>`_
        :param factor: list of factor indices (those should match the factors used e.g. in a correlation matrix
        :type psize: int
        :type rating: list of floats
        :type exposure: list of floats
        :type factor: list of int
        :returns: returns a Portfolio object
        :rtype: object

        .. note:: The initialization in itself does not validate if the provided values form indeed valid portfolio data

        """
        self.psize = psize
        self.exposure = exposure
        self.rating = rating
        self.factor = factor

    def loadjson(self, data):
        """Load portfolio data from JSON object.

        The data format for the input json object is a list of dictionaries as follows
        [{"ID":"1","PD":"0.015","EAD":"40","FACTOR":0},
          ...
         {"ID":"2","PD":"0.286","EAD":"20","FACTOR":0}]

        """
        self.psize = len(data)
        for x in data:
            self.exposure.append(float(x['EAD']))
            self.rating.append(float(x['PD']))
            self.factor.append(x['FACTOR'])

    def preprocess_portfolio(self):
        """
        Produce some portfolio statistics like total number of entities and exposure weighted average probability of default
        :return:
        """
        N = self.psize
        Total_Exposure = np.sum(self.exposure)
        p = np.inner(self.rating, self.exposure) / Total_Exposure
        return N, p
