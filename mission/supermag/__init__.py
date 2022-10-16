import os
import system.manager as smg
import libs.system as system
from datetime import datetime
import libs.epoch
from libs.cdf import cdf
import mission.supermag.supermag_api as sm_api
from system.constant import secofday
import numpy as np


# Default settings.
local_data_root = os.path.join(system.diskdir('data'),'sdata','supermag')
if not os.path.exists(local_data_root):
    try:
        os.mkdir(local_data_root)
    except:
        raise Exception(f'{local_data_root} does not exist ...')

assert os.path.isdir(local_data_root), f'{local_data_root} is not a directory ...'

def _file_request(
    input_time_range,
):

    file_request = dict()
    file_request['time_range'] = smg.prepare_time_range(input_time_range)
    file_request['cadence'] = 'day'

    return file_request


def valid_range(id, probe=None):

    now = datetime.now().strftime('%Y-%m-%d') 

    return ['1975',now]


def load_file(
    input_time_range,
    input_id='aei',
    version='v01',
    file_times=None,
    local_data_dir=local_data_root,
    remote_data_dir=None,
):

    file_request = _file_request(input_time_range)
    if file_times is not None: file_request['file_times'] = file_times


    # A look up dictionary containing the info of remote and local data locations.
    file_infos = dict()

    # The Supermag auroral electrojet index: sme, smu, sml, smo.
    id = 'aei'
    base_name = 'sm_'+id+'_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,id,'%Y',base_name),
        'valid_range': smg.prepare_time_range(valid_range(id)),
    }

    # THe Supermag auroral electrojet regional: sme lt, smu lt, sml lt.
    id = 'aei_regional'
    base_name = 'sm_'+id+'_%Y%m%d_'+version+'.cdf'
    file_infos[id] = {
        'local_pattern': os.path.join(local_data_dir,id,'%Y',base_name),
        'valid_range': smg.prepare_time_range(valid_range(id)),
    }


    # Process the file request, find and download the files.
    assert input_id in file_infos.keys(), f'{input_id} not supported ...'
    file_info = file_infos[input_id]
    for key in file_info:
        file_request[key] = file_info[key]

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


def gen_file(file_time, file, input_id='aei'):

    return globals()['gen_file_for_'+input_id](file_time, file)




def gen_file_for_aei(file_time, file):

    vars = ['sme','smu','sml']
    start_time = libs.epoch.convert_time(file_time, input='unix', output='%Y-%m-%dT%H:%M')
    try:
        flag, df = sm_api.SuperMAGGetIndices(logon='shengtian', start=start_time, extent=secofday, flagstring=','.join(vars))
        if flag != 1:
            return False
    except:
        return False

    # Write data to CDF.
    try:
        cdfid = cdf(file)

        time_var = 'unix_time'
        settings = {
            'VAR_TYPE': 'support_data',
            'UNITS': 'sec',
        }
        cdfid.save_var(time_var, df['tval'].values, data_type='CDF_DOUBLE', settings=settings)

        for var in vars:
            settings = {
                'VAR_TYPE': 'data',
                'UNITS': 'nT',
                'FIELDNAM': var.upper(),
                'DEPEND_0': time_var,
            }
            data = np.float32(df[var.upper()].values)
            data[data>=9999] = np.nan
            cdfid.save_var(var, data, data_type='CDF_FLOAT', settings=settings)


        return True
    except:
        return False

    
