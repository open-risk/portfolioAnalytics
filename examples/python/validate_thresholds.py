# encoding: utf-8

# (c) 2014-2019 Open Risk, all rights reserved
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


""" Validate a set of calculated thresholds

The intermediate objects required for validation (grids and densities)
are not stored. They have to be recomputed for validation purposes

"""

import transitionMatrix as tm
from transitionMatrix.predefined import Generic
from portfolioAnalytics.thresholds.model import ThresholdSet
from portfolioAnalytics.thresholds.settings import AR_Model
from portfolioAnalytics import source_path
dataset_path = source_path + "datasets/"

# Example 1: Typical Annual Credit Rating Transition Matrix
# Example 2: Monthly Transition Matrix

example = 2


if example == 1:
    M = tm.TransitionMatrix(values=Generic)
    # Lets take a look at the values
    M.print()
    M.validate()

    # The size of the rating scale
    Ratings = M .dimension

    # The Default (absorbing state)
    Default = Ratings - 1

    # Lets extend the matrix into multi periods
    Periods = 5
    T = tm.TransitionMatrixSet(values=M, periods=Periods, method='Power', temporal_type='Cumulative')

    # Initialize a threshold set
    As = ThresholdSet(TMSet=T)

    print("> Fit Multiperiod Thresholds")
    for ri in range(0, Ratings):
        print("RI: ", ri)
        As.fit(AR_Model, ri)

    print("> Validate Multiperiod Thresholds against Input Transition Matrix Set")
    Q = As.validate(AR_Model)

    print("> Save Multiperiod Thresholds in JSON Format")
    As.to_json('generic_thresholds.json')

elif example == 2:
    TS = tm.TransitionMatrixSet(json_file=dataset_path + 'generic_monthly.json')
    As = ThresholdSet(TMSet=TS)
    for ri in range(0, TS.entries[0].dimension):
        print("RI: ", ri)
        As.fit(AR_Model, ri)

    print("> Validate Multiperiod Thresholds against Input Transition Matrix Set")
    Q = As.validate(AR_Model)
