import os
import system.manager as smg
from mission import ml
import libs.epoch as epoch
import read.supermag
import libs.math as math
from libs.cdf import cdf
import numpy as np

local_data_root = os.path.join(ml.local_data_root,'supermag')
os.makedirs(local_data_root, exist_ok=True)
assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

valid_range = smg.prepare_time_range(['1975','2023'])

def aei(
    input_time_range,
    probe='',
    input_id='aei',
    file_times=None,
    version='v01',
    local_data_dir=local_data_root,
):

    prefix = 'sm_'
    resolution = ml.time_step
    resolution_str = str(round(resolution/60))+'min'
    base_name = prefix+input_id+'_'+resolution_str+'_%Y_'+version+'.cdf'

    local_path = os.path.join('supermag_'+resolution_str)
    file_request = {
        'time_range': smg.prepare_time_range(input_time_range),
        'cadence': 'year',
        'local_pattern': os.path.join(local_data_dir,local_path,base_name),
    }
    if file_times is not None: file_request['file_times'] = file_times

    files = smg.prepare_files(file_request)

    # Generate non-exist files.
    nonexist_files = file_request['nonexist_files']
    new_files = list()
    for file in nonexist_files:
        file_times = file_request['file_times']
        local_files = file_request['local_files']
        index = local_files.index(file)
        flag = gen_file(file_times[index], file, input_id)
        if flag is True:
            new_files.append(file)
    for file in new_files:
        files.append(file)
        nonexist_files.remove(file)
    files.sort()
    nonexist_files.sort()
    file_request['files'] = files
    file_request['nonexist_files'] = nonexist_files


    return files


def gen_file(file_time, file, input_id):


    try:
        cdfid = cdf(file)
    except:
        return False

    year_str = epoch.convert_time(file_time, input='unix', output='%Y')
    time_range = epoch.convert_time([year_str,str(int(year_str)+1)], input='%Y', output='unix')
    time_step = ml.time_step
#    common_times = math.make_bins(time_range, time_step)
    common_times = math.make_bins([time_range[0], time_range[1]-time_step], time_step)+time_step*0.5
    settings = {
        'VAR_TYPE': 'support_data',
        'UNITS': 'sec',
    }
    time_var = 'unix_time'
    cdfid.save_var(time_var, common_times, data_type='CDF_DOUBLE', settings=settings)

    for type in ['sme','smo','smu','sml']:
        func = getattr(read.supermag,type)
        var = func(time_range)
        data = np.interp(common_times, smg.get_time(var), smg.get_data(var))
        settings = {
            'VAR_TYPE': 'data',
            'UNITS': 'nT',
            'FIELDNAM': type.upper(),
            'DEPEND_0': time_var,
        }
        cdfid.save_var(type, data, data_type='CDF_FLOAT', settings=settings)

    return True
