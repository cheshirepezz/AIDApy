# -*- coding: utf-8 -*-

import os
import re
import ntpath
import pandas as pd


def generate_location_dict():
    magnetosphere = ['chorus', 'Chorus-like', 'Chorus', 'Magnetospheric',
                     'magnetospheric', 'Microinjections',
                     'micro injection', 'micro  injection',
                     'plasmapause', 'EMIC', 'Radiation belt',
                     'radiation belts', ' PP ', 'Msphere', 'Msph', 'Magnetosphere',
                     'MSPH', 'magnetosphere', 'MSPhere', 'plasmasphere',
                     'msphere', ' MSP ']
    magnetosphere.extend(prepare_small_string('PP'))

    plasma_sheet = ['plasmshet', 'neutral sheet', 'Outer PS', 'outerPS',
     'Neutral sheet', 'Plasma sheet',
     'Plasma Sheet', 'plasma sheet', 'plasmasheet',
     'Plasmasheet', 'CPS', 'plasam sheet']
    plasma_sheet.extend(prepare_small_string('PS'))
    plasma_sheet.extend(prepare_small_string('ps'))
    plasma_sheet.extend(prepare_small_string('Ns'))
    plasma_sheet.extend(prepare_small_string('NS'))
    plasma_sheet.extend(prepare_small_string('ULF'))


    solar_wind = ['Sowlar Wind', 'Solar Wnd', 'Sowlar Wind', 'sowlar wind',
     'solar wind', 'Solar wind', 'Solar Wind', 'solar wnd',
     'soalr wind', 'Solar WInd', 'Soar wind', 'Solar wnid',
     'SW-Current Sheets', 'interplanetary shock', 'Interplanetary shock',
     'sola wind', 'solarwind', 'Solarwind']
    solar_wind.extend(prepare_small_string('SW'))
    solar_wind.extend(prepare_small_string('IMF'))
    solar_wind.extend(prepare_small_string('Sw'))

    magnetosheath = ['MAgnetosheath', 'magnetoshearth', 'Manetosheath CS',
     'Magnetsheath', 'msheath', 'MSheath',
     'magnetosheah', 'magntosheath', 'magnetosheatht',
     'magnetosheat', 'magnetoshea', 'Magnetosheat',
     'Magnetosheath', 'Msheath', 'magnetosheath', 'Sheath',
     'msth', 'MShetah', 'magentosheath', 'mangetosheath', 'sheath', 'Msehat',
     'Magnetosheaht', 'Magnetoshetah', 'Magnetohseath',
     'Mshseath', 'magntosheet', 'Magnetoeath']
    magnetosheath.extend(prepare_small_string('MSH'))
    magnetosheath.extend(prepare_small_string('MS'))
    magnetosheath.extend(prepare_small_string('MsH'))
    magnetosheath.extend(prepare_small_string('msh'))
    magnetosheath.extend(prepare_small_string('ms'))
    magnetosheath.extend(prepare_small_string('SMH'))


    magnetotail = ['Train of BBFs and dipolarizations', 'Bz Dipolarizations',
     'Bursty bulk flows', 'Dipoolarization front',
     'tail', 'Two Dipolarizations', 'dipolarization',
     'DPfronts', 'DPfront', 'DP front',
     'Dipolarization', 'dipolarziation front', 'BBFs',
     'Dipolazrization front', 'DP event', 'Dipolarzition front',
     'Bursty bulk flow', 'Bursty Bulk Flow',
     'bursty bulk flow', 'Tailward', 'magnetotail', 'Bursty Bulk FLow',
     'Magnetotail', 'Mtail', 'Bursty bluk flows', 'Dipolarizion front']
    magnetotail.extend(prepare_small_string('BBF'))
    magnetotail.extend(prepare_small_string('DP'))
    magnetotail.extend(prepare_small_string('DFs'))
    magnetotail.extend(prepare_small_string('DPF'))
    magnetotail.extend(prepare_small_string('DF'))

    bow_shock = ['Bopw shock', 'Q-para', 'shock transition',
     'bow shockj', 'Quasi-perp bow showck',
     'Q-parallel Bow Schock', 'Qpar bows hock',
     'Q-perp shock', 'q-perp shock',
     'Quasi-perp bowshock', 'quasi-perp shock',
     'Quasi perpendicular Bow Shock',
     'Quasi-perp shock', 'Perpendicular shock',
     'perp shock', 'quasi-perpendicular shock',
     'q-para shock', 'Q par BShock', 'Qperp shock', 'QPerp shock',
     'quasi-para shock', 'Quasi-para shock',
     'Qparallel shock', 'Quasiparallel Shock',
     'Quasi-parallel Bow Shock', 'Q-par shock',
     'Quasi-parallel shock', 'quasi-par shock',
     'Quasi-par shock', 'Quasi-Parallel shock',
     'bowshock', 'bo shock', 'BS-crossing',
     'boswshock', 'Bowshock', 'bow-shock',
     'bows shock', 'bow shocks', 'quasi-parallel shocks',
     'quasi-parallel shock', 'parallel shock',
     'Bow shocks', 'Bow Shock', 'Bow shock',
     'bow shock', 'Quasi-perp Shock', 'Qpar bows hock' 'partial shock',
     'Oblique shock', 'Quasi-parallel shocks', 'Bopw shock',
     'Q-para shock', 'Multiple shock', 'multiple shock', 'bow shockj',
     'boe shock']
    bow_shock.extend((prepare_small_string('BS')))
    bow_shock.extend((prepare_small_string('shocks')))
    bow_shock.extend((prepare_small_string('Shock')))
    bow_shock.extend((prepare_small_string('shock')))

    magnetopause = ['magnetopause', 'Magnetopause',
     'magnetopaus', 'Magnetopaus', 'Mpause',
     'mpause', 'magnteopaue', 'magneotpause',
     'Magnetopsue', 'magnetopuse']
    magnetopause.extend(prepare_small_string('MP'))
    magnetopause.extend(prepare_small_string('MPs'))
    magnetopause.extend(prepare_small_string('Mp'))
    magnetopause.extend(prepare_small_string('mp'))

    foreshock = ['Foreshock-like', 'Foreshock-related', 'Upstream',
     'upstream', 'fore shock', 'foreshock', 'forshock',
     'Foreshock', 'Foershock', 'Forshock', 'for3shock']
    foreshock.extend(prepare_small_string('FS'))
    foreshock.extend(prepare_small_string('fs'))
    foreshock.extend(prepare_small_string('Fs'))

    psbl = ['PSBL', 'psbl', 'PLSBl', 'lobe', 'Lobe', 'LOBE',
            'Mantle', 'mantle']
    psbl.extend(prepare_small_string('PSBL'))
    psbl.extend(prepare_small_string('psbl'))

    boundary_layer = ['boundary layer', 'Boundary layer', 'boundary transition',
     'Boundary Layer', 'LLBL', 'Boundar layer',
     'bounday layer', 'BoundaryLayer']
    boundary_layer.extend(prepare_small_string('BL'))
    boundary_layer.extend(prepare_small_string('bl'))
    boundary_layer.extend(prepare_small_string('Bl'))

    LOCATION_LIST = {"MAGNETOSPHERE": magnetosphere,
                     "PLASMA_SHEET": plasma_sheet,
                     "SOLAR_WIND": solar_wind,
                     "MAGNETOSHEATH": magnetosheath,
                     "MAGNETOTAIL": magnetotail,
                     "BOW_SHOCK": bow_shock,
                     "MAGNETOPAUSE": magnetopause,
                     "FORESHOCK": foreshock,
                     "PSBL": psbl,
                     "BOUNDARY_LAYER": boundary_layer
                     }

    return LOCATION_LIST

