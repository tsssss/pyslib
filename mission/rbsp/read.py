import imp
from mission import rbsp, utils
import pyspedas
import pytplot
from libs import vector


# Orbit.
def orbit(
    time_range,
    probe,
    coord='gsm',
):

    r_gse_var = _orbit(time_range, probe, vars='r_gse')
    coord = coord.lower()
    prefix = 'rbsp'+probe+'_'
    r_coord_var = prefix+'r_'+coord
    if coord != 'gse':
        pyspedas.cotrans(r_gse_var, r_coord_var, coord_in='gse', coord_out=coord)

    return r_coord_var

def mlt(time_range, probe,):
    return _orbit(time_range, probe, vars='mlt')

def lshell(time_range, probe,):
    return _orbit(time_range, probe, vars='lshell')

def mlat(time_range, probe,):
    return _orbit(time_range, probe, vars='mlat')

def dis(time_range, probe,):
    r_gse_var = _orbit(time_range, probe, vars='r_gse')
    time, r_gse = pytplot.get_data(r_gse_var)
    prefix = 'rbsp'+probe+'_'
    dis_var = prefix+'dis'
    pytplot.store_data(dis_var,
        data={'x':time,'y':vector.magnitude(r_gse)})


def _orbit(
    time_range,
    probe,
    vars=None,
):

    assert probe in ['a','b']
    id = 'cleaned_orbit'
    files = rbsp.ssc.load_file(time_range, probe, id)
    prefix = 'rbsp'+probe+'_'
    var_request = {
        'files': files,
        'in_vars': [prefix+vars],
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

