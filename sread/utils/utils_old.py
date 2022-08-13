import sys
import os
import socket
import getpass
import requests
import email.utils as eut
import time
import datetime
import numpy as np
import datatype


#---Plotting variable.
class sgVar(object):
    def __init__(self):
        pass


#---Utilities.

# Prepare file names to be passed in getfile.
# Replace patterns with given times.
def prepfile(utr0, pattern, dt=86400.):

    if type(utr0) == datatype.ut:
        utr0 = utr0.ut()
    if len(utr0) == 1:
        utr1 = utr0+[0,dt]
    elif len(utr0) == 2:
        utr1 = utr0
    else:
        raise SyntaxError

    # remove remainder to fit dt.
    utr1 = utr1-np.remainder(utr1, dt)
    if utr1[1] == utr1[0]: utr1[1] += dt

    # break down time range
    nfile = np.floor((utr1[1]-utr1[0])/dt)
    uts = np.linspace(utr1[0], utr1[1], num=nfile, endpoint=False)

    # replace pattern with times.
    ffns = []
    for tut in uts:
        t0 = datetime.datetime.utcfromtimestamp(tut)
        ffns.append(t0.strftime(pattern))

    # uniq file.
    ffns = sorted(list(set(ffns)))

    return ffns


# Prepare a local file to be read.
# If there's no URL given or no internet connection: return local file name if it exists.
# Otherwise, download the remote file if the local file doesn't exist,
# or the remote file is newer or larger in file size.
# Set check_remote to True if the file is still updating. Otherwise, the code is satisfied
# when a local file is found.
def getfile(locffn, rempath='', check_remote=False):
    locdir = os.path.dirname(locffn)
    basefn = os.path.basename(locffn)
    locexist = os.path.exists(locffn)

    # check local only.
    if rempath == '':
        print('Remote path is missing, returning with local search results ...')
        if locexist:
            print('Local file exists: '+locffn)
            return locffn
        else:
            print('Local file does not exist: '+locffn)
            return None

    # if doesn't check_remote, then return local file if it exists.
    if check_remote == False:
        print('check_remote is False, returning with local search results ...')
        if locexist:
            print('Local file exists: '+locffn)
            return locffn
        else:
            print('Local file does not exist: '+locffn)

    # test remote connection.
    try:
        response = requests.head(rempath)
        print('Remote path exists: '+rempath)
        remffn = rempath+'/'+basefn
        response = requests.head(remffn)
        try:
            remfsize = response.headers['Content-Length']
            remmtime = response.headers['Last-Modified']
            # convert from string to local time.
            remfsize = int(remfsize)
            remmtime = time.mktime(eut.parsedate(remmtime))
            print('Remote file exists: '+remffn)
            download = False
            if locexist:
                # decide download or not.
                locmtime = os.path.getmtime(locffn)
                locfsize = os.path.getsize(locffn)
                if locfsize != remfsize:
                    print('Remote file is different in file size ...')
                    download = True
                if locmtime-remmtime < 0:
                    print('Remote file is newer ...')
                    download = True
                if download == False:
                    print('Local file is up to date, skip downloading ...')
            else:
                print('Local file does not exist: '+locffn)
                download = True

            if download:
                print('Downloading remote file ...')
                if not os.path.exists(locdir):
                    try:
                        os.makedirs(locdir)
                    except:
                        print('Fail to create local directory: '+locdir)
                        return None
                buffsize = 1024
                r = requests.get(remffn, stream=True)
                with open(locffn, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=buffsize):
                        if chunk:
                            f.write(chunk)
                # fix mtime.
                os.utime(locffn, (remmtime,remmtime))
            return locffn
        except:
            print('Remote file does not exist: '+remffn+', returning with local search results ...')
            if locexist:
                return locffn
            else:
                return None
    except: # no remote connection, return local search results.
        print('Remote path does not exist: '+rempath+', returning with local search results ...')
        if locexist:
            return locffn
        else:
            return None




# Return the parent directory of the given directory.
def parentdir(dir, nlevel=1):
    pdir = os.path.dirname(dir)
    if nlevel == 1:
        return pdir
    else:
        return parentdir(pdir, nlevel=nlevel-1)


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
        return '/'.join(['','Volumes',disk])
    elif platform in unix:
        return '/'.join(['','media',disk])
    elif platform in win:
        pass
# doesn't work so far.
#        for letter in string.ascii_uppercase:
#            drive[letter] = os.path.exists(letter+':')
#        return '/'.join([letter,disk])
    else:
        return None


# return [user,hostname].
def usrhost():
    usr = getpass.getuser()
    host = socket.gethostname()
    return [usr,host]






#---Constants
DATA_ROOT_DIR = diskdir('Research')+'/data'
# DATA_ROOT_DIR = homedir()+'/data'
# if not os.path.exists(DATA_ROOT_DIR):
#     os.makedirs(DATA_ROOT_DIR)
