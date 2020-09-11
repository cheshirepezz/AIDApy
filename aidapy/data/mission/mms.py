#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module serves as data manager for MMS

Authors : Romain Dupuis, Hugo Breuillard """
from collections import OrderedDict

#import heliopy.data.mms as mms
import heliopy_multid.data.mms as mms
from aidapy.data.mission.base_mission import BaseMission


class Mms(BaseMission):
    """MMS data manager.

    Parameters
    ----------
    t_start : datetime object
        It gives the time at which we started to look at the data

    t_end : datetime object
        It gives the time at which we finished looking at the data

    Attributes
    ----------
    meta_data : metadata object
        Contains all the metadata. It is generated after the data

    data : dict of sunpy timeseries object
        Dict containing the time series queried by the user

    mission : str
        Name of the mission
    """
    def __init__(self, t_start, t_end):
        super().__init__(t_start, t_end)
        self.mission = 'mms'
        self.instrument = None
        self._mode = 'low_res'
        self.coords = 'gse'
        self.allowed_probes = ['1', '2', '3', '4']
        self.probes = ['1', '2']  # , '3']
        self._probe = '1'
        self.data_types = ['dc_mag']
        self.json_conversion = {}
        self.frame = 'dbcs'

    def set_observation(self, obs_settings):
        """Set parameter for the observation.
        """
        self.instrument = obs_settings['instr']
        self.product_string = obs_settings['prod_string']
        # self.product_list = obs_settings['cdf_key']
        self.product_list = obs_settings['prod']

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
        if self.frame:
            json_str = json_str.replace('${frame}', self.frame)

        return json_str

    def _download_ts(self):
        mms_df = mms.download_files(self._probe, self.instrument, self._mode,
                                    self.t_start.datetime, self.t_end.datetime,
                                    product_string=self.product_string,
                                    product_list=self.product_list,
                                    xarray=True)

        if self.instrument != "mec":
            mms_metadata = mms.download_files(
                self._probe, 'mec', 'srvy', self.t_start.datetime,
                self.t_end.datetime, product_list=
                {'sc_pos': 'mms{0}_mec_r_{1}'.format(
                    self._probe, self.coords)},
                xarray=True)
            # Add mms_metadata to mms_df as an entry in attrs
            mms_df.attrs['pos_gse'] = mms_metadata

        return mms_df
