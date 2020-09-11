.. _changes:

AIDApy 0.1.2 (2020-06-24)
===========================

This is the first release of *aidapy*.


Features
----------

- ``aidapy.data.mission``: wrap *heliopy* to provide data from
  3 different missions (OMNI, cluster, and MMS) in *xarray* format
  with high-level products.
- ``aidapy.aidaxr``: provides extensions to `xarray.DataSet` and
  `xarrayDataArray`.
  Statistical methods are computed on the xarray data. Visualization and
  computations are provided for velocity distribution functions.
  Specific methods for observations are also added,
  such as curlometer or plasma beta. Extreme events methods are also provided.
- ``aidapy.ml``: basic classes providing multi layer perceptrons
  and GMM for particle
  distribution analysis.
- ``aidapy.tools``: various scripts to support velocity distribution plots
  and MMS analysis.
- ``aidapy.aidafunc``: high-levels methods helping the users to retrieve
  observational data, to perform search of specific events, and
  to set specific configuration for heliopy and ESA cookie.

Enhancements
--------------

- Creation of the CHANGELOG, LICENSE, MANIFEST, README, STYLEGUIDE,
  requirements.txt.
- Add setup.py with full information and a installation guide
- *heliopy_multid* is now a dependency


Documentation
----------------------

- Creation of the documentation generated with sphinx.
- Upload on readthedocs.
- Link with the jupyter notebooks.

Bug fixes
----------
