.. -*- mode: rst -*-

.. |LicenseMIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
.. _LicenseMIT: https://opensource.org/licenses/MIT

.. |LicenseCC| image:: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
.. _LicenseCC: https://creativecommons.org/licenses/by/4.0/

.. |Pipeline| image:: https://gitlab.com/aidaspace/aidapy/badges/master/pipeline.svg
.. _Pipeline: https://gitlab.com/aidaspace/aidapy/commits/master

.. |CoverageReport| image:: https://codecov.io/gl/aidaspace/aidapy/branch/master/graph/badge.svg
.. _CoverageReport: https://codecov.io/gl/aidaspace/aidapy

.. |PylintScore| image:: https://aidaspace.gitlab.io/aidapy/pylint.svg
.. _PylintScore: https://gitlab.com/aidaspace/aidapy/commits/master

.. |Maintenance| image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
.. _Maintenance: https://gitlab.com/aidaspace/aidapy/commits/master

.. |DocSphinx| image:: https://img.shields.io/static/v1.svg?label=sphinx&message=documentation&color=blue
.. _DocSphinx: https://gitlab.com/aidaspace/aidapy/commits/master

.. |PyPi| image:: https://img.shields.io/badge/install_with-pypi-brightgreen.svg
.. _PyPi: https://pypi.org/project/aidapy/


AIDApy
=======


|LicenseMit|_ |LicenseCC|_ |Pipeline|_ |PyPi|_ |CoverageReport|_ |PylintScore|_ |DocSphinx|_ |Maintenance|_

The Python package ``aidapy`` centralizes and simplifies access to:

- Spacecraft data from heliospheric missions
- Space physics simulations
- Advanced statistical tools
- Machine Learning, Deep Learning algorithms, and applications

The ``aidapy`` package is part of the project AIDA (Artificial Intelligence Data Analysis) in Heliophysics funded from
the European  Unions  Horizon  2020  research  and  innovation  programme under grant agreement No 776262.
It is distributed under the open-source MIT license.

Full documentation can be found `here <https://aidapy.readthedocs.io>`_


.. end-marker-intro-do-not-remove


.. start-marker-install-do-not-remove

Installation
------------

The package aidapy has been tested only for Linux.


Using PyPi
^^^^^^^^^^^^^^^

``aidapy`` is available for pip.

.. code-block:: bash

        pip install aidapy


From sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sources are located on **GitLab**:

    https://gitlab.com/aidaspace/aidapy

1) Clone the GitLab repo:

Open a terminal and write the below command to clone in your PC the
AIDApy repo:

.. code-block:: bash

    git clone https://gitlab.com/aidaspace/aidapy.git
    cd aidapy


2) Create a virtual env

AIDApy needs a significant number of dependencies. The easiest
way to get everything installed is to use a virtual environment.

-  Anaconda

You can create a virtual environment and install all the dependencies using conda_
with the following commands:

.. code-block:: bash

    pip install conda
    conda create -n aidapy
    source activate aidapy

.. _conda: http://conda.io/


- Virtual Env

Virtualenv_ can also be used:

.. code-block:: bash

    pip install virtualenv
    virtualenv AIDApy
    source AIDApy/bin/activate

.. _virtualenv: https://virtualenv.pypa.io/en/latest/#


3) Install the version you want via the commands:

For the "basic" version:

.. code-block:: bash

        python setup.py install


For the version with the ML use cases:

.. code-block:: bash

        pip install aidapy[ml]


4) Test the installation in your PC by running. (**Install both versions before running the tests**)

.. code-block:: bash

        python setup.py test

5) (Optional) Generate the docs: install the extra dependencies of doc and run
the `setup.py` file:

.. code-block:: bash

        pip install aidapy[doc]
        python setup.py build_sphinx

Once installed, the doc can be generated with:

.. code-block:: bash

        cd doc
        make html


Dependencies
^^^^^^^^^^^^^

The required dependencies are:

