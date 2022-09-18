import sys
import os
import socket
import getpass
from pyspedas.utilities.download import download




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