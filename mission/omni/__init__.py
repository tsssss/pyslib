import os
import system.manager as smg
import libs.system as system
from datetime import datetime

# Default settings.
local_data_root = os.path.join(system.diskdir('data'),'omni')
if not os.path.exists(local_data_root): local_data_root = os.path.join(system.homedir(),'data','omni')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'

assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'


def _file_request(
    input_time_range,
):

    file_request = dict()
    file_request['time_range'] = smg.prepare_time_range(input_time_range)
    file_request['cadence'] = 'month'

    return file_request



def valid_range(id, probe=None):

    valid_ranges = dict()

    valid_ranges['ae'] = ['1995-01-01','2018-12-31/24:00']
    
    now = datetime.now().strftime('%Y-%m-%d') 
    valid_ranges['cdaweb%hourly'] = ['1963',now]
    valid_ranges['cdaweb%hro'] = ['1981',now]
    valid_ranges['cdaweb%hro2'] = ['1995',now]

    if id not in valid_ranges: raise Exception(f'Unknown id: {id} ...')
    return valid_ranges[id]


def load_file(
    input_time_range,
    input_id='cdaweb%hro2',
    version='v*',
    file_times=None,
    local_data_dir=local_data_root,
    remote_data_dir='https://cdaweb.gsfc.nasa.gov/pub/data/omni/',
    resolution='1min',
):

    file_request = _file_request(input_time_range)
    if file_times is not None: file_request['file_times'] = file_times

    # A look up dictionary containing the info of remote and local data locations.
    file_infos = dict()

    # hourly.
    id = 'cdaweb%hourly'
    base_name = 'omni2_h0_mrg1hr_%Y%m01_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,'omni_cdaweb','hourly','%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,'omni_cdaweb','hourly','%Y',base_name),
        'valid_range': smg.prepare_time_range(valid_range(id)),
    }

    # hro.
    id = 'cdaweb%hro'
    base_name = 'omni_hro_'+resolution+'_%Y%m01_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,'omni_cdaweb','hro_'+resolution,'%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,'omni_cdaweb','hro_'+resolution,'%Y',base_name),
        'valid_range': smg.prepare_time_range(valid_range(id)),
    }

    # hro2.
    id = 'cdaweb%hro2'
    base_name = 'omni_hro2_'+resolution+'_%Y%m01_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,'omni_cdaweb','hro2_'+resolution,'%Y',base_name),
        'remote_pattern': os.path.join(remote_data_dir,'omni_cdaweb','hro2_'+resolution,'%Y',base_name),
        'cadence': 'month',
        'valid_range': smg.prepare_time_range(valid_range(id)),
    }


    # Process the file request, find and download the files.
    assert input_id in file_infos.keys(), f'{input_id} not supported ...'
    file_info = file_infos[input_id]
    for key in file_info:
        file_request[key] = file_info[key]

    files = smg.prepare_files(file_request) 
    return files