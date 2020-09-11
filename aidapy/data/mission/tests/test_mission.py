from datetime import datetime
import pytest

from aidapy.data.mission.base_mission import BaseMission
from aidapy.data.mission.mission import Mission
# TODO: Add mocks or substitutes to replace all calls of the download methods
# of heliopy (very long to load)


class TestBaseMissionClass(object):
    def test_check_time_format_start(self):
        with pytest.raises(TypeError) as type_info:
            t_start = 'toto'
            t_end = datetime(1970, 1, 3, 0, 0, 0)
            BaseMission(t_start, t_end)
        assert str(type_info.value) == 'the time must be a datetime' \
                                       ' or astropy.time instance'

    def test_check_time_format_end(self):
        with pytest.raises(TypeError) as type_info:
            t_start = datetime(1970, 1, 3, 0, 0, 0)
            t_end = 'toto'
            BaseMission(t_start, t_end)
        assert str(type_info.value) == 'the time must be a datetime' \
                                       ' or astropy.time instance'

    def test_mission_registered(self):
        t_start = datetime(1970, 1, 3, 0, 0, 0)
        t_end = datetime(1970, 1, 3, 1, 0, 0)
        with pytest.raises(ValueError) as type_info:
            Mission('toto', t_start, t_end)
        assert str(type_info.value) == 'the mission {} is not yet' \
                                       ' implemented'.format('toto')