def generate_event_dict():

    dipolarization_front = ['Dipoolarization front', 'DP fronts',
                   'DPfronts', 'DPfront', 'DP front','dipolarziation front',
                   'Dipolazrization front', 'Dipolarzition front',
                   'Dipolarizion front', 'Dipolarazitaion front',
                   'Bz fronts','Bz front', 'Dipolariz. Front',
                   'Dipolatization front', 'dipolazation front',
                    'dipolariztaion front', 'dipolariztionn front',
                    'dipolarizatiuon fronts', 'dipolariztion front',
                    'Dpfront', 'Dp front', 'dipolarizatipon front',
                    'jet fronts', 'jet front', 'Jet front',
                    'Front', 'front']
    dipolarization_front.extend(prepare_small_string('DFs'))
    dipolarization_front.extend(prepare_small_string('DPF'))
    dipolarization_front.extend(prepare_small_string('DF'))

    bursty_bulk_flow = ['bursty bulk flows', 'bursty bulk flow',
                        'Bursty bulk flows', 'Bursty bulk flow']
    bursty_bulk_flow.extend(prepare_small_string('BBFs'))
    bursty_bulk_flow.extend(prepare_small_string('BBF'))

    plasma_jet = ['jets', 'jet']

    EVENT_LIST = {"DIPOLARIZATION_FRONT": dipolarization_front,
                  "BURSTY_BULK_FLOW": bursty_bulk_flow,
                  "PLASMA_JET": plasma_jet}

    return EVENT_LIST


