from astropy.time import Time
from astropy.time.formats import TimeFromEpoch, erfa
from pyspedas.utilities.time_string import time_string
from pyspedas.utilities.time_double import time_double

# To convert between epoch, epoch16, tt2000, unixtime, and other time formats.
# Related references are:
# https://github.com/MAVENSDC/PyTplot/blob/master/pytplot/importers/cdf_to_tplot.py
# https://github.com/MAVENSDC/cdflib/blob/master/cdflib/epochs_astropy.py 

class SDT(TimeFromEpoch):
    name = 'sdt_unix'
    unit = 1.0 / (erfa.DAYSEC)  # Seconds
    epoch_val = '1968-05-24 00:00:00'
    epoch_val2 = None
    epoch_scale = 'utc'
    epoch_format = 'iso'


def to_time(times, message):
    """
    'time' is the astropy.time.Time object.
    'epoch','epoch16','tt2000' are CDF related times.
    'sdt_unix' or 'sdt' is used for reading data exported from SDT.
    """

    msg = message.lower()
    if msg == 'time': return times
    if msg in ['epoch','epoch16','tt2000']:
        msg = 'cdf_'+msg
    elif msg == 'cdf_double':
        msg = 'unix'
    elif msg == 'sdt':
        msg = 'sdt_unix'

    try:
        _times = Time(times, format=msg)
    except:
        # To handle other string formats.
        _times = Time(time_double(times), format='unix')

    return _times
        

def from_time(times, message):

    msg = message.lower()
    if msg == 'time': return times
    if msg in ['epoch','epoch16','tt2000']:
        msg = 'cdf_'+msg
    elif msg == 'cdf_double':
        msg = 'unix'
    elif msg == 'sdt':
        msg = 'sdt_unix'
    
    try:
        times.format = msg
        return times.value
    except:
        times.format = 'unix'
        return time_string(times.value, fmt=message)
        

    

def convert_time(
    times=None,
    input=None,
    output=None,
):
    if times is None: return None

    try:
        return from_time(to_time(times, input), output)
    except:
        return from_time(to_time(list(times), input), output)