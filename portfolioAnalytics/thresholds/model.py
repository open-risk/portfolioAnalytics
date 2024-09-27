# encoding: utf-8

"""This module is part of the portfolioAnalytics package."""

# (c) 2017-2024 Open Risk (https://www.openriskmanagement.com)
#
# portfolioAnalytics is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of portfolioAnalytics. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import transitionMatrix as tm
from matplotlib import collections as mc
from scipy.stats import norm
from transitionMatrix.model import TransitionMatrixSet

from portfolioAnalytics.thresholds import settings
from portfolioAnalytics.thresholds.settings import VERBOSE, GRAPHS

# choose matplotlib backend

matplotlib.use("agg")


# Calculate survival distribution function at period k and point x
# Convolution of last period survival function with process one step transition density
def integrate_g(ff, x, an, dx, dt, mu, phi_1):
    """Integrate G."""
    dt_root = np.sqrt(dt)
    offset = mu + phi_1 * x
    arg = (an - offset) / dt_root
    F = norm.cdf(arg)
    integrant = np.multiply(ff, F)
    integral = np.trapz(integrant, x, dx)
    return integral


# Obtain survival density at point x by integrating over grid
def integrate_f(ff, x, an, dx, dt, mu, phi_1):
    """Integrate F."""
    dt_root = np.sqrt(dt)
    offset = mu + phi_1 * x
    arg = (an - offset) / dt_root
    F = norm.pdf(arg)
    integrant = ff * F
    integral = np.trapz(integrant, x, dx) / dt_root
    return integral


