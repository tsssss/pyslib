import sys
import os
import socket
import getpass


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