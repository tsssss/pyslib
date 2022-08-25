# from collections import OrderedDict
import xarray as xr
import numpy as np

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
    time_var = data_quants[var].attrs.get('time_var', None)
    return get_data(time_var)

def rename(var, out_var=None):
    if out_var is None: return
    data_quants[out_var] = data_quants.pop(var)

def save(var, filename=None):
    if filename is None: return


def merge(in_vars, output=None, depend_on=None):
    if output is None:
        return None
    
    ndim = len(in_vars)
    if depend_on is None: depend_on = in_vars[0]
    try: depend_var = in_vars[depend_on]
    except: depend_var = depend_on
    xx, _ = get_data(depend_on)
    ntime = len(xx)
    yy = np.empty((ntime,ndim))