class ThresholdSet(object):
    """The Threshold set object stores a multiperiod migration/default threshold structure as a numpy array.

    .. Todo:: Separate integration method from transition data

    """

    def __init__(self, ratings=None, periods=None, TMSet=None, json_file=None):
        """Create a new threshold set. Different options for initialization are:

        * providing shape values (Ratings, Periods)
        * providing a transition matrix set
        * providing a file URL

        :param ratings: size of the transition matrix
        :param periods: number of periods (equally spaced)
        :param TMSet: a TransitionMatrix Set object (optional)

        :type ratings: int
        :type periods: int
        :type TMSet: object

        :returns: returns a ThresholdSet object
        :rtype: object

        .. note:: The transition matrix set

        :Example:

        Instantiate a threshold set directly using an existing transition matrix set

        A = tm.thresholds.ThresholdSet(TMSet=T)

        """
        if (ratings and periods) is not None:
            self.A = np.zeros((ratings, ratings, periods))
            self.T = tm.TransitionMatrixSet(dimension=ratings, periods=periods, temporal_type='Cumulative')
        elif TMSet is not None:
            self.ratings = TMSet.entries[0].dimension
            self.periods = len(TMSet.periods)

            # Grid and accuracy settings
            self.grid_size = settings.GRID_POINTS
            self.precision = settings.PRECISION
            self.scale = settings.SCALE

            # Thresholds
            self.A = np.zeros(shape=(self.ratings, self.ratings, self.periods), dtype='double')
            # Transition Matrix Set
            self.T = TMSet

            # Process Survival Density per period
            self.f = np.zeros(shape=(self.grid_size, self.periods, self.ratings), dtype='double')
            # Solution Grid
            self.grid = np.zeros(shape=(self.grid_size, self.periods, self.ratings), dtype='double')
            self.grid_step = np.zeros(shape=(self.periods, self.ratings), dtype='double')
            # Set the max grid value using the scale parameter (heuristic rule)
            self.grid_max = np.zeros(shape=(self.periods,), dtype='double')
        elif json_file is not None:
            self.from_json(json_file)
        else:
            raise ValueError

    def fit(self, AR_Model, ri, dt=1.0):
        """ Fit Thresholds given autoregressive model and transition matrix given the initial state ri.

        .. note::

          The threshold corresponding to the starting rating is set by convention to NaN. The threshold corresponding to a defaulted state is set by convention to - Infinity. These values are stored in memory as numpy NaN and Infinity value respectively. They are serialized as strings "nan" and "-inf" respectively.

        """

        self.periods = 2

        # Process parameters
        mu = AR_Model['Mu']
        phi_1 = AR_Model['Phi'][0]
        x_0 = AR_Model['Initial Conditions'][0]

        dt_root = np.sqrt(dt)
        pi = 4.0 * np.arctan(1.0)
        sqrt_two_pi = np.sqrt(2. * pi)

        self.grid_max = mu + self.scale * dt_root * np.sqrt(np.arange(1, self.periods + 1))

        # The Default (absorbing state)
        Default = self.ratings - 1

        if ri == Default:

            # Transition Threshold for defaulted state (ALL PERIODS)
            # Absorbing states don't have meaningful transition thresholds
            # By convention assigned minus infinity

            for rf in range(Default, -1, -1):  # for all final ratings
                for k in range(0, self.periods):
                    if rf == ri:
                        self.A[ri, rf, k] = np.NaN
                    else:
                        self.A[ri, rf, k] = - np.Inf

        else:

            #
            # ========= Transition Thresholds for the First Period ===========
            #

            k = 0

            # Compute transition thresholds from initital rating (ri) to all final ratings (rf)
            # If rf == ri we don't need to compute threshold (case is bracketed by rating change thresholds above and
            # below )
            offset = mu + phi_1 * x_0
            for rf in range(Default, -1, -1):  # for all final ratings
                # compute the cumulative transition probability from initial rating to all ratings
                # from default and up to the final target rating
                cumulative = self.T.entries[k][ri, Default]
                if rf < ri:  # Upgrade case, the final rating is better (smaller number) than the initial
                    # print('Upgrade to', rf)
                    for j in range(rf + 1, Default):
                        cumulative += self.T.entries[k][ri, j]
                elif rf > ri:  # Downgrade case, the final rating is worse (larger number) then the initial
                    # print('Downgrade to', rf)
                    for j in range(rf, Default):
                        # print('Contribution', ri, j, T.entries[0][ri, j])
                        cumulative += self.T.entries[k][ri, j]

                if ri != rf:
                    # print(cumulative)
                    self.A[ri, rf, k] = dt_root * norm.ppf(cumulative) + offset
                else:
                    # NaN value for threshold of initial rating state
                    self.A[ri, rf, k] = np.NaN

            # Integration Grid for the First Period
            # Starts at lower absorbing state level

            self.grid_step[k, ri] = (self.grid_max[k] - self.A[ri, Default, k]) / (self.grid_size - 1)
            arg = np.zeros_like(self.grid[:, k, ri])
            for i in range(0, self.grid_size):
                self.grid[i, k, ri] = self.A[ri, Default, k] + self.grid_step[k, ri] * i
                arg[i] = (self.grid[i, k, ri] - offset) / dt_root

            # Survival Density for the First Period
            self.f[:, k, ri] = norm.pdf(arg) / dt_root

            if VERBOSE:
                print('------------------------------------------------------------------------------')
                print('Transition Rates From Initial Rating State', ri)
                print('------------------------------------------------------------------------------')
                for rf in range(0, self.ratings):
                    print('To ->', end=' ')
                    print('{0:3}'.format(rf), end='')
                    print(' | ', end='')
                    for k in range(0, self.periods):
                        val = self.T.entries[k][ri, rf]
                        print('{:06.5f}'.format(val), end=' ')
                    print('')

                k = 0
                print('------------------------------------------------------------------------------')
                print('Grid Size :', self.grid_size)
                print('Max Grid Point:', self.grid_max[k])
                print('D Grid Point :', self.A[ri, Default, k])
                print('Step :', self.grid_step[k, ri])
                print('X :', self.grid[:4, k, ri])
                print('f :', self.f[:4, k, ri])

            if GRAPHS:
                print("First Period Graph")
                plt.plot(self.grid[:, 0, ri], self.f[:, 0, ri])
                plt.plot([self.A[ri, Default, 0], self.A[ri, Default, 0]], [0, 0.2])
                plt.plot([self.A[ri, Default - 1, 0], self.A[ri, Default - 1, 0]], [0, 0.2])
                plt.show()

            #
            # ========== PERIOD LOOP for subsequent threshold families =========
            #

            for k in range(1, self.periods):

                #
                # CALCULATE FIRST THE DEFAULT THRESHOLD A(ri -> D, k)
                # print("==========", k, "=========")
                rf = Default
                # Transition to default during [k-1, k]
                cumulative = self.T.entries[k][ri, Default] - self.T.entries[k - 1][ri, Default]

                anp1 = 0
                # Initial guess for threshold taken from previous period
                an = self.A[ri, rf, k - 1]
                Tk = cumulative
                counter = 0

                delta = settings.DELTA
                # Iterate until convergence to find new threshold
                while np.abs(delta) > self.precision:
                    counter += 1
                    gn = integrate_g(self.f[:, k - 1, ri], self.grid[:, k - 1, ri], an, self.grid_step[k - 1, ri], dt,
                                     mu, phi_1)
                    fn = integrate_f(self.f[:, k - 1, ri], self.grid[:, k - 1, ri], an, self.grid_step[k - 1, ri], dt,
                                     mu, phi_1)
                    anp1 = an - (gn - Tk) / fn
                    # print(counter, Tk, gn, fn, an, anp1)
                    delta = anp1 - an
                    an = anp1

                # Store Default Threshold for period k
                self.A[ri, rf, k] = anp1
                print("Period : ", k, "Initial: ", ri, "Final: ", rf, "Value: ", anp1)
                # Compute the cumulative transition probability from ri -> rf
                # Conditional on survival till k-1

                # New Grid Step / Grid (depends on grid max and default threshold
                self.grid_step[k, ri] = (self.grid_max[k] - self.A[ri, Default, k]) / self.grid_size
                i = np.arange(0, self.grid_size)
                self.grid[:, k, ri] = self.A[ri, Default, k] + i * self.grid_step[k, ri]

                # Propagate the survival density to the next step by integrating with the transition density
                # Each new grid point on next period is obtained via an integral over previous period grid
                # i iterates over new grid (k)
                # j iterates over old grid (k-1)
                # Survival Density for Period k
                # Interior point contributions starting from the k-1 default threshold
                offset = mu + phi_1 * self.grid[:, k - 1, ri]

                for i in range(0, self.grid_size):
                    F = np.exp(
                        -(self.grid[i, k, ri] - offset) * (self.grid[i, k, ri] - offset) / 2. / dt) \
                        / sqrt_two_pi / dt_root
                    integrant = np.multiply(self.f[:, k - 1, ri], F)
                    self.f[i, k, ri] = np.trapz(integrant, self.grid[:, k - 1, ri], self.grid_step[k - 1, ri])

                if VERBOSE:
                    print('------------------------------------------------------------------------------')
                    print('Period ', k)
                    print('Max Grid Point:', self.grid_max[k])
                    print('D Grid Point :', self.A[ri, Default, k])
                    print('Step :', self.grid_step[k, ri])
                    print('X :', self.grid[:4, k, ri])
                    print('f :', self.f[:4, k, ri])

                # for all final ratings starting from Default - 1 and moving to highest rating (0)
                # Compute migration transition thresholds

                for rf in range(Default - 1, -1, -1):

                    if rf == ri:
                        # Set by convention the same level threshold to NaN
                        self.A[ri, ri, k] = np.NaN
                        # cumulative = 0.0
                        # for j in range(rf + 1, Default):
                        #     cumulative += self.T.entries[k][ri, j]
                    else:
                        cumulative = 0.0
                        # Final Rating Represents Upgrade
                        if rf < ri:
                            for j in range(rf + 1, Default):
                                cumulative += self.T.entries[k][ri, j]
                        # Final Rating Represents Downgrade
                        elif rf > ri:
                            for j in range(rf, Default):
                                cumulative += self.T.entries[k][ri, j]

                        q = self.f[0, k, ri] * self.grid_step[k, ri]
                        c = 0
                        Tk = cumulative
                        # print('RF', rf, Tk, self.T.entries[k][ri, rf])
                        while q < Tk:
                            q += self.f[c, k, ri] * self.grid_step[k, ri]
                            c += 1

                        self.A[ri, rf, k] = self.grid[c, k, ri]

                if VERBOSE:
                    print('------------------------------------------------------------------------------')
                    print('Thresholds For Initial Rating State', ri)
                    print('------------------------------------------------------------------------------')
                    for rf in range(0, self.ratings):
                        print('To ->', end=' ')
                        print('{0:3}'.format(rf), end='')
                        print(' | ', end='')
                        for k in range(0, self.periods):
                            val = self.A[ri, rf, k]
                            if np.isnan(val):
                                print('{:8s}'.format('NaN'), end=' ')
                            elif np.isinf(val):
                                print('{:8s}'.format('Inf'), end=' ')
                            else:
                                print('{:+6.5f}'.format(val), end=' ')
                        print('')

                if GRAPHS:
                    plt.plot(self.grid[:, k, ri], self.f[:, k, ri])
                    plt.plot([self.A[ri, Default, k], self.A[ri, Default, k]], [0, 0.2])
                    plt.plot([self.A[ri, Default - 1, k], self.A[ri, Default - 1, k]], [0, 0.2])
                    plt.title("Density")
                    plt.show()

        return

    def validate(self, AR_Model):
        """Validate calculated Thresholds given autoregressive model

        The comparison is accomplished by producing the implied transition matrix and setting against
        the input set

        .. Todo:: Automate the comparison when a new set is produced

        """

        self.periods = 2

        # Initialize a transition Matrix set container to hold the results
        Q = tm.TransitionMatrixSet(dimension=self.ratings, periods=self.periods, temporal_type='Cumulative')

        # The Default (absorbing state)
        Default = self.ratings - 1

        # AR Process parameters
        mu = AR_Model['Mu']
        phi_1 = AR_Model['Phi'][0]
        x_0 = AR_Model['Initial Conditions'][0]

        # Validate the transition rates for all initial ratings
        for ri in range(0, Default):

            # ========== PERIOD LOOP =========
            for k in range(0, self.periods):

                # rf = Default is separate case

                # survival probability during k
                integral = np.trapz(self.f[:, k, ri], self.grid[:, k, ri], self.grid_step[k, ri])
                Q.entries[k][ri, Default] = 1.0 - integral

                # Testing Transitions to top (rf = 0) rating

                # If starting from a rating below 0
                if ri > 0:
                    p_grid = ma.masked_less(self.grid[:, k, ri], self.A[ri, 0, k])
                    p_f = ma.masked_array(self.f[:, k, ri], p_grid.mask)
                    integral = np.trapz(p_f, p_grid, self.grid_step[k, ri])
                    Q.entries[k][ri, 0] = integral
                # If starting at rating 0
                else:
                    p_grid = ma.masked_less(self.grid[:, k, ri], self.A[0, 1, k])
                    p_f = ma.masked_array(self.f[:, k, ri], p_grid.mask)
                    integral = np.trapz(p_f, p_grid, self.grid_step[k, ri])
                    Q.entries[k][0, 0] = integral

                # Testing other transitions
                for rf in range(1, self.ratings - 1):
                    # Staying in same rating
                    if rf == ri:
                        p_grid = ma.masked_outside(self.grid[:, k, ri], self.A[ri, rf - 1, k], self.A[ri, rf + 1, k])
                    # Upgrade
                    elif rf < ri:
                        p_grid = ma.masked_outside(self.grid[:, k, ri], self.A[ri, rf, k], self.A[ri, rf - 1, k])
                    # Downgrade
                    elif rf > ri:
                        p_grid = ma.masked_outside(self.grid[:, k, ri], self.A[ri, rf, k], self.A[ri, rf + 1, k])

                    p_f = ma.masked_array(self.f[:, k, ri], p_grid.mask)
                    integral = np.trapz(p_f, p_grid, self.grid_step[k, ri])
                    Q.entries[k][ri, rf] = integral

        print('==============================================================================')
        print('                      Transition Matrix Validation Results                    ')
        print('==============================================================================')
        print('Number of Rating States: ', self.ratings)
        print('Number of Periods: ', self.periods)
        print('------------------------------------------------------------------------------')
        print('T is the input matrix, Q is reconstructed matrix, E is the absolute error')
        print('------------------------------------------------------------------------------')
        for ri in range(0, self.ratings):
            print('From Initial Rating State', ri)
            print('------------------------------------------------------------------------------')
            for rf in range(0, self.ratings):
                print('T ', end=' ')
                print('{0:3}'.format(rf), end='')
                print(' | ', end='')
                for k in range(0, self.periods):
                    val = self.T.entries[k][ri, rf]
                    print('{:06.4f}'.format(val), end=' ')
                print('')
                print('Q ', end=' ')
                print('{0:3}'.format(rf), end='')
                print(' | ', end='')
                for k in range(0, self.periods):
                    val = Q.entries[k][ri, rf]
                    print('{:06.4f}'.format(val), end=' ')
                print('')
                print('E ', end=' ')
                print('{0:3}'.format(rf), end='')
                print(' | ', end='')
                for k in range(0, self.periods):
                    val = self.T.entries[k][ri, rf] - Q.entries[k][ri, rf]
                    print('{:06.4f}'.format(val), end=' ')
                print('')
                print('..............................................................................')
        print('==============================================================================')

        return Q

    def to_json(self, json_file=None, accuracy=5):
        """Convert to JSON."""
        hold = []
        for k in range(self.A.shape[2]):
            # Matrix of k-th period
            # Round values to desired accuracy
            # Convert NaN and Infinity to values (JSON Requirement)
            entry = np.around(self.A[:, :, k], accuracy)
            strict_json = np.nan_to_num(entry)
            hold.append(strict_json.tolist())
        serialized = json.dumps(hold, indent=2, separators=(',', ': '))
        if json_file is not None:
            json_file = open(json_file, 'w')
            json_file.write(serialized)
            json_file.close()
        return serialized

    def from_json(self, json_file):
        """Read from JSON."""
        values = json.load(open(json_file))
        # Infer number of periods
        self.periods = len(values)
        # Infer number of rating states
        entry = values[0]
        self.ratings = len(entry)

        # Initialize thresholds
        A = np.zeros(shape=(self.ratings, self.ratings, self.periods), dtype='double')
        for k in range(0, self.periods):
            entry = values[k]
            A[:, :, k] = np.array(entry, dtype=np.float64)
        self.A = A

    def print(self, format_type='Standard', accuracy=2):
        """Pretty print a threshold matrix set

        :param format_type: formating options (Standard, Percent)
        :type format_type: str
        :param accuracy: number of decimals to display
        :type accuracy: int

        """

        for k in range(self.A.shape[2]):
            entry = np.around(self.A[:, :, k], accuracy)
            for s_in in range(entry.shape[0]):
                for s_out in range(entry.shape[1]):
                    if format_type == 'Standard':
                        format_string = "{0:." + str(accuracy) + "f}"
                        print(format_string.format(entry[s_in, s_out]) + ' ', end='')
                    elif format_type == 'Percent':
                        print("{0:.2f}%".format(100 * entry[s_in, s_out]) + ' ', end='')
                print('')
            print('')

    def plot(self, rating):
        """Plot."""
        lines = []
        ri = rating
        for rf in range(0, self.ratings):
            for k in range(0, self.periods):
                if rf != ri:
                    value = self.A[ri, rf, k]
                    line = [(k, value), (k + 1.0, value)]
                    lines.append(line)

        lc = mc.LineCollection(lines, linewidths=2)
        fig, ax = plt.subplots()
        ax.add_collection(lc)
        ax.autoscale()
        ax.margins(0.1)
        ax.set_xlabel("Periods")
        ax.set_ylabel("Normalized Z Level")
        plt.title("Transition Thresholds from Initial " + str(ri) + " State")
        plt.show()


