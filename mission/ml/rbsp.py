import os
import system.manager as smg
from mission import ml
from mission import rbsp

local_data_root = os.path.join(ml.local_data_root,'rbsp')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

all_probes = rbsp.all_probes
valid_range = smg.prepare_time_range(['2012','2020'])


def orbit_var(
    input_time_range,
    probe='a',
    id='',
    file_times=None,
    version='v01',
    local_data_dir=local_data_root,
):

    # Check inputs.
    assert probe in all_probes
    rbspx = 'rbsp'+probe
    prefix = 'rbsp'+probe+'_'

    file_request = rbsp.file_request(input_time_range, probe)
    if file_times is not None: file_request['file_times'] = file_times

    # A look up dictionary containing the info of remote and local data locations.
    resolution = ml.time_step
    resolution_str = str(round(resolution/60))+'min'
    base_name = prefix+'orbit_var_'+resolution_str+'_%Y_'+version+'.cdf'
    local_path = os.path.join('orbit_var_'+resolution_str,rbspx)
    file_info = {
        'cadence': 'year',
        'valid_range': valid_range,
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
    }

    for key in file_info:
        file_request[key] = file_info[key]

    return smg.prepare_files(file_request)



def hope_en_spec(
    input_time_range,
    probe='a',
    id='',
    file_times=None,
    version='v01',
    local_data_dir=local_data_root,
):


    # Check inputs.
    assert probe in all_probes
    rbspx = 'rbsp'+probe
    prefix = 'rbsp'+probe+'_'

    file_request = rbsp.file_request(input_time_range, probe)
    if file_times is not None: file_request['file_times'] = file_times

    # A look up dictionary containing the info of remote and local data locations.
    resolution = ml.time_step
    resolution_str = str(round(resolution/60))+'min'
    base_name = prefix+'hope_en_spec_'+resolution_str+'_%Y_'+version+'.cdf'
    local_path = os.path.join('hope_en_spec_'+resolution_str,rbspx)
    file_info = {
        'cadence': 'year',
        'valid_range': valid_range,
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
    }

    for key in file_info:
        file_request[key] = file_info[key]

    return smg.prepare_files(file_request)