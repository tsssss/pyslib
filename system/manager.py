# from collections import OrderedDict
import os
import xarray as xr
import numpy as np
from libs.cdf import cdf as cdf
import numpy as np
import libs.epoch as epoch
from pyspedas.utilities.time_string import time_string
from pyspedas.utilities.time_double import time_double
import system.constant as constant
import libs.math as math
from pathlib import Path
import libs.system as system
from libs.cotran import cotran as lib_cotran



# To store data in memory.
data_quants = dict()

def set_data(var, data, settings):
    data_quants[var] = xr.DataArray(data)
    data_quants[var].name = var
    data_quants[var].attrs = settings

def set_setting(var, settings):
    data_quants[var].attrs.update(settings)

def get_data(var):
    return data_quants[var].values

def get_setting(var, key=None):
    settings = data_quants[var].attrs
    if key is None: return settings
    else: return settings.get(key, None)

def get_time(var):
    return get_data(get_time_var(var))

def get_time_var(var):
    return data_quants[var].attrs.get('time_var', None)

def get_depend_vars(var):
    return data_quants[var].attrs.get('depend_vars', None)

def rename(var, out_var=None):
    if out_var is None: return
    data_quants[out_var] = data_quants.pop(var)

def has_var(var):
    return var in data_quants.keys()

def save(var, filename=None):
    if filename is None: return


def merge(in_vars, output=None, time_var=None, settings=None):

    if output is None:
        return None
    
    data = list()
    for var in in_vars:
        data.append(get_data(var))

    try:
        data = np.array(data)
    except:
        # data are not in the same dimensions.
        if time_var is None:
            time_var = get_time_var(in_vars[0])
            times = get_time(in_vars[0])

            for var, i in zip(in_vars,range(len(in_vars))):
                if i == 0: continue
                data[i] = np.interp(times, data[i], get_time(var))
            data = np.array(data)
    
    if len(data) == 0: return
    if settings is None:
        settings = get_setting(in_vars[0])
        settings['display'] = 'vector'
    set_data(output, data, settings)


        

def _cdf_read_var(
    var='',
    files=[],
    rec_range=None,
    step=1,
):

    cdfid = cdf(files[0])
    data_info = cdfid.read_var_info(var)
    data_setting = cdfid.read_setting(var)
    var_dim = data_info['dims']
    dim = [0]
    if len(var_dim) == 1 and var_dim[0] == 0:
        pass
    else:
        dim.extend(var_dim)


    # Read data.
    data = np.empty(dim)
    for range, file in zip(rec_range,files):
        cdfid = cdf(file)
        data = np.concatenate((data,cdfid.read_var(var, range, step)), axis=0)

    return data, data_setting


