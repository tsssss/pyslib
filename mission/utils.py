import os.path
from pyspedas.utilities.download import download
from pyspedas.utilities.time_string import time_string
from pyspedas.utilities.time_double import time_double
from pathlib import Path
from pytplot import cdf_to_tplot, tplot_rename
import constant
import libs.math as math


def prepare_time_range(input_time_range):
    if input_time_range is None: return None
    time_range = input_time_range.copy()
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


def download_file(remote_file, local_file):
    """
    Download one file from a given URL to local disk.
    :param remote_file:
    :param local_file:
    :return:
    """
    remote_dir = os.path.dirname(remote_file)+'/'
    local_dir = os.path.dirname(local_file)+'/'
    base = os.path.basename(remote_file)
    # verify=False to skip SSL/TLS certificate, which may stop downloading a file.
    try:
        local_file = download(remote_file=base, remote_path=remote_dir, local_path=local_dir, last_version=True, verify=True)
    except:
        local_file = download(remote_file=base, remote_path=remote_dir, local_path=local_dir, last_version=True, verify=False)
    if len(local_file) == 0: return None
    return local_file[0]

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
            local_files = time_string(file_times, fmt=local_pattern)


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
            remote_files = time_string(file_times, fmt=remote_pattern)


    # Sync with the server.
    downloaded_files = []
    for remote_file, local_file in zip(remote_files,local_files):
        downloaded_files.append(download_file(remote_file,local_file))

    # Check if local files exist again.
    exist_files, nonexist_files = check_file_existence(downloaded_files)
    request['files'] = exist_files
    if len(nonexist_files) != 0:
        request['nonexist_files'] = nonexist_files
    return exist_files


def read_var(var_request):

    files = var_request['files']
    in_vars = var_request['in_vars']
    vars = cdf_to_tplot(files, varnames=in_vars)

    key = 'out_vars'
    if key not in var_request:
        var_request[key] = []
    out_vars = var_request[key]
    if len(out_vars) != len(in_vars): out_vars = in_vars
    if out_vars != vars:
        for var, out_var in zip(vars,out_vars):
            tplot_rename(var, out_var)
    
    if len(out_vars) == 1: out_vars = out_vars[0]
    return out_vars
