portfolioAnalytics
=========================

portfolioAnalytics is a Python powered library for the calculation of semi-analytic approximations to portfolio credit models

* Author: `Open Risk <http://www.openriskmanagement.com>`_
* License: Apache 2.0
* Code Documentation: `Read The Docs <https://portfolioAnalytics.readthedocs.io/en/latest/>`_
* Mathematical Documentation: `Open Risk Manual <https://www.openriskmanual.org/wiki/Transition_Matrix>`_
* Training: `Open Risk Academy <https://www.openriskacademy.com/login/index.php>`_
* Development Website: `Github <https://github.com/open-risk/portfolioAnalytics>`_


Functionality
-------------

You can use portfolioAnalytics to create semi-analytic loss distributions for a variety of stylized credit portfolios. The library provides semi-analytical functions useful for testing the accuracy of credit portfolio simulation models. The basic formulas are reasonably simple and well known: They underpin the calculation of RWA (risk weighted assets), and in turn required capital, thus ensuring stability for the entire banking systems worldwide. You can also use the library to estimate transition thresholds for stochastic processes


**NB: portfolioAnalytics is still in active development. If you encounter issues please raise them in our github repository**


Vasicek Portfolio Models Library
----------------------------------------------

Dependencies: scipy, sympy

Portfolio Model Examples
-------------------------

Check the jupyter notebooks and python scripts

Current Functions
-----------------

* vasicek_base
* vasicek_base_el
* vasicek_base_ul
* vasicek_lim
* vasicek_lim_el
* vasicek_lim_ul
* vasicek_lim_q

The Vasicek Base family produces finite pool loss probabilities and measures (EL, UL)

The Vasicek Lim family produces asymptotic pool loss probabilities and measures (EL, UL, Quantile)

Limitations
-------------
The portfolioAnalytics library provides a range of powerful modelling functionalities that are are of relevance in real credit portfolio management activities. Yet achieving the tractability and usability of a semi-analytic calculation suite is not without some tradeoffs. Several simplifications are made (extensively documented in the Mathematical Documentation). Those simplifications imply that when using the portfolioAnalytics models to assess the risk in actual portfolios it is important to assess


Installation
=======================

You can install and use the portfolioAnalytics package in any system that supports the `Scipy ecosystem of tools <https://scipy.org/install.html>`_

Dependencies
-----------------

- portfolioAnalytics requires Python 3
- the thresholds module depends on the Open Risk transitionMatrix and correlationMatrix libraries
- It depends on numerical and data processing Python libraries (Numpy, Scipy, Pandas)
- The Visualization API depends on Matplotlib
- The precise dependencies are listed in the requirements.txt file.
- portfolioAnalytics may work with earlier versions of these packages but this has not been tested


From PyPi
-------------

.. code:: bash

    pip3 install pandas
    pip3 install matplotlib
    pip3 install portfolioAnalytics

From sources
-------------

Download the sources to your preferred directory:

.. code:: bash

    git clone https://github.com/open-risk/portfolioAnalytics


Using virtualenv
----------------

It is advisable to install the package in a virtualenv so as not to interfere with your system's python distribution

.. code:: bash

    virtualenv -p python3 tm_test
    source tm_test/bin/activate

If you do not have pandas already installed make sure you install it first (will also install numpy)

.. code:: bash

    pip3 install pandas
    pip3 install matplotlib
    pip3 install -r requirements.txt

Finally issue the install command and you are ready to go!

.. code:: bash

    python3 setup.py install

File structure
-----------------
The distribution has the following structure:

| portfolioAnalytics         The library source code
|    estimators            Estimator methods (TODO)
|    utils                 Helper classes and methods
|    thresholds            Algorithms for calibrating AR(n) process thresholds to input transition rates
|    vasicek               Collection of portfolio analytic solutions
|    creditmetrics         Analytic calculation of variance for credit metrics style models
| examples                 Usage examples
| datasets                 Contains a variety of datasets useful for getting started with portfolioAnalytics
| tests                    Testing suite

Testing Framework
----------------------

It is a good idea to run the test-suite. Before you get started:

- Adjust the source directory path in portfolioAnalytics/__init__ and then issue the following in at the root of the distribution
- Unzip the data files in the datasets directory

.. code:: bash

    python3 test.py

Getting Started
=======================

Check the Examples pages in this documentation

Look at the examples directory for a variety of typical workflows.

For more in depth study, the Open Risk Academy has courses elaborating on the use of the library

- Analysis of `Credit Migration using Python portfolioAnalytics: <https://www.openriskacademy.com/course/view.php?id=38>`_

