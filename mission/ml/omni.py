import os
import system.manager as smg
from mission import ml

local_data_root = os.path.join(ml.local_data_root,'omni')
assert os.path.exists(local_data_root), f'{local_data_root} does not exist ...'
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

valid_range = smg.prepare_time_range(['1981','2023'])

def param(
    input_time_range,
    probe='',
    id='',
    file_times=None,
    version='v01',
    local_data_dir=local_data_root,
):

    prefix = 'omni_'

    resolution = ml.time_step
    resolution_str = str(round(resolution/60))+'min'
    base_name = prefix+'param_'+resolution_str+'_%Y_'+version+'.cdf'

    local_path = os.path.join('omni_param_'+resolution_str)
    file_request = {
        'time_range': smg.prepare_time_range(input_time_range),
        'cadence': 'year',
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
    }
    if file_times is not None: file_request['file_times'] = file_times

    return smg.prepare_files(file_request)