def cdf_read_var(
    var,
    files,
    rec_range=None,
    step=1,
    time_range=None,
    time_var=None,
    time_format=None,
    read_depend_var=True,
):

    # Prepare time range.
    if time_range is None:
        tr = None
    else:
        tr = prepare_time_range(time_range)
    
    # Prepare files.
    if rec_range is None:
        rec_range = list()

        # Use time to get range.
        if time_var is not None:
            if time_format is None:
                cdfid = cdf(files[0])
                time_format = (cdfid.read_var_info(time_var))['cdf_type']
            tr = epoch.convert_time(tr, input=default_time_format, output=time_format)
            pre_times = None
            for file in files:
                cdfid = cdf(file)
                # Read all times and trim to the given time range.
                t = cdfid.read_var(time_var)
                index = (np.where(np.logical_and(t>=tr[0], t<=tr[1])))[0]
                if len(index) == 0: continue
                range = [np.min(index),np.max(index)]
                t = t[index]
                # Avoid overlap in time.
                if pre_times is not None:
                    index = (np.where(t>pre_times[-1]))[0]
                    range[0] += index[0]
                    t = t[index[0]:]
                pre_times = t
                rec_range.append(range)
        else:
            for file in files:
                cdfid = cdf(file)
                var_info = cdfid.read_var_info(var)
                range = [0,var_info['maxrec']]
                rec_range.append(range)

    # Read data and setting, store in memory.
    data, data_setting = _cdf_read_var(var, files, rec_range=rec_range, step=step)
    set_data(var, data, settings=data_setting)


    # Read depend_var.
    if read_depend_var is True:
        depend_vars = list()
        for key in data_setting:
            if 'depend' not in key.lower(): continue
            # Get the depend_var, data, and setting.
            depend_var = data_setting[key]
            data, data_setting = _cdf_read_var(depend_var, files, rec_range, step=step)
            if depend_var == time_var:
                data = epoch.convert_time(data, input=time_format, output=default_time_format)
            # Need to avoid overwriting existing var.
            while has_var(depend_var):
                # No need to update the depend_var.
                if np.array_equal(data, get_data(depend_var)):
                    break
                else:
                    # Change to a different name and try again.
                    depend_var += '_'
            else:
                # If depend_var does not exist, then save the data and setting.
                set_data(depend_var, data, settings=data_setting)
            depend_vars.append(depend_var)

            if depend_var == time_var:
                set_setting(var, {'time_var':time_var})
        set_setting(var, {'depend_vars':depend_vars})



def read_var(var_request):

    files = var_request.get('files', None)
    in_vars = var_request.get('in_vars', None)
    if files is None or in_vars is None:
        return None


    extension = (os.path.splitext(files[0]))[1]
    step = int(var_request.get('step', 1))
    time_var = var_request.get('time_var', None)
    time_range = var_request.get('time_range', None)
    if step < 1: step = 1
    for var in in_vars:
        if extension == '.cdf':
            cdf_read_var(var, files, time_range=time_range, time_var=time_var, step=step)

    out_vars = var_request.get('out_vars', [])
    if len(out_vars) != len(in_vars): out_vars = in_vars
    for in_var, out_var in zip(in_vars,out_vars):
        rename(in_var, out_var)
    
    if len(out_vars) == 1: out_vars = out_vars[0]
    return out_vars


def check_file_existence(files):
    exist_files = []
    nonexist_files = []
    for file in files:
        path = os.path.dirname(file)
        base = os.path.basename(file)
        f = [str(file) for file in Path(path).glob(base)]
        try:
            file = (sorted(f))[-1]
            exist_files.append(file)
        except:
            nonexist_files.append(file)
    return exist_files, nonexist_files



def prepare_files(request):
    """
    Return files that are verified to exist on local disks for an input time range and file patterns or more complicated requests.
    """


    # file_times. This is used to replace pattern to actual file names.
    file_times = request.get('file_times', None)
    if file_times is None:
        # Need to get file_times from time_range.

        # Cadence. By default there is one file per day.
        cadence = request.get('cadence', 'day')

        # time_range. By default is a pair of unix timestamps.
        time_range = prepare_time_range(request.get('time_range', None))

        # valid_range. By default is a pair of unix timestamps.
        valid_range = prepare_time_range(request.get('valid_range', None))

        # validated_time_range. By default is time_range.
        validated_time_range = validate_time_range(time_range, valid_range)

        file_times = break_down_times(validated_time_range, cadence)


    # local_files. This is the main output we want.
    local_files = request.get('local_files', [])
    if len(local_files) == 0:
        # local_pattern. This is used to be replaced by file_times to get local_file.
        local_pattern = request.get('local_pattern', None)
        if not (local_pattern is None or file_times is None):
            local_files = epoch.convert_time(file_times, input='unix', output=local_pattern)


    # Check if local files exist.
    exist_files, nonexist_files = check_file_existence(local_files)
    if len(nonexist_files) == 0:
        request['files'] = exist_files
        return exist_files

    
    # remote_files. This is the optional info for syncing local_files.
    remote_files = request.get('remote_files', [])
    if len(remote_files) == 0:
        # remote_pattern. This is used to be replaced by file_times to get remote_file.
        remote_pattern = request.get('remote_pattern', None)
        if not (remote_pattern is None or file_times is None):
            remote_files = epoch.convert_time(file_times, input='unix', output=remote_pattern)


    # Sync with the server.
    downloaded_files = []
    for remote_file, local_file in zip(remote_files,local_files):
        downloaded_files.append(system.download_file(remote_file,local_file))

    # Check if local files exist again.
    exist_files, nonexist_files = check_file_existence(downloaded_files)
    request['files'] = exist_files
    if len(nonexist_files) != 0:
        request['nonexist_files'] = nonexist_files
    return exist_files




