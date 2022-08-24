from astropy.time import Time
from astropy.time.formats import TimeFromEpoch, erfa

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

    if message == 'time': return times
    if message in ['epoch','epoch16','tt2000']:
        msg = 'cdf_'+message
    elif message == 'sdt':
        msg = 'sdt_unix'
    else:
        msg = message
    _times = Time(times, format=msg)

    return _times
        

def from_time(times, message):

    if message == 'time': return times
    if message in ['epoch','epoch16','tt2000']:
        msg = 'cdf_'+message
    elif message == 'sdt':
        msg = 'sdt_unix'
    else:
        msg = message
    times.format = msg
    
    return times.value

    

def convert_time(
    times,
    input=None,
    output=None,
):
    return from_time(to_time(times, input), output)