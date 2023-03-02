from mission import rbsp
from libs import vector
import pytplot
import system.manager as smg


# Orbit.
def orbit(
    time_range,
    probe,
    resolution,
    coord='gsm',
    get_name=False,
):

    if get_name: return _orbit(time_range, probe, vars='r_gse', resolution=resolution, get_name=True)

    r_gse_var = _orbit(time_range, probe, vars='r_gse', resolution=resolution)
    coord = coord.lower()
    settings = {
        'display_type': 'vector',
        'coord': 'gse',
        'short_name': 'R',
        'coord_labels': list('xyz'),
    }
    smg.set_setting(r_gse_var, settings)

    prefix = 'rbsp'+probe+'_'
    r_coord_var = prefix+'r_'+coord
    if coord != 'gse':
        smg.cotran(r_gse_var, r_coord_var, coord_in='gse', coord_out=coord)

    return r_coord_var

def mlt(time_range, probe, resolution, get_name=False):
    if get_name: return _orbit(time_range, probe, vars='mlt', resolution=resolution, get_name=True)
    return _orbit(time_range, probe, vars='mlt', resolution=resolution)

def lshell(time_range, probe, resolution, get_name=False):
    if get_name: return _orbit(time_range, probe, vars='lshell', get_name=True)
    return _orbit(time_range, probe, vars='lshell', resolution=resolution)

def mlat(time_range, probe, resolution, get_name=False):
    if get_name: return _orbit(time_range, probe, vars='mlat', get_name=True)
    return _orbit(time_range, probe, vars='mlat', resolution=resolution)

def dis(time_range, probe, resolution, get_name=False):
    if get_name: return _orbit(time_range, probe, vars='r_gse', get_name=True)

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
    get_name=False,
):

    assert probe in rbsp.all_probes
    prefix = 'rbsp'+probe+'_'
    in_var = prefix+vars
    out_var = in_var
    if get_name: return out_var

    id = 'cleaned_orbit'
    native_resolution = 1
    step = int(resolution/native_resolution)
    files = rbsp.ssc.load_file(time_range, probe, id)
    var_request = {
        'files': files,
        'in_vars': [in_var],
        'out_vars': [out_var],
        'time_range': time_range,
        'time_var': 'Epoch',
        'step': step,
    }
    return smg.read_var(var_request)






# Quaternion.
def q_uvw2gse(
    time_range,
    probe,
    get_name=False,
):

    assert probe in rbsp.all_probes
    prefix = 'rbsp'+probe+'_'
    q_var = prefix+'q_uvw2gse'
    if get_name is True: return q_var

    id = 'spice'
    files = rbsp.efw.load_file(time_range, probe, id)
    var_request = {
        'files': files,
        'in_vars': [q_var],
    }
    return smg.read_var(var_request)



# Hope.
def hope_omni_flux(
    time_range,
    probe,
    species,
    get_name=False,
):

    assert probe in rbsp.all_probes
    assert species in rbsp.hope.species
    the_var = 'f'+species+'do'
    prefix = 'rbsp'+probe+'_'
    out_var = prefix+'hope_'+the_var
    if get_name is True: return out_var

    id = 'l3%pa'
    var_request = {
        'files': rbsp.hope.load_file(time_range, probe, id),
        'in_vars': [the_var.upper()],
        'out_vars': [out_var],
    }
    return smg.read_var(var_request)


def hope_l2_flux(
    time_range,
    probe,
    species,
    get_name=False,
):

    assert probe in rbsp.all_probes
    assert species in rbsp.hope.species
    the_var = 'f'+species+'du'
    prefix = 'rbsp'+probe+'_'
    out_var = prefix+'hope_l2_'+the_var
    if get_name is True: return out_var

    if species == 'e': suffix = '_Ele'
    else: suffix = '_Ion'
    energy_var = 'HOPE_ENERGY'+suffix
    epoch_delta_var = 'Epoch'+suffix+'_DELTA'

    id = 'l2%sector'
    files = rbsp.hope.load_file(time_range, probe, id)
    var_request = {
        'files': files,
        'in_vars': [the_var.upper(),energy_var,epoch_delta_var],
        'out_vars': [out_var,out_var+'_energy',out_var+'_epoch_delta'],
    }
    out_vars = smg.read_var(var_request)
    smg.set_setting(out_var, {'energy':out_vars[1], 'epoch_delta':out_vars[2]})
    return out_var


# EMFISIS.

def bfield(
    time_range,
    probe,
    resolution='4sec',
    coord='gsm',
    get_name=False,
):
    assert probe in rbsp.all_probes

    prefix = 'rbsp'+probe+'_'
    out_var = prefix+'b_'+coord
    if get_name: return out_var


    all_resolutions = ['hires','1sec','4sec']
    assert resolution in all_resolutions

    id = 'l3%magnetometer'
    files = rbsp


