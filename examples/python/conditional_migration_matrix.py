# encoding: utf-8

# (c) 2017-2023 Open Risk, all rights reserved (https://www.openriskmanagement.com)
#
# portfolioAnalytics is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of TransitionMatrix. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for+ the specific language governing permissions and
# limitations under the License.


""" Derive a conditional migration matrix given a stress scenario

For this example we assume we already have a
multi-period set of transition matrices and have already modelled transition thresholds for
a given AR process

"""
import numpy as np

from portfolioAnalytics import source_path
from portfolioAnalytics.thresholds.model import ThresholdSet, ConditionalTransitionMatrix
from portfolioAnalytics.thresholds.settings import AR_Model

dataset_path = source_path + "datasets/"

# A Generic matrix with 7 non-absorbing and one absorbing state

Generic = [
    [0.92039, 0.0709, 0.0063, 0.0015, 0.0006, 0.0002, 0.0001, 1e-05],
    [0.0062, 0.9084, 0.0776, 0.0059, 0.0006, 0.001, 0.0002, 0.0001],
    [0.0005, 0.0209, 0.9138, 0.0579, 0.0044, 0.0016, 0.0004, 0.0005],
    [0.0004, 0.0021, 0.041, 0.8936, 0.0482, 0.0086, 0.0024, 0.0037],
    [0.0003, 0.0008, 0.014, 0.0553, 0.8225, 0.0815, 0.0111, 0.0145],
    [0.0001, 0.0004, 0.0057, 0.0134, 0.0539, 0.8114, 0.0492, 0.0659],
    [1e-05, 0.0002, 0.0029, 0.0058, 0.0155, 0.1054, 0.52879, 0.3414],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]]

# Initialize a threshold set from file
As = ThresholdSet(json_file=dataset_path + 'generic_thresholds.json')

# Inspect values (we assume these inputs have already been validated after generation!)
# As.print(accuracy=4)

# Specify the initial rating of interest
ri = 3

# As.plot(ri)

# Initialize a conditional migration matrix with the given thresholds

Q = ConditionalTransitionMatrix(thresholds=As)

# # Q.print()
#
# print(dir(Q))
#
# Specify the stress factor for all periods (in this example five)
Scenario = np.zeros((Q.periods), dtype=float)

Scenario[0] = 2.0
Scenario[1] = 2.0
Scenario[2] = - 2.0
Scenario[3] = - 2.0
Scenario[4] = 0.0

# Specify sensitivity to stress
rho = 0.5

# Calculate conditional transition rates for an initial state (5)
Q.fit(AR_Model, Scenario, rho, ri)
# Print the conditional transition rates for that rating
Q.print_matrix(format_type='Standard', accuracy=4, state=ri)
# Graph the modelled survival densities versus migration thresholds
Q.plot_densities(state=ri)
# Q.plot_densities(1, ri)
