Mission
=========

Introduction
-------------
The Mission subpackage is based on routines mainly
adopted from HelioPy (https://heliopy.readthedocs.io/en/stable/) and  SunPy packages (https://docs.sunpy.org/en/stable/) and further developed.
It allows to select and download data from in situ,
remote and ground open-access databases. In its present version,
the subpackage allows to download data from NASA OMNI, ESA Cluster
and NASA MMS in situ data. The tool includes the capability to verify
the version of the data to download, in order to always have the latest
version of the files. The main output of the subpackage are xarray
to be further used by other subpackages of the AIDApy package.


The main features of the Mission subpackage are:

-  being able to handle various missions, such as the Cluster mission
   or the Magnetospheric Multiscale Mission. Additional missions could
   be added according to needs without any major change to the architecture,
   either by contributing to HelioPy or building our own downloader;
-  having precise control of the data. The query can ask specific
   time range, probes, coordinates, etc. The module will check the
   availability of the data;
-  managing time-varying multi-dimensional distributions.
   This feature is of great importance to the mission module as it is
   not available for other Python packages;
-  ensuring the use of a proper data container providing raw data but
   also time range, metadata, etc;
-  offering a uniform interface to other AIDApy’s packages in order to
   perform advanced analysis on the mission data. For instance,
   an aidapy timeseries object can be generated using data from
   the mission package, given access to statistical tools and data
   processing to the final user.

Inputs
-------------
The philosophy of AIDApy is to ease as much as possible the user experience.
To this end, we decided to minimize the number of arguments entered by the user
and the knowledge required to obtain the desired data. Below is a list of the
parameters the code needs from the user:

1. The first parameter to enter is the start and the end of the requested time
   interval as a Python datetime.datetime object written as: datetime(year,
   month, day, hour, minute, second) or an astropy.Time object allowing to
   handle multiple time format such as GPS, ISOT, or FITS.

2. The second parameter specifies the mission from which to download the data,
   as a string: ``'mission' = '<mission1>'``.

3. The third parameter is a list of strings, containing the different probes
   of the multi spacecraft mission considered: ``'probes' = ['<probe1>',
   '<probe2>', ...]``. Note that for the single spacecraft mission or if one
   wants data from all probes, one can omit the ``'probes'`` parameter or set it
   to an empty string.

4. The fourth parameter is a string specifying the coordinate system the user
   wants the data in, such as: ``'coords' = '<coord_system>'``. Note that for the
   sake of clarity, it has been decided that data can be retrieved in only one
   coordinate system at once. By default, the coordinate system is set to 
   Geocentric Solar Ecliptic (GSE).

5. The last parameter to enter is a list of strings containing the data
   products that the user wants to be loaded (for instance the
   magnetic field vector, the ion density, etc), written as:
   ``'prod' = ['<product1>', '<product2>', ...]``. 
   As mentioned in the
   previous section, a catalog of all available products is embedded in the
   Mission subpackage, which will be updated on the fly as more and more
   space missions and datasets will be added. We note here that
   this catalog also includes Level 3 (L3) products that are not directly available 
   through open-access databases but are processed in the **AIDApy** package. 
   A preliminary catalog of detailed available products can be found below in
   the following table:

+----------------+----------+------------------------+---------------------------+
| Data product   | Level    | Available for missions | Description               |
+================+==========+========================+===========================+
| dc_mag         | L2       | - OMNIWeb              | 3-component (x, y, z) or  |
|                |          | - MMS                  | 4-component (x, y, z, tot)|
|                |          | - Cluster              | vector of magnetic field  |
+----------------+----------+------------------------+---------------------------+
| i_dens         | L2       | - OMNIWeb              | Ion number density        |
|                |          | - MMS                  |                           |
|                |          | - Cluster              |                           |
+----------------+----------+------------------------+---------------------------+
| e_dens         | L2       | - OMNIWeb              | Electron number density   |
|                |          | - MMS                  |                           |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_dist         | L2       | - MMS                  | 3D ion distribution       |
|                |          | - Cluster              | function                  |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| e_dist         | L2       | - MMS                  | 3D electron distribution  |
|                |          |                        | function                  |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_bulkv        | L2       | - MMS                  | Ion bulk velocity vector  |
|                |          | - Cluster              |                           |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| e_bulkv        | L2       | - MMS                  | Electron bulk velocity    |
|                |          | - Cluster              | vector                    |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_temppara     | L2       | - MMS                  | Ion temperature           |
|                |          | - Cluster              | parallel to dc_mag        |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_tempperp     | L2       | - MMS                  | Ion temperature           |
|                |          | - Cluster              | perpendicular to dc_mag   |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_temp         | L2       | - Cluster              | Total ion temperature     |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| all            | L2       | - OMNIWeb              | All products available    |
|                |          |                        | for OMNI data             |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| sc_pos         | L2       | - OMNIWeb              | Spacecraft location       |
|                |          | - MMS                  |                           |
|                |          | - Cluster              |                           |
+----------------+----------+------------------------+---------------------------+
| sc_att         | L2       | - MMS                  | Spacecraft attitude       |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| dc_elec        | L2       | - MMS                  | Direct-current electric   |
|                |          |                        | field                     |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| dc_elec        | L2       | - MMS                  | Direct-current electric   |
|                |          |                        | field                     |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_omniflux     | L2       | - MMS                  | Omnidirectional ion       |
|                |          |                        | energy spectrum           |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_energy       | L2       | - MMS                  | Ion energy channels table |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_aspoc        | L2       | - MMS                  | ASPOC instrument ion      |
|                |          |                        | current                   |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_prestens     | L2       | - MMS                  | Ion pressure tensor       |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_temptens     | L2       | - MMS                  | Ion temperature tensor    |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| i_heatq        | L2       | - MMS                  | Ion heat flux             |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| j_curl         | L3       | - MMS                  | Current density calculated|
|                |          | - Cluster              | from the Curlometer method|
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| mag_elev_angle | L3       | - OMNIWeb              | Magnetic elevation angle  |
|                |          | - MMS                  |                           |
|                |          | - Cluster              |                           |
+----------------+----------+------------------------+---------------------------+
| i_beta         | L3       | - MMS                  | Ion plasma beta           |
|                |          | - Cluster              |                           |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+
| e_beta         | L3       | - MMS                  | Electron plasma beta      |
|                |          | - Cluster              |                           |
|                |          |                        |                           |
+----------------+----------+------------------------+---------------------------+


High level interface
---------------------

The function :py:mod:`load_data` is used as an high-level interface with the mission subpackage.
Below is a code snippet showing how to define the inputs for the :py:mod:`load_data` function
using a Python dictionary:

.. code-block:: python

	# Define the time interval
	start_time = datetime(<year>, <month>, <day>, <hour>, <minute>, <second>)
	end_time = datetime(<year>, <month>, <day>, <hour>, <minute>, <second>)

	# Define the settings as a Python dictionary
	settings = {'prod': ['<prod1>', '<prod2>'], 'probes': ['<probe1>', '<probe2>'],
	'coords': '<coord_system>'}

Once the parameters are set up, we generate the Mission downloader and
download the data. This is done by calling the :py:mod:`load_data` function, that tells the 
Mission subpackage to create a specific downloader for every mission and time 
interval requested, and download and load
the desired data products for the specified probes and coordinate system:

.. code-block:: python

	data = load_data('mission'='<mission>', start_time, end_time, **settings)
	
The data is then returned in the data object and can be printed using the print()
Python command. The returned data is discussed in the following section.


Outputs
-------------
The DataArray and Dataset objects from the Python package
xarray (http://xarray.pydata.org/en/stable/) have been chosen as outputs for
the Mission subpackage, as they have been especially designed to handle
time-series of multidimensional data. It is basically an N-dimensional
array with labeled coordinates and dimensions, which also supports metadata
aware operations (see details in the Metadata subsection). It also provides
many functions to easily manipulate multidimensional data, such as indexing,
reshaping, resampling, etc.

The following code snippet is an example of what is printed when downloading
a 1D array (e.g., time series of values) of size (2000) and
a 2D array (e.g., time series of vector components) of size (1000,3) (the 
first dimension is the time and the second dimension is the vector components):

.. code-block:: python

	>>> print(data)
	<xarray.Dataset>
	Dimensions:                        (<1D_array_dimension1>: 2000, <2D_array_dimension1>: 1000, <2D_array_dimension2>: 3)
	Coordinates:
	  * <1D_array_dimension1>          (<time1>) datetime64[ns] 2013-08-05T00:00:00.000007 ... 2013-08-05T00:04:59.000987
	  * <2D_array_dimension1>          (<time2>) datetime64[ns] 2013-08-05T00:00:00.000006 ... 2013-08-05T00:05:00
	  * <2D_array_dimension2>          (<vector_components>) <U1 'x' ... 'z'
	Data variables:
		<prod1>                        (<time1>) float32 86.812 ... 29.063
		<prod2>                        (<time2>, <vector_components>) float32 144.979 ... 5.028
	Attributes:
		mission:  <mission>

The data retrieved from the Mission subpackage is an ``xarray.Dataset`` object,
which is basically a labeled dictionary of xarray.DataArray objects. This Dataset
contains two ``xarray.DataArray`` objects, which are in their turn N-dimensional
arrays with labeled coordinates and dimensions.
This Dataset object has a total of 3 ``Dimensions``, which represent the two 
``Coordinates`` (labels) of the 2D DataArray (``<vector_components>``, the xyz components
of the vector and ``time1``, the timestamps) and the coordinate (label) of the 1D DataArray
(``time2``, the timestamps).
The dimensions of the arrays are summarized in the ``Data variables`` section: each
DataArray has one ``Data variable`` that represent the queried data products.
The dimension of each data product (array) is shown in front of each data variable
(here (1000,3) and (2000)), as well as the data type and first and last value of 
each data product (i.e., DataArray).
Metadata is embedded in the objects ``Attributes`` in the form of a basic Python 
dictionary. For instance, the mission is written in the Dataset ``Attributes`` 
and the units and spacecraft location can be found in the ``Attributes`` of 
each DataArray object (e.g., units can be retrieved by typing ``data['prod1'].attrs['Units']``).

Plotting
-------------
The DataArray and Dataset objects provide a simplified plotting
system (see http://xarray.pydata.org/en/stable/plotting.html) based on
the popular matplotlib package (https://matplotlib.org). Thus, it is rather
easy to plot the data that is returned by the Mission subpackage using either the 
``xarray.Dataset.plot()`` or ``xarray.DataArray.plot()`` methods. For instance,
the following code snippet shows how to line plot the 1D array from the above Dataset:

.. code-block:: python

	>>> data['prod1'].plot()

The following code snippet shows how to line plot the 2D array from the above Dataset:

.. code-block:: python

	>>> data['prod2'].plot.line(x='time2')



File handling
-------------
Because the core of the downloading process is based on the HelioPy package,
we chose to borrow its file handling system.

1) Configuration file:

   HelioPy comes with a sample source or configuration file (“heliopyrc”),
   that is located in ``~/.heliopy/heliopyrc`` and can be customised by the user
   (the config parser will look in ~/.heliopy first). The default contents of
   the configuration file are:

- The working directory is the parent directory in which all downloaded data
  will be  stored. By default, it is set to: ``download_dir = ~/heliopy/data``
  Note that this default value may be changed to ``~/aidapy/data`` in the future.
  Inside this directory, the files are stored in a rather standardized folder
  tree with the following structure: ``~/mission/probe/instrument/mode``
  (if available, else the year).

- The user can also choose whether to convert all downloaded data to a
  hdf store, enabling much faster file reading after the initial load, but
  requiring the additional h5py and py-tables dependencies. By default, this
  value is set to False: ``use_hdf = False``

- In this file is also stored the user’s personal Cluster cookie that is
  required to download data from the Cluster Science Archive (CSA).
  This personal cookie can be retrieved by registering at the following
  address: http://www.cosmos.esa.int/web/csa/register-now . By default,
  the cookie value is not set: ``cluster_cookie = none``


2) File version control:

   One key point of the AIDA project objectives is to always deal with
   up-to-date data files, that evolve on the fly from open-access sources
   due to regular reprocessing of available datasets. Fortunately,
   the HelioPy package fulfills this requirement by getting the latest
   version of data files at every execution. In other words, the program checks
   the latest available files from the open-access sources every time data is
   requested. If the available file is not already in the user’s database,
   then it is downloaded and processed. Thus, the up-to-date data is returned
   to the user every time. This behavior will also be generalized to the AIDApy
   in the future. Every time the user will analyse spacecraft data in the AIDApy,
   the program will check if the latest available files are in the user database,
   otherwise it will download and process them.


.. py:module:: load_data
.. py:currentmodule:: load_data

load_data function
------------------

.. automodule:: aidapy.aidafunc.load_data
   :members:
   :undoc-members:
   :noindex:

