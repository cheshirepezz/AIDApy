import pytest
from aidapy import get_mission_info

missions = ['omni', 'mms', 'cluster']


@pytest.mark.parametrize("mission", missions)
def test_get_name(mission):
    info = get_mission_info(mission)
    name = info['name']
    if mission is 'mms':
        true_name = 'mms'
    elif mission is 'cluster':
        true_name = 'cluster'
    elif mission is 'omni':
        true_name = 'omni'
    assert name == true_name


@pytest.mark.parametrize("mission", missions)
def test_get_allowed_probed(mission):
    info = get_mission_info(mission)
    allowed_probes = info['allowed_probes']
    if mission is 'mms':
        true_allowed_probes = ['1', '2', '3', '4']
    elif mission is 'cluster':
        true_allowed_probes = ['1', '2', '3', '4']
    elif mission is 'omni':
        true_allowed_probes = ['1']
    assert allowed_probes == true_allowed_probes


@pytest.mark.parametrize("mission", missions)
def test_get_data_settings(mission):
    info = get_mission_info(mission)
    data_settings = info['data_settings']
    if mission is 'mms':
        true_data_settings = ['dc_mag', 'i_dens', 'e_bulkv', 'i_dist']
    elif mission is 'cluster':
        true_data_settings = ['dc_mag', 'i_dens', 'i_dist']
    elif mission is 'omni':
        true_data_settings = ['dc_mag', 'i_dens', 'all']
    assert all(x in data_settings for x in true_data_settings)


@pytest.mark.parametrize("mission", missions)
def test_get_info_with_prod(mission):
    info = get_mission_info(mission, product='magnetic')
    assert info == ['dc_mag']
