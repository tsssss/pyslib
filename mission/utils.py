import os.path
import sys
import socket
import getpass
from pyspedas.utilities.download import download
from pyspedas.utilities.time_string import time_string
from pyspedas.utilities.time_double import time_double
import itertools
import numpy as np
from pathlib import Path
from pytplot import cdf_to_tplot, tplot_rename

def mkarthm(a, b, c, mode):
    """
    mode='x0', a=x0, b=dx, c=n
    mode='x1', a=x1, b=dx, c=n
    mode='dx', a=x0, b=x1, c=dx
    mode='n' , a=x0, b=x1, c=n
    :param x0: the first element
    :param x1: the last element
    :param dx: the step between elements
    :param n: the number of element
    :return: a list of array

    print(utils.mkarthm(0,1,9, 'x0'))
    print(utils.mkarthm(0,-1,9, 'x1'))
    print(utils.mkarthm(0,10,1,'dx'))
    print(utils.mkarthm(0,10,5,'n'))
    """

    assert mode in ['x0','x1','dx','n']

    if mode == 'x0':
        return a+b*np.arange(c)
    elif mode == 'x1':
        return a-b*np.flip(np.arange(c))
    elif mode == 'dx':
        ns = (b-a)/c
        if ns-np.floor(ns) >= 0.9: ns = np.round(ns)
        else: ns = np.floor(ns)
        ns += 1
        return a+c*np.arange(ns)
    else:
        dx = (b-a)/(c-1)
        return a+dx*np.arange(c)


def sort_uniq(seq):
    """
    Return a sorted and uniq list of the input list.
    :param seq: input list.
    :return: output list.
    """
    return (x[0] for x in itertools.groupby(sorted(seq)))


def prepare_time_range(input_time_range):
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

    secofday = 86400.
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

    times = mkarthm(t0, t1, ntime+1, 'n')
    if format is not None:
        str_times = time_string(times, fmt=format)
        times = time_double(sort_uniq(str_times))

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
    local_file = download(remote_file=base, remote_path=remote_dir,
        local_path=local_dir, last_version=True, verify=True)
    if len(local_file) == 0:
        return ''
    else:
        return local_file[0]



def prepare_files(request):

    # Default return values.
    files = []
    request['nonexist_files'] = []

    # Cadence. By default there is one file per day.
    key = 'cadence'
    if not key in request:
        request[key] = 'day'
    cadence = request[key]

    # time_range. By default is a pair of unix timestamps.
    key = 'time_range'
    if key not in request: request[key] = None
    time_range = request[key]

    # valid_range. By default is a pair of unix timestamps.
    key = 'valid_range'
    if key not in request: request[key] = None
    valid_range = request[key]

    # validated_time_range. By default is time_range.
    validated_time_range = validate_time_range(time_range, valid_range)


    # file_times. This is used to replace pattern to actual file names.
    key = 'file_times'
    if not key in request:
        request[key] = None
    if request[key] is None:
        # Need to get file_times from time_range.
        file_times = break_down_times(validated_time_range, cadence)
        request[key] = file_times
    file_times = request[key]


    # local_pattern. This is used to be replaced by file_times to get local_file.
    key = 'local_pattern'
    if not key in request:
        request[key] = None

    # remote_pattern. This is used to be replaced by file_times to get remote_file.
    key = 'remote_pattern'
    if not key in request:
        request[key] = None


    # local_files. This is the main output we want.
    key = 'local_files'
    if not key in request:
        request[key] = []
    local_files = request[key]
    if len(local_files) == 0:
        local_pattern = request['local_pattern']
        if not (local_pattern is None or file_times is None):
            local_files = time_string(file_times, fmt=local_pattern)
            request[key] = local_files
    
    # remote_files. This is the optional info for syncing local_files.
    key = 'remote_files'
    if not key in request:
        request[key] = []
    remote_files = request[key]
    if len(remote_files) == 0:
        remote_pattern = request['remote_pattern']
        if not (remote_pattern is None or file_times is None):
            remote_files = time_string(file_times, fmt=remote_pattern)
            request[key] = remote_files


    # Check if local files exist.
    out_files = []
    for local_file in local_files:
        path = os.path.dirname(local_file)
        base = os.path.basename(local_file)
        files = []
        for file in Path(path).glob(base):files.append(str(file))
        if len(files) == 1:
            out_files.append(files[0])
        elif len(files) > 1:
            files = sorted(files)
            out_files.append(files[-1])
    if len(out_files) == len(local_files):
        request['local_files'] = out_files
        return out_files


    # Sync with the server.
    out_files = []
    for remote_file, local_file in zip(remote_files,local_files):
        out_files.append(download_file(remote_file,local_file))
    local_files = out_files

    # Check if local files exist again.
    out_files = []
    nonexist_files = []
    for local_file in local_files:
        if os.path.exists(local_file):
            out_files.append(local_file)
        else:
            nonexist_files.append(local_file)
    if len(out_files) == 0:
        request['local_files'] = out_files
        request['nonexist_files'] = nonexist_files
    return out_files

# Return the root directory of the current script.
def rootdir():
    myname = sys.argv[0]
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


def read_var(var_request):
    files = var_request['local_files']
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
    
    return out_vars



