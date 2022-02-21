# encoding: utf-8

# (c) 2017-2022 Open Risk (https://www.openriskmanagement.com), all rights reserved
#
# PortfolioAnalytics is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of PortfolioAnalytics. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.


import json

from correlationMatrix import CorrelationMatrix

from portfolioAnalytics import dataset_path
from portfolioAnalytics.creditmetrics import variance
from portfolioAnalytics.utils.portfolio import Portfolio

json_data = open(dataset_path + '/portfolio_data1.json').read()
data = json.loads(json_data)
print(data)

P = Portfolio()
P.loadjson(data)

Omega = CorrelationMatrix(values=[[1, 0.2, 0.2], [0.2, 1.0, 0.2], [0.2, 0.2, 1.0]])
loadings = [0.3, 0.3, 0.3]
print(variance(P, Omega.matrix, loadings))
