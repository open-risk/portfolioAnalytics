# encoding: utf-8

# (c) 2017-2022 Open Risk, all rights reserved
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


"""Example of calculating thresholds."""

import transitionMatrix as tm
from transitionMatrix.creditratings.predefined import Generic

from portfolioAnalytics.thresholds.model import ThresholdSet
from portfolioAnalytics.thresholds.settings import AR_Model
from portfolioAnalytics import dataset_path

# Example 1: Typical Annual Credit Rating Transition Matrix
# Example 2: Monthly Transition Matrix

example = 2

if example == 1:
    # M = tm.TransitionMatrix(values=Minimal)
    M = tm.TransitionMatrix(values=Generic)
    # Lets take a look at the values
    print("> Load and validate a minimal transition matrix")
    M.print()
    M.validate()
    print("> Valid Input Matrix? ", M.validated)

    # The size of the rating scale
    Ratings = M.dimension

    # The Default (absorbing state)
    Default = Ratings - 1

    # Lets extend the matrix into multi periods
    Periods = 10
    T = tm.TransitionMatrixSet(values=M, periods=Periods, method='Power', temporal_type='Cumulative')
    print("> Extend the matrix into 10 periods")
elif example == 2:
    T = tm.TransitionMatrixSet(periods=120, temporal_type='Cumulative', json_file=dataset_path + "generic_monthly.json")
    Ratings = T.entries[0].dimension

# Initialize a threshold set
As = ThresholdSet(TMSet=T)

# Calculate thresholds per initial rating state
print("> Calculate thresholds per initial rating state")
for ri in range(0, Ratings):
    print("Initial Rating: ", ri)
    As.fit(AR_Model, ri, dt=1.0/12.0)
As.to_json(json_file="monthly_thresholds.json")

# Display the calculated thresholds
# print("> Display the calculated thresholds")
# As.print()