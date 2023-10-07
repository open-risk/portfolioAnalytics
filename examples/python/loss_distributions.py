# encoding: utf-8

# (c) 2017-2023 Open Risk (https://www.openriskmanagement.com), all rights reserved
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

from portfolioAnalytics import dataset_path
from portfolioAnalytics.model import LossDistribution
from portfolioAnalytics.utils.portfolio import Portfolio

# Load the portfolio data
print(dataset_path)
json_data = open(dataset_path + '/portfolio_data1.json').read()
data = json.loads(json_data)

# Create a portfolio
P = Portfolio()
P.loadjson(data)

# Create a finite Vasicek model loss distribution

V = LossDistribution()
V.calculate(method='Finite_Vasicek', asset_correlation=0.4, portfolio=P)
V.print_moments()
