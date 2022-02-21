# -*- coding: utf-8 -*-

# (c) 2017-2022 Open Risk, all rights reserved (https://www.openriskmanagement.com)
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

from portfolioAnalytics.vasicek import vasicek_base

""" Using the portfolio model library to calculate default probabilities in finite 
portfolio with N credits - Calculate probability of k losses

"""

# Calculate the probability of four losses in a portfolio of ten credits when the PD is 0.1 and correlation is 20%

print("p=", vasicek_base(10, 0, 0.34140, 0.2))
