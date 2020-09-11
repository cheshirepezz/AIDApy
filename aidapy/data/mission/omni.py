#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module serves as data manager for Omniweb

Authors : Romain Dupuis, Hugo Breuillard """

from collections import OrderedDict
import pandas as pd
import xarray as xr

import heliopy.data.omni as omni

from aidapy.data.mission.base_mission import BaseMission
from heliopy_multid.data.util import convert_units_to_str


class Omni(BaseMission):
    """Omniweb data manager

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

    ts : timeseries object
        Contains the time series queried by the user

    mission : str
        Name of the misson
    """
    def __init__(self, t_start, t_end):
        super().__init__(t_start, t_end)
        self.mission = 'omni'
        self.allowed_probes = ['1']
        self.probes = ['1']
        self._probe = '1'
        self.coords = 'gse'
        self.data_types = ['all']

    def _download_ts(self):
        omni_ts = omni.h0_mrg1hr(self.t_start.datetime, self.t_end.datetime)
        omni_df = omni_ts.data
        omni_units = omni_ts.units
        time_index = omni_ts.index

        omni_units = convert_units_to_str(omni_units)

        # Remove the strange variables with 1800 in the name
        omni_df = omni_df[omni_df.columns.drop(list(omni_df.filter(regex='1800')))]

        if self.product_list:
            prod_list = []
            for val in self.product_list:
                prod_list.append(val)
            thisdata = pd.DataFrame(omni_df, columns=prod_list)
            data = xr.DataArray(thisdata, coords=[time_index, prod_list],
                                dims=['time', 'products'])
            data.attrs['Units'] = {}
            for product in prod_list:
                data.attrs['Units'][product] = omni_units[product]
        else:
            thisdata = pd.DataFrame(omni_df)
            data = xr.Dataset({})
            for i, product in enumerate(thisdata.columns):
                data[product] = xr.DataArray(thisdata[product],
                                             coords=[time_index],
                                             dims=['time'])
            data.attrs['Units'] = omni_units
        omni_output = data

        return omni_output

    def set_observation(self, obs_settings):
        """Doc string
        """
        self.product_list = obs_settings['prod']

    def _json_replace(self, json_str):
        json_str = json_str.replace('${coords}', self.coords.upper())
        #json_str = json_str.replace('${name_all}', str(self.names[3:])[1:-1])
        return json_str

    def _set_mode_default(self, obs_settings):
        """Set the mode specific to each instrument.
        """
        self._mode = None

    @classmethod
    def variables_info(cls):
        r"""Print variables info with corresponding index
        """
        print('This is the list of variables downloaded from OMNIWEB')
        for variable in cls.names:
            print(variable)
            print('-----------------------------')
