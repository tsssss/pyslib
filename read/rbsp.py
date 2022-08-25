from mission import rbsp
import pyspedas
import pytplot
from libs import vector
from pyslib import utils


# Orbit.
def orbit(
    time_range,
    probe,
    resolution,
    coord='gsm',
):

    r_gse_var = _orbit(time_range, probe, vars='r_gse', resolution=resolution)
    coord = coord.lower()
    prefix = 'rbsp'+probe+'_'
    r_coord_var = prefix+'r_'+coord
    if coord != 'gse':
        pyspedas.cotrans(r_gse_var, r_coord_var, coord_in='gse', coord_out=coord)

    return r_coord_var

def mlt(time_range, probe, resolution):
    return _orbit(time_range, probe, vars='mlt', resolution=resolution)

def lshell(time_range, probe, resolution):
    return _orbit(time_range, probe, vars='lshell', resolution=resolution)

def mlat(time_range, probe, resolution):
    return _orbit(time_range, probe, vars='mlat', resolution=resolution)

def dis(time_range, probe, resolution):
    r_gse_var = _orbit(time_range, probe, vars='r_gse', resolution=resolution)
    time, r_gse = pytplot.get_data(r_gse_var)
    prefix = 'rbsp'+probe+'_'
    dis_var = prefix+'dis'
    pytplot.store_data(dis_var,
        data={'x':time,'y':vector.magnitude(r_gse)})


def _orbit(
    time_range,
    probe,
    vars=None,
    resolution=60,
):

    assert probe in ['a','b']
    id = 'cleaned_orbit'
    native_resolution = 1
    step = int(resolution/native_resolution)
    files = rbsp.ssc.load_file(time_range, probe, id)
    prefix = 'rbsp'+probe+'_'
    var_request = {
        'files': files,
        'in_vars': [prefix+vars],
        'time_range': time_range,
        'time_var': 'Epoch',
        'step': step,
    }
    return utils.read_var(var_request)






# Quaternion.
def q_uvw2gse(
    time_range,
    probe,
):

    id = 'spice'
    files = rbsp.efw.load_file(time_range, probe, id)
    prefix = 'rbsp'+probe+'_'
    q_var = prefix+'q_uvw2gse'
    var_request = {
        'files': files,
        'in_vars': [q_var],
    }
    return utils.read_var(var_request)



# Hope.
def hope_omni_flux(
    time_range,
    probe,
    species,
):

    assert species in rbsp.hope.species
    the_var = 'f'+species+'do'
    prefix = 'rbsp'+probe+'_'

    id = 'l3%pa'
    var_request = {
        'files': rbsp.hope.load_file(time_range, probe, id),
        'in_vars': [the_var.upper()],
        'out_vars': [prefix+'hope_'+the_var],
    }
    return utils.read_var(var_request)

