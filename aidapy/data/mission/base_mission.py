#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module serves as base for all the mission data manager

Author : Romain Dupuis """
#from collections import abc
from abc import abstractmethod
import os
import json

from datetime import datetime
from astropy.time import Time


class BaseMission:
    """Base format for the data downloaded from missions

    Parameters
    ----------
    t_start : datetime object
        It gives the time at which we started to look at the data

    t_end : datetime object
        It gives the time at which we finished looking at the data

    Attributes
    ----------
    """
    def __init__(self, t_start, t_end):
        self.meta_data = None
        self.mission = None
        self.instrument = None
        self.allowed_probes = None
        self.probes = None
        self.data_settings = {}
        self.product_list = None
        self.product_string = None
        self._probe = None
        self.coords = None
        self.mode = "low_res"  # Default mode for all missions
        self.frame = None

        self.t_start = self._to_astropy_time(t_start)
        self.t_end = self._to_astropy_time(t_end)

    def __repr__(self):
        return 'Data manager for {} mission \n' \
               ' Start time is {}\n' \
               'End time is {}'.format(
                   self.mission, self.t_start, self.t_end)

    @staticmethod
    def _check_time_format(time_instance):
        """Check the time format.

        Parameters
        ----------
        time_instance : datetime or astropy.time instance
            Time object we want to convert
        """
        if not isinstance(time_instance, (Time, datetime)):
            raise TypeError("the time must be a datetime "
                            "or astropy.time instance")
        if isinstance(time_instance, Time) and len(time_instance) != 1:
            raise TypeError('the astropy.time must have a single value')
        return True

    def _to_astropy_time(self, time_instance):
        """Convert the input instance to astropy.time.

        Parameters
        ----------
        time_instance : datetime or astropy.time instance
            Time object we want to convert

        Return
        ------
        astropy_time : astropy.time instance
        """
        checked_time_format = self._check_time_format(time_instance)
        if checked_time_format:
            astropy_time = Time(time_instance)
        return astropy_time

    @staticmethod
    def convert_time(time, format_out):
        """Convert time to an accepted astropy time format

        Parameters
        ----------
        time : datetime or astropy.time instance
            Time object we want to convert

        format_out : str
            Indicates what is the format output.
            Must be a format accepted by astropy
        """
        if format_out not in Time.FORMATS.keys():
            raise TypeError('{0} is not an accepted format by astropy.Time, '
                            ' must be in {1}'.format(
                                format_out, Time.FORMATS.keys()))
        if isinstance(time, Time) and len(time) == 1:
            output_time = getattr(time, format_out)
        return output_time

    def _check_data_types(self, data_types):
        for data_type in data_types:
            if data_type not in self.data_settings.keys():
                raise ValueError(('{0} is not an available data type, '
                                  'the following are available:{1}').format(
                                      data_type, self.data_settings.keys()))
        return True

    def download_data(self, data_types, probes, coords, mode, frame):
        """Download data
        """
        if data_types is None:
            data_types = self.data_types

        data_types_converted = self._convert_to_list(data_types)
        data_dict = {}

        self.set_coords(coords)
        self.set_probes(probes)
        self.set_mode(mode)
        self.set_frame(frame)

        for data_type in data_types_converted:
            for probe in self.probes:
                self.set_probe(probe)
                if not self.mode or self.mode in ['low_res', 'high_res']:
                    self.set_data_settings()
                    self._check_data_types(data_types_converted)
                    data_setting = self.data_settings[data_type]
                    self._set_mode_default(data_setting)
                    self.set_data_settings()
                    data_setting = self.data_settings[data_type]
                else:
                    self._set_mode_defined()
                    self.set_data_settings()
                    self._check_data_types(data_types_converted)
                    data_setting = self.data_settings[data_type]

                self.set_observation(data_setting)
                ts = self._download_ts()
                ts_with_units = self.parse_units(ts)
                #data_dict[self.mission+probe+'_'+data_type] = ts_with_units
                data_dict[data_type+probe] = ts_with_units

        return data_dict

    def set_probes(self, probes):
        """Set the probes
        """
        if probes is None:
            probes = self.allowed_probes #[self._probe]
        converted_probes = self._convert_to_list(probes, probes=True)
        if self._check_probes(converted_probes):
            self.probes = converted_probes

    def set_probe(self, probe):
        """Set the current working probe
        """
        if probe:
            self._probe = probe

    def set_coords(self, coords):
        """Set the coordinates
        """
        if coords:
            self.coords = coords

    def set_mode(self, mode):
        """Set the instrument mode
        """
        if mode:
            self.mode = mode

    def set_frame(self, frame):
        """Set the frame only for spacecraft attitude
        """
        if frame:
            self.frame = frame

    def set_data_settings(self):
        """Docstring
        """
        if self._probe and self.coords and self.mode:
            path_settings = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 'mission_settings',
                '{}.json'.format(self.mission)))
            with open(path_settings) as f:
                d = json.load(f)  # , object_pairs_hook=OrderedDict)
                data_settings_str = json.dumps(d)
                data_settings_final = self._json_replace(data_settings_str)
                self.data_settings = json.loads(data_settings_final)

    def _check_probes(self, probes):
        """ This simple method checks if the list of probes is allowed:
        """
        # Check if the list is a subset of the allowed probes
        if set(probes).issubset(set(self.allowed_probes)):
            output = True
        else:
            raise ValueError('The queried probes {0} are not allowed, '
                             ' must be in {1}'.format(probes,
                                                      self.allowed_probes))
        return output

    @staticmethod
    def _convert_to_list(input_, probes=False):
        """ This simple method converts probe_input into a list
        if it is a str, an int, or a list
        """
        if isinstance(input_, str):
            output_ = [input_]
        elif isinstance(input_, int) and probes:
            output_ = [str(input_)]
        elif isinstance(input_, list):
            output_ = [str(i) for i in input_]
        elif probes:
            raise ValueError('Convert only str, int, or list. '
                             'Wrong argument type for probes: {}'.format(
                                 type(input_)))
        else:
            raise ValueError('Convert only str, or list. '
                             'Wrong argument type: {}'.format(type(input_)))
        return output_

    def get_mission_info(self):
        """
         Provide information on the mission

        Return
        ------
        info : dict
            Dictionary with information on the mission with the following keys
            - name:
            - allowed_probes:
            - data_settings:
        """
        info = dict()
        info['name'] = self.mission
        info['allowed_probes'] = self.allowed_probes
        info['data_settings'] = self.data_settings
        return info

    @staticmethod
    def parse_units(xarray_obj):
        """ Convert unit at the dim level to unit at coord level
        """
        #attrs = xarray_obj.attrs
        #dims = xarray_obj.dims
        #coords = xarray_obj.coords
        #new_attrs = OrderedDict()

        ## if all units at coor level are the same,
        # units are kept at the dim level
        #for attr_key, attr_value in attrs.items():
        #    if attr_key in dims:
        #        for coord in coords[attr_key]:
        #            new_attrs[str(coord.values)] = attr_value
        #    else:
        #        new_attrs[attr_key] = attr_value
        #xarray_obj.attrs = new_attrs
        return xarray_obj

    @abstractmethod
    def set_observation(self, obs_settings):
        """ Abstract method to set the different parameters of the mission
        """
        raise NotImplementedError()

    @abstractmethod
    def _set_mode_defined(self):
        """ Abstract method to set the modes for each instrument
        """
        raise NotImplementedError()

    @abstractmethod
    def _set_mode_default(self, obs_settings):
        """ Abstract method to set the modes for each instrument
        """
        raise NotImplementedError()

    @abstractmethod
    def _json_replace(self):
        """ Abstract method to replace values in json mission settings
        """
        raise NotImplementedError()

    @abstractmethod
    def _download_ts(self):
        """ Abstract method to download sunpy timeseries from heliopy
        """
        raise NotImplementedError()
