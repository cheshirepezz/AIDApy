#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module serves to build high level interface to use mission data

Author : Romain Dupuis """

import aidapy.data.mission.omni as omni
import aidapy.data.mission.mms as mms
import aidapy.data.mission.cluster as cluster


class Mission:
    """Docstring
    """
    def __init__(self, mission_name, t_start, t_end):
        self.concrete_mission = mission_factory.get_mission(mission_name,
                                                            t_start, t_end)

    def download_data(self, data_types=None, probes=None, coords=None,
                      mode=None, frame=None):
        """Method at the Mission level to query data downloading
        """
        if not self.concrete_mission:
            raise ValueError('You must generate the mission before')
        return self.concrete_mission.download_data(data_types, probes,
                                                   coords, mode, frame)

    def get_info_on_mission(self):
        """Provide information on the mission
        """
        # raise NotImplementedError()
        self.concrete_mission.set_data_settings()
        return self.concrete_mission.get_mission_info()


class MissionFactory:
    """Docstring of MissionFactory
    """
    def __init__(self):
        self._mission_creators = {}

    def register_mission(self, mission_name, mission_creator):
        """Add the implemented mission to the list of available cretors
        """
        self._mission_creators[mission_name] = mission_creator

    def get_mission(self, mission_name, t_start, t_end):
        """Provide the relevant mission object
        """
        mission_created = self._mission_creators.get(mission_name)
        if not mission_created:
            raise ValueError('the mission {} is not yet implemented'.format(
                mission_name))
        return mission_created(t_start, t_end)


mission_factory = MissionFactory()
mission_factory.register_mission('omni', omni.Omni)
mission_factory.register_mission('mms', mms.Mms)
mission_factory.register_mission('cluster', cluster.Cluster)