- `Python <https://python.org>`_  >= 3.6
- `scikit-learn <https://scikit-learn.org>`_ >= 0.21
- `numpy <https://www.numpy.org>`_ >= 1.18
- `scipy <https://scipy.org>`_ >= 1.4.1
- `matplotlib <https://matplotlib.org>`_ >= 3.2.1
- `pandas <https://pandas.pydata.org/>`_ >= 1.0.3
- `heliopy <https://github.com/heliopython/heliopy>`_ >= 0.12
- `sunpy <https://docs.sunpy.org/en/stable/>`_ >= 1.1.2
- `astropy <https://www.astropy.org/>`_ >=4.0.1
- `xarray <https://xarray.pydata.org/en/stable/>`_ >=0.15
- `bottleneck <https://pypi.org/project/Bottleneck/>`_ >= 1.3.2
- `heliopy-multid <https://pypi.org/project/heliopy-multid/>`_ >= 0.0.2

Optional dependencies are:

- `pytorch <https://pytorch.org/>`_ >= 1.4
- `skorch <https://github.com/skorch-dev/skorch>`_ >= 0.8.0

Testing dependencies are:

- `pytest <https://docs.pytest.org/en/latest/>`_ >= 2.8

Extra testing dependencies:

- `coverage <https://coverage.readthedocs.io>`_ >= 4.4
- `pylint <https://www.pylint.org>`_ >= 1.6.0


.. end-marker-install-do-not-remove



Usage
--------

AIDApy's high level interface has been created in order to combine
simplicity with workability. In the example below, the end user
downloads data from the MMS space mission for a specific time range and
afterwards extracts the *mean* of these. Finally the timeseries are
ploted in the screen.

.. code:: python

    from datetime import datetime
    #AIDApy Modules
    from aidapy import load_data

    ###############################################################################
    # Define data parameters
    ###############################################################################
    # Time Interval
    start_time = datetime(2018, 4, 8, 0, 0, 0)
    end_time = datetime(2018, 4, 8, 0, 1, 0)

    # Dictionary of data settings: mission, product, probe, coordinates
    # Currently available products: 'dc_mag', 'i_dens', and 'all'
    settings = {'prod': ['dc_mag'], 'probes': ['1', '2'], 'coords': 'gse'}

    ###############################################################################
    # Download and load desired data as aidapy timeseries
    ###############################################################################
    xr_mms = load_data(mission='mms', start_time=start_time, end_time=end_time, **settings)

    ###############################################################################
    # Extract a Statistical Measurement of the data
    ###############################################################################
    xr_mms['dc_mag1'].statistics.mean()

    ###############################################################################
    # Plot the loaded aidapy timeseries
    ###############################################################################
    xr_mms['dc_mag1'].graphical.peek()

Contributing
------------

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

All the code must follow the instructions of STYLEGUIDE.rst. Please make sure to update tests as
appropriate.

Licenses
--------

This software (AIDApy) and the database of the AIDA project (AIDAdb) are
distributed under the `MIT <https://www.gnu.org/licenses/gpl-3.0>`__
license.

The data collections included in the AIDAdb are distributed under the
Creative Commons `CC BT
4.0 <https://creativecommons.org/licenses/by/4.0/>`__ license.



.. |license-mit| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
.. |license-cc| image:: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
   :target: https://creativecommons.org/licenses/by/4.0/
.. |pipeline-status| image:: https://gitlab.com/aidaspace/aidapy/badges/master/pipeline.svg
   :target: https://gitlab.com/aidaspace/aidapy/commits/master
.. |coverage-report| image:: https://codecov.io/gl/aidaspace/aidapy/branch/master/graph/badge.svg
   :target: https://codecov.io/gl/aidaspace/aidapy
.. |pylint-score| image:: https://aidaspace.gitlab.io/aidapy/pylint.svg
   :target: https://gitlab.com/aidaspace/aidapy/commits/master
.. |maintenance-yes| image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
   :target: https://gitlab.com/aidaspace/aidapy/commits/master
.. |doc-sphinx| image:: https://img.shields.io/static/v1.svg?label=sphinx&message=documentation&color=blue
   :target: https://gitlab.com/aidaspace/aidapy/commits/master
.. |pypi| image:: https://img.shields.io/badge/install_with-pypi-brightgreen.svg
   :target: https://pypi.org/project/aidapy/

