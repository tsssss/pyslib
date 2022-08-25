import sys
import os
import socket
import getpass
import numpy as np
from pathlib import Path
from pyspedas.utilities.download import download
from pyspedas.utilities.time_string import time_string
from pyspedas.utilities.time_double import time_double
import libs.epoch as epoch
import constant
import libs.math as math
from libs.cdf import cdf as cdf
import slib


default_time_format = 'unix'


# Return the root directory of the current script.
def rootdir():
#    myname = sys.argv[0]
    mypath = os.path.dirname(sys.argv[0])
    return os.path.abspath(mypath)


# Return the home directory of the current logged in user.
def homedir():
    return os.path.expanduser('~')


# Return the directory of the given external disk.
def diskdir(disk):
    platform = sys.platform
    
    win = ['win32']
    unix = ['linux2','cygwin','os2','os2emx','riscos','atheos']
    mac = ['darwin']

    if platform in mac:
        dir = '/'.join(['','Volumes',disk])
    elif platform in unix:
        dir = '/'.join(['','media',disk])
    elif platform in win:
        dir = None
# doesn't work so far.
#        for letter in string.ascii_uppercase:
#            drive[letter] = os.path.exists(letter+':')
#        return '/'.join([letter,disk])
    else:
        dir = None
    
    return dir


# return [user,hostname].
def usrhost():
    usr = getpass.getuser()
    host = socket.gethostname()
    return [usr,host]


# return extension.
def get_extension(file):
    f = file
    if type(f) == list: f = file[0]
    return (os.path.splitext(f))[1]


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
                time_format = (cdfid.read_var_info(time_var))['cdftype']
            tr = epoch.convert_time(tr, input=default_time_format, output=time_format)
            times = np.empty([0])
            for file in files:
                cdfid = cdf(file)
                # Read all times and trim to the given time range.
                t = cdfid.read_var(time_var, step=step)
                index = np.where(np.logical_and(t>=tr[0], t<=tr[1]))
                if len(index) == 0: continue
                range = [np.min(index),np.max(index)]
                t = t[index]
                # Avoid overlap in time.
                if len(times)>0 :
                    if times[-1] == t[0]:
                        range[0] += 1
                        t = t[1:]
                times = np.concatenate((times,t), axis=0)
                rec_range.append(range)
            if time_format is not None:
                times = epoch.convert_time(times, input=time_format, output=default_time_format)
        else:
            for file in files:
                cdfid = cdf(file)
                var_info = cdfid.read_var_info(var)
                range = [0,var_info['maxrec']]
                rec_range.append(range)

    # Read data and setting, store in memory.
    data, data_setting = _cdf_read_var(var, files, rec_range=rec_range, step=step)
    slib.set_data(var, data, settings=data_setting)


    # Read depend_var.
    if read_depend_var is True:
        depend_vars = list()
        for key in data_setting:
            if 'depend' not in key.lower(): continue
            # Get the depend_var, data, and setting.
            depend_var = data_setting[key]
            data, data_setting = _cdf_read_var(depend_var, files, rec_range, step=step)
            # Need to avoid overwriting existing var.
            while slib.has_var(depend_var):
                # No need to update the depend_var.
                if np.array_equal(data, slib.get_data(depend_var)):
#                if data == slib.get_data(depend_var):
                    break
                else:
                    # Change to a different name and try again.
                    depend_var += '_'
            else:
                # If depend_var does not exist, then save the data and setting.
                slib.set_data(depend_var, data, settings=data_setting)
            depend_vars.append(depend_var)

            if depend_var == time_var:
                slib.set_setting(var, {'time_var':time_var})
        slib.set_setting(var, {'depend_vars':depend_vars})



def read_var(var_request):

    files = var_request.get('files', None)
    in_vars = var_request.get('in_vars', None)
    if files is None or in_vars is None:
        return None


    extension = get_extension(files[0])
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
        slib.rename(in_var, out_var)
    
    if len(out_vars) == 1: out_vars = out_vars[0]
    return out_vars


def local_data_root():
    local_data_root = diskdir('data')
    if not os.path.exists(local_data_root):
        local_data_root = os.path.join(homedir(),'data')
    return local_data_root