class ConditionalTransitionMatrix(TransitionMatrixSet):
    """The _`ConditionalTransitionMatrix` object stores a family of TransitionMatrix objects as a time ordered list.

    Its main functionality is to allow conditioning (stressing) the values in accordance with a predefined model

    """

    def __init__(self, thresholds=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.A = thresholds.A
        self.dimension = thresholds.A[:, :, 0].shape[0]
        self.entries = []
        self.temporal_type = 'Cumulative'
        self.periods = thresholds.A.shape[2]
        self.dimension = thresholds.A.shape[0]
        self.T = np.zeros(shape=(self.dimension, self.dimension, self.periods), dtype=np.float)

    # Override the print method
    def print_matrix(self, format_type='Standard', accuracy=2, state=None):
        """Pretty print a threshold matrix set

        :param format_type: formating options (Standard, Percent)
        :type format_type: str
        :param accuracy: number of decimals to display
        :type accuracy: int

        """

        print("State ", state)
        if state is None:
            for k in range(self.T.shape[2]):
                entry = np.around(self.T[:, :, k], accuracy)
                for s_in in range(entry.shape[0]):
                    for s_out in range(entry.shape[1]):
                        if format_type == 'Standard':
                            format_string = "{0:." + str(accuracy) + "f}"
                            print(format_string.format(entry[s_in, s_out]) + ' ', end='')
                        elif format_type == 'Percent':
                            print("{0:.2f}%".format(100 * entry[s_in, s_out]) + ' ', end='')
                    print('')
                print('')
        else:
            for k in range(self.T.shape[2]):
                entry = np.around(self.T[:, :, k], accuracy)
                # print(entry)
                for s_out in range(entry.shape[1]):
                    if format_type == 'Standard':
                        format_string = "{0:." + str(accuracy) + "f}"
                        print(format_string.format(entry[state, s_out]) + ' ', end='')
                    elif format_type == 'Percent':
                        print("{0:.2f}%".format(100 * entry[state, s_out]) + ' ', end='')
                print('')

    def fit(self, AR_Model, Scenario, rho, ri):
        """Calculate conditional transition rates given thresholds and stochastic model


        """

        # Grid and accuracy settings
        self.grid_size = settings.GRID_POINTS
        self.precision = settings.PRECISION
        self.scale = settings.SCALE

        # Process parameters
        mu = AR_Model['Mu']
        phi_1 = AR_Model['Phi'][0]
        x_0 = AR_Model['Initial Conditions'][0]

        # Temporal scale
        # TODO(validate arbitrary timestep)
        # dt = 1.0
        dt2 = 1.0 - rho * rho
        dt_root = np.sqrt(dt2)
        pi = 4.0 * np.arctan(1.0)
        sqrt_two_pi = np.sqrt(2. * pi)

        self.grid_max = mu + self.scale * dt_root * np.sqrt(np.arange(1, self.periods + 1))
        # Process Survival Density per period
        self.f = np.zeros(shape=(self.grid_size, self.periods, self.dimension), dtype='double')
        # Solution Grid
        self.grid = np.zeros(shape=(self.grid_size, self.periods, self.dimension), dtype='double')
        self.grid_step = np.zeros(shape=(self.periods, self.dimension), dtype='double')

        # The Default (absorbing state)
        Default = self.dimension - 1

        if ri == Default:
            # Absorbing states don't have different stressed transitions
            for rf in range(Default, -1, -1):  # for all final ratings
                for k in range(0, self.periods):
                    # Likelihood of remaining in default
                    if rf == ri:
                        self.T[ri, rf, k] = 1.0
                    # Likelihood of moving away from default
                    else:
                        self.T[ri, rf, k] = 0.0

        else:

            # ========== PERIOD LOOP =========
            for k in range(0, self.periods):

                # New Grid Step / Grid (depends on grid max and default threshold
                self.grid_step[k, ri] = (self.grid_max[k] - self.A[ri, Default, k]) / (self.grid_size - 1)
                offset = mu + phi_1 * x_0 + rho * Scenario[k]

                # Compute the cumulative transition probability from ri -> rf
                # Conditional on survival till k-1

                if k == 0:
                    # Integration Grid for the First Period
                    # Starts at lower absorbing state level

                    arg = np.zeros_like(self.grid[:, k, ri])
                    for i in range(0, self.grid_size):
                        self.grid[i, k, ri] = self.A[ri, Default, k] + self.grid_step[k, ri] * i
                        arg[i] = (self.grid[i, k, ri] - offset) / dt_root

                    # Survival Density for the First Period
                    self.f[:, k, ri] = norm.pdf(arg) / dt_root

                else:

                    i = np.arange(0, self.grid_size)
                    self.grid[:, k, ri] = self.A[ri, Default, k] + i * self.grid_step[k, ri]

                    # Propagate the survival density to the next step by integrating with the transition density
                    # Each new grid point on next period is obtained via an integral over previous period grid
                    # i iterates over new grid (k)
                    # j iterates over old grid (k-1)
                    # Survival Density for Period k
                    # Interior point contributions starting from the k-1 default threshold
                    offset = mu + phi_1 * self.grid[:, k - 1, ri] + rho * Scenario[k]

                    for i in range(0, self.grid_size):
                        F = np.exp(
                            -(self.grid[i, k, ri] - offset) * (
                                    self.grid[i, k, ri] - offset) / 2. / dt_root) / sqrt_two_pi / dt_root
                        integrant = np.multiply(self.f[:, k - 1, ri], F)
                        self.f[i, k, ri] = np.trapz(integrant, self.grid[:, k - 1, ri], self.grid_step[k - 1, ri])

                # rf = Default is separate case
                rf = Default
                # stressed survival (non-default) probability during k
                integral = np.trapz(self.f[:, k, ri], self.grid[:, k, ri], self.grid_step[k, ri])
                self.T[ri, rf, k] = 1.0 - integral

                for rf in range(Default - 1, -1, -1):
                    # Stressed transitions to top (rf = 0) rating
                    # If starting from a rating below 0
                    if ri > 0:
                        p_grid = ma.masked_less(self.grid[:, k, ri], self.A[ri, 0, k])
                        p_f = ma.masked_array(self.f[:, k, ri], p_grid.mask)
                        integral = np.trapz(p_f, p_grid, self.grid_step[k, ri])
                        self.T[ri, 0, k] = integral
                    # If starting at rating 0
                    else:
                        p_grid = ma.masked_less(self.grid[:, k, ri], self.A[0, 1, k])
                        p_f = ma.masked_array(self.f[:, k, ri], p_grid.mask)
                        integral = np.trapz(p_f, p_grid, self.grid_step[k, ri])
                        self.T[0, 0, k] = integral

                    # Stressed probabilities for other transitions
                    for rf in range(1, self.dimension - 1):
                        # Staying in same rating
                        if rf == ri:
                            p_grid = ma.masked_outside(self.grid[:, k, ri], self.A[ri, rf - 1, k],
                                                       self.A[ri, rf + 1, k])
                        # Upgrade
                        elif rf < ri:
                            p_grid = ma.masked_outside(self.grid[:, k, ri], self.A[ri, rf, k], self.A[ri, rf - 1, k])
                        # Downgrade
                        elif rf > ri:
                            p_grid = ma.masked_outside(self.grid[:, k, ri], self.A[ri, rf, k], self.A[ri, rf + 1, k])

                        p_f = ma.masked_array(self.f[:, k, ri], p_grid.mask)
                        integral = np.trapz(p_f, p_grid, self.grid_step[k, ri])
                        self.T[ri, rf, k] = integral

    def plot_densities(self, period=None, state=0):
        """Plot densities."""
        if period is not None:
            k = period
            ri = state
            Default = self.dimension - 1
            plt.plot(self.grid[:, k, ri], self.f[:, k, ri])
            for rf in range(0, Default):
                plt.plot([self.A[ri, rf, k], self.A[ri, rf, k]], [0, 1])
            plt.title("Density")
            plt.show()
        else:
            plt.style.use(['ggplot'])
            m = self.periods
            ri = state
            Default = self.dimension - 1
            f, axarr = plt.subplots(m, 1, sharex=True)
            # f, axarr = plt.subplots(m, 1)

            y_max = 1.2 * np.max(self.f)
            for k in range(m):
                axarr[k].set_xlim([-3, 6])
                axarr[k].set_ylim([0, y_max])
                axarr[k].plot(self.grid[:, k, ri], self.f[:, k, ri])
                for rf in range(0, Default):
                    axarr[k].plot([self.A[ri, rf, k], self.A[ri, rf, k]], [0, y_max])
                axarr[k].set_title('Period: ' + str(k + 1), fontsize=10)

            plt.show()
