Examples
========

The examples directory includes python scripts and jupyter notebooks to help you get started

- Generating loss distributions analytically
- Estimating thresholds given a multi-period transition matrix set


Python Scripts
-------------------------------------------

Located in examples/python (For testing purposes all examples can be run using the run_examples.py script
located in the root directory)


Portfolio Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* portolio_model.py

Using the portfolio model library to calculate default probabilities in finite
portfolio with N credits


Rating Transition Thresholds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* calculate_thresholds.py
* validated_thresholds.py
* visualize_thresholds.py

Example of using portfolioAnalytics to compute multi-period transition thresholds
compatible with a given transition matrix. Validate computed thresholds.

The mathematical framework documented in
`Multi-Period Transition Thresholds <https://www.openriskmanual.org/wiki/Multi-Period_Transition_Thresholds>`_

.. image:: ../../examples/Thresholds.png



Jupyter Notebooks
-------------------------------------------

* Adjust_NotRated_State.ipynb
* Matrix_Operations.ipynb
* Portfolio_Examples.ipynb