def local_data_root():
    local_data_root = system.diskdir('data')
    if not os.path.exists(local_data_root):
        local_data_root = os.path.join(system.homedir(),'data')
    return local_data_root




default_time_format = 'unix'

def prepare_time_range(input_time_range):
    if input_time_range is None: return None
    time_range = input_time_range.copy()
    # TODO: Consider to use convert_time and default_time_format.
    if type(time_range[0]) is str: time_range = time_double(time_range)
    time_range = sorted(time_range)
    return time_range


def validate_time_range(input_time_range, vr):
    if vr is None: return input_time_range

    tr = input_time_range.copy()
    if tr[0] < vr[0]: tr[0] = vr[0]
    if tr[1] > vr[1]: tr[1] = vr[1]
    return tr


def break_down_times(time, cadence='day'):
    """
    Return a list of times for a given time or time range and cadence.
    :param time: a time or time range.
    :param cadence: a string or number to specify the cadence.
    :return: a list of times in unix time.
    """

    # Check input, make sure it's a list.
    if time is None: return None

    if type(time) is list:
        time_range = time
    else:
        time_range = list(time)

    if len(time_range) == 1:
        return time_range
    if type(time_range[0]) is str: time_range = time_double(time_range)

    secofday = constant.secofday
    if type(cadence) is str:
        if cadence == 'year':
            format = '%Y'
            dt = secofday
        elif cadence == 'month':
            format = '%Y-%m'
            dt = secofday
        elif cadence == 'day':
            format = '%Y-%m-%d'
            dt = secofday
        elif cadence == 'hour':
            format = '%Y-%m-%d/%H'
            dt = 3600.
        elif cadence == 'minute':
            format = '%Y-%m-%d/%H:%M'
            dt = 60.
        elif cadence == 'second':
            format = '%Y-%m-%d/%H:%M:%S'
            dt = 1.
        else:
            raise ValueError('Unkown cadence.')
    else:
        format = None
        dt = cadence
        if dt < 1: format = '%Y-%m-%d/%H:%M:%S.%f'

    # Calculate the proper start and end times.
    t0 = time_range[0]
    t1 = time_range[1]
    t0 = t0-(t0 % dt)
    t1 = t1-(t1 % dt)
    if t1 == time_range[1]: t1 -= dt
    if t1 < t0: t1 = t0

    ntime = (t1-t0)/dt
    if ntime == 0: return [t0]

    times = math.mkarthm(t0, t1, ntime+1, 'n')
    if format is not None:
        str_times = time_string(times, fmt=format)
        times = time_double(math.sort_uniq(str_times))

    return times


def cotran(in_var, out_var=None, coord_in=None, coord_out=None, probe=None):
    
    if coord_in is None:
        coord_in = get_setting(in_var, 'coord')
    if coord_out is None:
        raise Exception('No output coord ..')
    
    vec_in = get_data(in_var)
    times = get_time(in_var)
    setting = get_setting(in_var)
    setting['coord'] = coord_out

    vec_out = lib_cotran(list(vec_in), list(times),
        input=coord_in, output=coord_out, probe=probe)
    
    if out_var is None:
        out_var = in_var.replace(coord_in, coord_out)
    set_data(out_var, vec_out, settings=setting)