def read_and_transform(file_name, category='location'):
    """
    Read the formated SITL report (preprocessed and ready to be read)
    as a Pandas Dataframe and add new columns (location, events, etc.)

    Parameters
    ----------
    file_name : str
        File name of the cleaned and prepared SITL report.

    category : str
        Specify which category are generated (location, events, etc.)

    Returns
    -------
    df : DataFrame object
        A df with all the information from the SITL report.
        Start time, end time, the location, and the associated text.
    """
    df = pd.read_csv(file_name)
    df['START TIME'] = pd.to_datetime(df['START TIME'])
    df['END TIME'] = pd.to_datetime(df['END TIME'])
    # df['DISCUSSION'] = df['DISCUSSION'].str.lower()
    df['LOCATION'] = get_info(df['DISCUSSION'], category=category)
    return df


def get_info(discussion_column, category='location'):
    """
    Generate a list of keys (from category) from a Serie of strings.

    Parameters
    ----------
    discussion_column : Series object
        Specific column from the SITL associated to the SITL discussion.

    category : str
        Specify which category are generated (location, events, etc.)

    Returns
    -------
    output : list of XXXX
        A df with all the information from the SITL report.
        Start time, end time, the location, and the associated text.
    """
    if category not in ['location', 'event']:
        raise ValueError('Get info only works for location or event')

    output = [look_for(text, category=category) for text in discussion_column]
    return output


def look_for(string, category=None):
    """
    Look for the presence of specific patterns in the SITL comments.

    Parameters
    ----------
    string : str
        SITL discussion string

    Returns
    -------
    output_key : str
        Key associated to the identified pattern.
        Example: 'ms' if 'magnetosphere' has been identified in string.
    """
    if category == 'event':
        key_pattern_association = generate_event_dict()
    elif category == 'location':
        key_pattern_association = generate_location_dict()
    else:
        raise NotImplementedError('{} is not yet implemented'.format(category))

    output_event = []
    events_list = list(key_pattern_association.values())
    # events_list = [item for sublist in events_list for item in sublist]

    PSBL_true = False

    # Various extra symbols and characters are added to the pattern.
    for sub_events_list in events_list:
        for event in sub_events_list:
