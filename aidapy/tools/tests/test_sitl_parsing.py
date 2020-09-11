import os
import glob
import pytest

import pandas as pd

from aidapy.tools.sitl_parsing import convert_sitl,\
    read_and_transform, generate_output_path


@pytest.fixture(scope="session")
def convert_file():
    """Setup code to create a groceries cart object with 6 items in it"""
    local_path = os.path.join('data', '2017-07-31_072433.txt')
    fixture_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    local_path,
    )

    files = glob.glob(fixture_path)

    for file_ in files:
        convert_sitl(file_)

    converted_path = generate_output_path(fixture_path)
    converted_files = glob.glob(converted_path)

    return converted_files


def test_location_counts(convert_file):
    converted_files = convert_file
    df_list = []
    for file_ in converted_files:
        df = read_and_transform(file_)
        df_list.append(df)
    final_df = pd.concat(df_list)
    value_counts = final_df['LOCATION'].value_counts()
    assert value_counts['NOTHING'] == 26
    assert value_counts['MAGNETOTAIL'] == 2

