# encoding: utf-8

# (c) 2014-2019 Open Risk (https://www.openriskmanagement.com)
#
# TransitionMatrix is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of TransitionMatrix. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.


from scipy import stats

import json
from portfolioAnalytics.utils import bivariatenormal as bv


# wrapper for inverse cumulative normal density
def Ninv(x):
    return stats.norm.ppf(x, loc=0.0, scale=1.0)


class Portfolio:
    def __init__(self, psize=0, pd=[], exposure=[], loading=[], atype=[]):
        self.psize = psize        
        self.pd = pd
        self.exposure = exposure
        self.loading = loading
        self.atype = atype
    def loadjson(self, data):
        self.psize = len(data)
        for x in data:
            self.pd.append(float(x['pd']))
            self.exposure.append(float(x['exposure']))
            self.loading.append(x['sector'])
            self.atype.append(int(x['exposureid']))            
# calculate portfolio loss variance


def variance(P):

    n = P.psize
    variance = 0.0
    name_var = 0.0
    
    for i in range(n): 
        for j in range(i): 
            p1 = P.pd[i]
            p2 = P.pd[j]
            a1 = Ninv(p1)
            a2 = Ninv(p2)           
            rho = 0.2
            variance_pair = P.exposure[i] * P.exposure[j] * (bv.BivariateNormalDistribution(a1, a2, rho) - p1 * p2)
            variance += variance_pair

    for i in range(n - 1): 
        p1 = P.pd[i]
        name_var += P.exposure[i] * P.exposure[i] * (p1 - p1 * p1)

    return 2 * variance + name_var

