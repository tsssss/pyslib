import sys
import os
import socket
import getpass
from pathlib import Path
from pyspedas.utilities.download import download
from pyspedas.utilities.time_string import time_string
import slib.manager as sm




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
        time_range = sm.prepare_time_range(request.get('time_range', None))

        # valid_range. By default is a pair of unix timestamps.
        valid_range = sm.prepare_time_range(request.get('valid_range', None))

        # validated_time_range. By default is time_range.
        validated_time_range = sm.validate_time_range(time_range, valid_range)

        file_times = sm.break_down_times(validated_time_range, cadence)


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




def local_data_root():
    local_data_root = diskdir('data')
    if not os.path.exists(local_data_root):
        local_data_root = os.path.join(homedir(),'data')
    return local_data_root