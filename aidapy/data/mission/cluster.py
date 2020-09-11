#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module serves as data manager for cluster

Authors : Romain Dupuis, Hugo Breuillard """

from collections import OrderedDict
#import heliopy.data.cluster as cluster
import heliopy_multid.data.cluster as cluster
from aidapy.data.mission.base_mission import BaseMission


class Cluster(BaseMission):
    """Cluster data manager.

    Parameters
    ----------
    t_start : datetime or astropy object
        It gives the time at which we started to look at the data

    t_end : datetime or astropy object
        It gives the time at which we finished looking at the data

    Attributes
    ----------
    mission : str
        Name of the mission

    allowed_probes : list of str
        List of probes available for the mission

    probes : list of str
        List of probes from which the downloader is going
        to download data

    coords : str
        Coordinates in which the data are downloaded
    """
    def __init__(self, t_start, t_end):
        super().__init__(t_start, t_end)
        self.mission = 'cluster'
        self.allowed_probes = ['1', '2', '3', '4']
        self.probes = ['1']
        self.coords = 'gse'
        self._probe = '3'
        self.data_types = ['dc_mag']
        self._mode = "low_res"

    def set_observation(self, obs_settings):
        """Set parameter for the observation.
        """
        self.instrument = obs_settings['instr']
        self.product_string = obs_settings['prod_string']
        self.product_list = obs_settings['cdf_key']

    def _set_mode_default(self, obs_settings):
        """Set the mode specific to each instrument.
        """
        self._mode = obs_settings[self.mode]

    def _set_mode_defined(self):
        """Set the mode specific to each instrument.
        """
        self._mode = self.mode

    def _json_replace(self, json_str):
        json_str = json_str.replace('${probe}', self._probe)
        json_str = json_str.replace('${coords}', self.coords)
        json_str = json_str.replace('${mode}', self._mode)
        return json_str

    def _download_ts(self):
        cluster_df = cluster._load(self._probe, self.t_start.datetime,
                                   self.t_end.datetime, self.instrument,
                                   product_id=self.product_string,
                                   product_list=self.product_list,
                                   try_download=True, xarray=True)

        cluster_metadata = cluster._load(self._probe, self.t_start.datetime,
                                         self.t_end.datetime, 'fgm',
                                         product_id='CP_FGM_SPIN',
                                         product_list=
                                         {'pos_gse':
                                              'sc_pos_xyz_gse__C{}_CP_FGM_SPIN'
                                              .format(self._probe)},
                                         try_download=True, xarray=True)

        # Add mms_metadata to mms_df as an entry in attrs
        cluster_df.attrs['pos_gse'] = cluster_metadata

        return cluster_df