#            if ' ' + event + ' ' in ' ' + string + ' ' or ' ' + event + '.' in ' ' + string + ' ' \
#                    or ' ' + event + ')' in ' ' + string + ' ' or '(' + event + ' ' in ' ' + string + ' ' \
#                    or ' ' + event + ';' in ' ' + string + ' ' or ';' + event + ' ' in ' ' + string + ' ' \
#                    or event + ' ' in ' ' + string + ' ':
            if event in ' ' + string + ' ':
                output_event.append(event)
                break

    # It none of the elements in key_pattern_association is found,
    # we have 'nothing'.
    if len(output_event) == 0:
        output_event.append('NOTHING')
    elif len(output_event) > 1:
        for key, value_list in key_pattern_association.items():
            for value in value_list:
                # output_event = [w.replace(value, key) for w in output_event]
                output_event = [key if w == value else w for w in output_event]
        output_event = ['MULTIPLE_LABELS' + '_' + '_'.join(output_event)]
    else:
        for key, value_list in key_pattern_association.items():
            for value in value_list:
                # output_event = [w.replace(value, key) for w in output_event]
                output_event = [key if w == value else w for w in output_event]

    # Remove potential duplicates
    output_event = list(set(output_event))

    output_key = output_event[-1]

    return output_key


def convert_sitl(file_path, specific_output_path=None):
    """
    Convert the SITL report into file readable by Pandas.
    It is written in the formated folder.

    Parameters
    ----------
    file_path : str
        File path of the SITL report.

    specific_output_path: str
        Specific the name of the folder (in the SITL report folder) where we
        want to save the converted report.
    """
    # Read in the file
    to_keep = []
    selection = False
    selection_line = 0
    with open(file_path, 'r') as file:
        for line_no, line in enumerate(file):
            if "List of selections" in line or selection:
                selection = True
                selection_line += 1
            if line_no > 14 or selection_line > 2:
                # Start and end time are separated by - (replace by a comma)
                corrected_line = line.replace(' - ', ',')
                splitted_line = corrected_line.split(',', maxsplit=4)
                # Remove line without 4 elements
                if len(splitted_line) < 3:
                    continue
                # Specific case when no observation
                if 'ABS' in splitted_line[3]:
                    continue

                # merge the discussion column, SITL can use comma in the text
                splitted_line[-1] = splitted_line[-1].replace(',', ' ')
                corrected_file = ','.join(splitted_line)
                # Remove space before and after the comma
                corrected_file = re.sub(r'\s*,\s*', ',', corrected_file)
                to_keep.append(corrected_file)

    # Write the file
    output_path = generate_output_path(file_path, specific_output_path)

    with open(output_path, 'w') as file2:
        for item in to_keep:
            file2.write("%s" % item)


def generate_output_path(input_file_path, specific_output_path=None):
    """
    Generate the output path where to write a new file from the path of
    an existing file.
    By default, the new output_path is in the 'formated' folder present in
    the folder of the existing file.

    Parameters
    ----------
    input_file_path : str
        File path of the existing file.

    specific_output_path: str
        Specific the name of the folder (in the SITL report folder) where we
        want to save the converted report.

    Returns
    -------
    output_path : str
        Output path for the new files.
        By default, associated path to 'formated'
    """
    # Write the file
    file_path, file_name = ntpath.split(input_file_path)
    if not specific_output_path:
        output_path = os.path.join(file_path, 'formated', file_name)
    else:
        output_path = os.path.join(specific_output_path, file_name)
        # Else Check output_path
    return output_path


def path_leaf(path):
    """
    Extract the file name from a path.
    If the file ends with a slash, the basename will be empty,
    so the function to deal with it

    Parameters
    ----------
    path : str
        Path of the file

    Returns
    -------
    output : str
        The name of the file
    """
    head, tail = ntpath.split(path)
    output = tail or ntpath.basename(head)
    return output


def prepare_small_string(string):
    improved_list = list()
    improved_list.append(' ' + string + ' ')
    improved_list.append(' ' + string + '.')
    improved_list.append('.' + string + ' ')
    improved_list.append(' ' + string + ')')
    improved_list.append('(' + string + ' ')
    improved_list.append(' ' + string + ';')
    improved_list.append(';' + string + ' ')
    improved_list.append(' ' + string + '/')
    improved_list.append('/' + string + ' ')

    return improved_list
